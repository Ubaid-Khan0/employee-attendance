import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
import threading
import time
from PIL import Image, ImageTk
from datetime import datetime

from database import (
    initialize_database,
    get_all_employees,
    get_today_attendance,
)

from employee_manager import (
    add_employee_with_images,
    delete_employee,
    edit_employee,
)

from attendance import (
    record_entry,
    record_exit,
)

from excel_export import (
    create_employee_excel,
    create_company_excel,
)

from face_recognition import (
    load_face_database,
    recognize_face,
)


# ============================================================
# COLORS
# ============================================================

BG = "#0f172a"
SIDEBAR = "#111827"
CARD = "#1e293b"
CARD_LIGHT = "#334155"

TEXT = "#f8fafc"
TEXT_SECONDARY = "#94a3b8"

PRIMARY = "#2563eb"
SUCCESS = "#22c55e"
WARNING = "#f59e0b"
DANGER = "#ef4444"

ENTRY_COLOR = "#16a34a"
EXIT_COLOR = "#dc2626"


# ============================================================
# MAIN APPLICATION
# ============================================================

class AttendanceApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Employee Attendance System"
        )

        self.root.geometry(
            "1400x850"
        )

        self.root.minsize(
            1200,
            700
        )

        self.root.configure(
            bg=BG
        )

        # ----------------------------------------------------
        # DATABASE
        # ----------------------------------------------------

        initialize_database()

        # ----------------------------------------------------
        # CAMERA
        # ----------------------------------------------------

        self.camera = None
        self.camera_running = False

        self.latest_frame = None
        self.frame_lock = threading.Lock()

        # Prevent multiple camera-opening attempts
        self.camera_lock = threading.Lock()

        # ----------------------------------------------------
        # FACE DATABASE
        # ----------------------------------------------------

        self.face_database = {}

        self.recognized_name = None
        self.recognized_distance = None
        self.last_unknown_message_time = 0
        self.unknown_message_cooldown = 2

        # ----------------------------------------------------
        # ATTENDANCE MODE
        # ----------------------------------------------------

        self.mode = "ENTRY"

        # ----------------------------------------------------
        # 60 SECOND COOLDOWN PER EMPLOYEE
        #
        # Example:
        #
        # Ubaid recognized at 9:00
        # Ubaid cannot trigger again until 9:01
        #
        # Another employee can still trigger attendance.
        # ----------------------------------------------------

        self.employee_cooldowns = {}

        self.cooldown_seconds = 60

        # ----------------------------------------------------
        # UI
        # ----------------------------------------------------

        self.create_styles()
        self.create_sidebar()
        self.create_main_area()

        self.show_dashboard()

        # ----------------------------------------------------
        # LOAD FACE DATABASE
        # ----------------------------------------------------

        threading.Thread(
            target=self.load_faces_background,
            daemon=True
        ).start()

        # ----------------------------------------------------
        # CAMERA
        # ----------------------------------------------------

        self.camera_running = True

        threading.Thread(
            target=self.camera_manager_loop,
            daemon=True
        ).start()

        threading.Thread(
            target=self.recognition_loop,
            daemon=True
        ).start()

        # ----------------------------------------------------
        # WINDOW CLOSE
        # ----------------------------------------------------

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_application
        )

    # ========================================================
    # STYLES
    # ========================================================

    def create_styles(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except:
            pass

        style.configure(
            "Treeview",
            background=CARD,
            foreground=TEXT,
            fieldbackground=CARD,
            rowheight=35,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview.Heading",
            background=CARD_LIGHT,
            foreground=TEXT,
            font=("Segoe UI", 10, "bold")
        )

        style.map(
            "Treeview",
            background=[
                ("selected", PRIMARY)
            ],
            foreground=[
                ("selected", "white")
            ]
        )

    # ========================================================
    # SIDEBAR
    # ========================================================

    def create_sidebar(self):

        self.sidebar = tk.Frame(
            self.root,
            bg=SIDEBAR,
            width=240
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(
            False
        )

        tk.Label(
            self.sidebar,
            text="ATTENDANCE",
            bg=SIDEBAR,
            fg=TEXT,
            font=("Segoe UI", 20, "bold")
        ).pack(
            pady=(30, 5)
        )

        tk.Label(
            self.sidebar,
            text="Employee Management",
            bg=SIDEBAR,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 9)
        ).pack(
            pady=(0, 30)
        )

        self.create_nav_button(
            "Dashboard",
            self.show_dashboard
        )

        self.create_nav_button(
            "Employees",
            self.show_employees
        )

        self.create_nav_button(
            "Attendance",
            self.show_attendance
        )

        self.create_nav_button(
            "Reports",
            self.show_reports
        )

        # ----------------------------------------------------
        # MODE
        # ----------------------------------------------------

        tk.Label(
            self.sidebar,
            text="ATTENDANCE MODE",
            bg=SIDEBAR,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 9, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(35, 10)
        )

        self.entry_button = tk.Button(
            self.sidebar,
            text="✓  ENTRY MODE",
            command=self.set_entry_mode,
            bg=ENTRY_COLOR,
            fg="white",
            activebackground=ENTRY_COLOR,
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            cursor="hand2",
            pady=10
        )

        self.entry_button.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.exit_button = tk.Button(
            self.sidebar,
            text="→  EXIT MODE",
            command=self.set_exit_mode,
            bg=CARD_LIGHT,
            fg=TEXT,
            activebackground=EXIT_COLOR,
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            cursor="hand2",
            pady=10
        )

        self.exit_button.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.mode_label = tk.Label(
            self.sidebar,
            text="Current: ENTRY",
            bg=SIDEBAR,
            fg=SUCCESS,
            font=("Segoe UI", 10, "bold")
        )

        self.mode_label.pack(
            pady=10
        )

    # ========================================================
    # NAVIGATION BUTTON
    # ========================================================

    def create_nav_button(
        self,
        text,
        command
    ):

        button = tk.Button(
            self.sidebar,
            text=text,
            command=command,
            bg=SIDEBAR,
            fg=TEXT_SECONDARY,
            activebackground=CARD_LIGHT,
            activeforeground=TEXT,
            relief="flat",
            anchor="w",
            padx=25,
            pady=12,
            font=("Segoe UI", 11),
            cursor="hand2"
        )

        button.pack(
            fill="x",
            padx=10,
            pady=2
        )

    # ========================================================
    # MAIN AREA
    # ========================================================

    def create_main_area(self):

        self.main = tk.Frame(
            self.root,
            bg=BG
        )

        self.main.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.content = tk.Frame(
            self.main,
            bg=BG
        )

        self.content.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=20
        )

    # ========================================================
    # CLEAR PAGE
    # ========================================================

    def clear_content(self):

        for widget in self.content.winfo_children():

            widget.destroy()

        # ========================================================
    # DASHBOARD
    # ========================================================

    def show_dashboard(self):

        self.clear_content()

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = tk.Frame(
            self.content,
            bg=BG
        )

        header.pack(
            fill="x",
            pady=(0, 20)
        )

        tk.Label(
            header,
            text="Dashboard",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 25, "bold")
        ).pack(
            side="left"
        )

        tk.Label(
            header,
            text=datetime.now().strftime(
                "%A, %d %B %Y"
            ),
            bg=BG,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 11)
        ).pack(
            side="right",
            pady=10
        )

        # ----------------------------------------------------
        # STATISTICS
        # ----------------------------------------------------

        employees = get_all_employees()

        total_employees = len(
            employees
        )

        today = datetime.now().strftime(
            "%Y-%m-%d"
        )

        present = 0
        late = 0

        for employee in employees:

            attendance = get_today_attendance(
                employee[0],
                today
            )

            if attendance:

                present += 1

                if len(attendance) > 5:

                    if attendance[5] == "Late":

                        late += 1

        absent = max(
            total_employees - present,
            0
        )

        stats_frame = tk.Frame(
            self.content,
            bg=BG
        )

        stats_frame.pack(
            fill="x"
        )

        self.create_stat_card(
            stats_frame,
            "TOTAL EMPLOYEES",
            total_employees,
            PRIMARY
        )

        self.create_stat_card(
            stats_frame,
            "PRESENT TODAY",
            present,
            SUCCESS
        )

        self.create_stat_card(
            stats_frame,
            "LATE TODAY",
            late,
            WARNING
        )

        self.create_stat_card(
            stats_frame,
            "ABSENT TODAY",
            absent,
            DANGER
        )

        # ----------------------------------------------------
        # CAMERA CARD
        # ----------------------------------------------------

        camera_card = tk.Frame(
            self.content,
            bg=CARD
        )

        camera_card.pack(
            fill="both",
            expand=True,
            pady=(20, 0)
        )

        # ----------------------------------------------------
        # CAMERA TITLE
        # ----------------------------------------------------

        tk.Label(
            camera_card,
            text="Live Attendance Camera",
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 15, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 5)
        )

        # ----------------------------------------------------
        # CAMERA DISPLAY CONTAINER
        # ----------------------------------------------------

        camera_display_container = tk.Frame(
            camera_card,
            bg="black",
            height=300
        )

        camera_display_container.pack(
            fill="both",
            padx=20,
            pady=(5, 5)
        )

        camera_display_container.pack_propagate(
            False
        )

        # ----------------------------------------------------
        # ACTUAL CAMERA LABEL
        # ----------------------------------------------------

        self.camera_frame = tk.Label(
            camera_display_container,
            bg="black",
            fg=TEXT,
            text="Connecting to camera...",
            font=("Segoe UI", 14),
            anchor="center"
        )

        self.camera_frame.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # MESSAGE AREA
        # ----------------------------------------------------

        self.message_frame = tk.Frame(
            camera_card,
            bg=CARD,
            height=75
        )

        self.message_frame.pack(
            fill="x",
            padx=20,
            pady=(5, 15)
        )

        # Prevent the frame from shrinking because of the label
        self.message_frame.pack_propagate(
            False
        )

        # ----------------------------------------------------
        # ATTENDANCE RESULT MESSAGE
        # ----------------------------------------------------

        self.result_label = tk.Label(
            self.message_frame,
            text="Waiting for employee...",
            bg=CARD,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 13, "bold"),
            anchor="center",
            justify="center"
        )

        self.result_label.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # START CAMERA DISPLAY
        # ----------------------------------------------------

        self.update_camera_display()
    # ========================================================
    # STAT CARD
    # ========================================================

    def create_stat_card(
        self,
        parent,
        title,
        value,
        accent
    ):

        card = tk.Frame(
            parent,
            bg=CARD,
            height=120
        )

        card.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5
        )

        tk.Label(
            card,
            text=title,
            bg=CARD,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 9, "bold")
        ).pack(
            anchor="w",
            padx=18,
            pady=(15, 5)
        )

        tk.Label(
            card,
            text=str(value),
            bg=CARD,
            fg=accent,
            font=("Segoe UI", 28, "bold")
        ).pack(
            anchor="w",
            padx=18
        )

    # ========================================================
    # EMPLOYEES
    # ========================================================

    def show_employees(self):

        self.clear_content()

        header = tk.Frame(
            self.content,
            bg=BG
        )

        header.pack(
            fill="x",
            pady=(0, 20)
        )

        tk.Label(
            header,
            text="Employees",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 25, "bold")
        ).pack(
            side="left"
        )

        tk.Button(
            header,
            text="+ Add Employee",
            command=self.add_employee_dialog,
            bg=PRIMARY,
            fg="white",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=10,
            cursor="hand2"
        ).pack(
            side="right"
        )

        table_frame = tk.Frame(
            self.content,
            bg=CARD
        )

        table_frame.pack(
            fill="both",
            expand=True
        )

        columns = (
            "name",
            "start",
            "allowed"
        )

        self.employee_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        self.employee_tree.heading(
            "name",
            text="Employee Name"
        )

        self.employee_tree.heading(
            "start",
            text="Start Time"
        )

        self.employee_tree.heading(
            "allowed",
            text="Last Allowed Time"
        )

        self.employee_tree.column(
            "name",
            width=400
        )

        self.employee_tree.column(
            "start",
            width=250
        )

        self.employee_tree.column(
            "allowed",
            width=250
        )

        self.employee_tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        self.refresh_employee_table()

        buttons = tk.Frame(
            self.content,
            bg=BG
        )

        buttons.pack(
            fill="x",
            pady=15
        )

        tk.Button(
            buttons,
            text="Edit Selected",
            command=self.edit_selected_employee,
            bg=PRIMARY,
            fg="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=10
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            buttons,
            text="Remove Selected",
            command=self.remove_selected_employee,
            bg=DANGER,
            fg="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=10
        ).pack(
            side="left",
            padx=5
        )

    # ========================================================
    # REFRESH EMPLOYEES
    # ========================================================

    def refresh_employee_table(self):

        for item in self.employee_tree.get_children():

            self.employee_tree.delete(
                item
            )

        employees = get_all_employees()

        for employee in employees:

            self.employee_tree.insert(
                "",
                "end",
                values=(
                    employee[0],
                    employee[1],
                    employee[2]
                )
            )

    # ========================================================
    # ADD EMPLOYEE
    # ========================================================

    def add_employee_dialog(self):

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "Add Employee"
        )

        window.geometry(
            "550x600"
        )

        window.configure(
            bg=BG
        )

        window.transient(
            self.root
        )

        window.grab_set()

        tk.Label(
            window,
            text="Add Employee",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 20, "bold")
        ).pack(
            pady=25
        )

        # Name

        tk.Label(
            window,
            text="Employee Full Name",
            bg=BG,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=40
        )

        name_entry = tk.Entry(
            window,
            bg=CARD,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 12)
        )

        name_entry.pack(
            fill="x",
            padx=40,
            pady=(5, 20),
            ipady=8
        )

        # Start

        tk.Label(
            window,
            text="Start Time (HH:MM)",
            bg=BG,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=40
        )

        start_entry = tk.Entry(
            window,
            bg=CARD,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 12)
        )

        start_entry.insert(
            0,
            "09:00"
        )

        start_entry.pack(
            fill="x",
            padx=40,
            pady=(5, 20),
            ipady=8
        )

        # Allowed

        tk.Label(
            window,
            text="Last Allowed Time (HH:MM)",
            bg=BG,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=40
        )

        allowed_entry = tk.Entry(
            window,
            bg=CARD,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 12)
        )

        allowed_entry.insert(
            0,
            "09:15"
        )

        allowed_entry.pack(
            fill="x",
            padx=40,
            pady=(5, 20),
            ipady=8
        )

        selected_images = []

        image_label = tk.Label(
            window,
            text="No images selected",
            bg=BG,
            fg=TEXT_SECONDARY
        )

        image_label.pack(
            pady=10
        )

        def select_images():

            files = filedialog.askopenfilenames(
                title="Select Employee Face Images",
                filetypes=[
                    (
                        "Image Files",
                        "*.jpg *.jpeg *.png"
                    )
                ]
            )

            if files:

                selected_images.clear()

                selected_images.extend(
                    files
                )

                image_label.config(
                    text=f"{len(files)} image(s) selected",
                    fg=SUCCESS
                )

        tk.Button(
            window,
            text="Select Face Images",
            command=select_images,
            bg=CARD_LIGHT,
            fg=TEXT,
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=10
        ).pack(
            pady=10
        )

        def save_employee():

            name = name_entry.get().strip()
            start = start_entry.get().strip()
            allowed = allowed_entry.get().strip()

            if not name:

                messagebox.showerror(
                    "Error",
                    "Please enter employee name.",
                    parent=window
                )

                return

            if not selected_images:

                messagebox.showerror(
                    "Error",
                    "Please select at least one face image.",
                    parent=window
                )

                return

            try:

                success, message = add_employee_with_images(
                    name,
                    start,
                    allowed,
                    selected_images
                )

            except Exception as e:

                success = False
                message = str(e)

            if success:

                messagebox.showinfo(
                    "Success",
                    message,
                    parent=window
                )

                threading.Thread(
                    target=self.load_faces_background,
                    daemon=True
                ).start()

                window.destroy()

                self.show_employees()

            else:

                messagebox.showerror(
                    "Error",
                    message,
                    parent=window
                )

        tk.Button(
            window,
            text="Save Employee",
            command=save_employee,
            bg=SUCCESS,
            fg="white",
            relief="flat",
            font=("Segoe UI", 12, "bold"),
            padx=30,
            pady=12
        ).pack(
            pady=25
        )

    # ========================================================
    # EDIT EMPLOYEE
    # ========================================================

    def edit_selected_employee(self):

        selected = self.employee_tree.selection()

        if not selected:

            messagebox.showwarning(
                "Select Employee",
                "Please select an employee first."
            )

            return

        values = self.employee_tree.item(
            selected[0],
            "values"
        )

        old_name = values[0]
        old_start = values[1]
        old_allowed = values[2]

        window = tk.Toplevel(
            self.root
        )

        window.title(
            "Edit Employee"
        )

        window.geometry(
            "500x450"
        )

        window.configure(
            bg=BG
        )

        window.transient(
            self.root
        )

        window.grab_set()

        tk.Label(
            window,
            text="Edit Employee",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 20, "bold")
        ).pack(
            pady=25
        )

        tk.Label(
            window,
            text="Employee Full Name",
            bg=BG,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=40
        )

        name_entry = tk.Entry(
            window,
            bg=CARD,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 12)
        )

        name_entry.insert(
            0,
            old_name
        )

        name_entry.pack(
            fill="x",
            padx=40,
            pady=8,
            ipady=8
        )

        tk.Label(
            window,
            text="Start Time",
            bg=BG,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=40
        )

        start_entry = tk.Entry(
            window,
            bg=CARD,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 12)
        )

        start_entry.insert(
            0,
            old_start
        )

        start_entry.pack(
            fill="x",
            padx=40,
            pady=8,
            ipady=8
        )

        tk.Label(
            window,
            text="Last Allowed Time",
            bg=BG,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=40
        )

        allowed_entry = tk.Entry(
            window,
            bg=CARD,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 12)
        )

        allowed_entry.insert(
            0,
            old_allowed
        )

        allowed_entry.pack(
            fill="x",
            padx=40,
            pady=8,
            ipady=8
        )

        def save_changes():

            new_name = name_entry.get().strip()
            new_start = start_entry.get().strip()
            new_allowed = allowed_entry.get().strip()

            if not new_name:

                messagebox.showerror(
                    "Error",
                    "Employee name cannot be empty.",
                    parent=window
                )

                return

            try:

                success, message = edit_employee(
                    old_name,
                    new_name,
                    new_start,
                    new_allowed
                )

            except Exception as e:

                success = False
                message = str(e)

            if success:

                messagebox.showinfo(
                    "Success",
                    message,
                    parent=window
                )

                threading.Thread(
                    target=self.load_faces_background,
                    daemon=True
                ).start()

                window.destroy()

                self.show_employees()

            else:

                messagebox.showerror(
                    "Error",
                    message,
                    parent=window
                )

        tk.Button(
            window,
            text="Save Changes",
            command=save_changes,
            bg=PRIMARY,
            fg="white",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            padx=30,
            pady=10
        ).pack(
            pady=25
        )

    # ========================================================
    # REMOVE EMPLOYEE
    # ========================================================

    def remove_selected_employee(self):

        selected = self.employee_tree.selection()

        if not selected:

            messagebox.showwarning(
                "Select Employee",
                "Please select an employee first."
            )

            return

        values = self.employee_tree.item(
            selected[0],
            "values"
        )

        name = values[0]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Remove employee '{name}'?"
        )

        if not confirm:
            return

        try:

            success, message = delete_employee(
                name
            )

        except Exception as e:

            success = False
            message = str(e)

        if success:

            # Remove cooldown
            self.employee_cooldowns.pop(
                name,
                None
            )

            messagebox.showinfo(
                "Removed",
                message
            )

            threading.Thread(
                target=self.load_faces_background,
                daemon=True
            ).start()

            self.show_employees()

        else:

            messagebox.showerror(
                "Error",
                message
            )

    # ========================================================
    # ATTENDANCE PAGE
    # ========================================================

    def show_attendance(self):

        self.clear_content()

        tk.Label(
            self.content,
            text="Today's Attendance",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 25, "bold")
        ).pack(
            anchor="w",
            pady=(0, 20)
        )

        frame = tk.Frame(
            self.content,
            bg=CARD
        )

        frame.pack(
            fill="both",
            expand=True
        )

        columns = (
            "name",
            "date",
            "checkin",
            "checkout",
            "status",
            "late"
        )

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "name": "Employee Name",
            "date": "Date",
            "checkin": "Check-in",
            "checkout": "Check-out",
            "status": "Status",
            "late": "Late Minutes"
        }

        widths = {
            "name": 250,
            "date": 130,
            "checkin": 130,
            "checkout": 130,
            "status": 130,
            "late": 120
        }

        for column in columns:

            tree.heading(
                column,
                text=headings[column]
            )

            tree.column(
                column,
                width=widths[column]
            )

        tree.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        employees = get_all_employees()

        today = datetime.now().strftime(
            "%Y-%m-%d"
        )

        for employee in employees:

            attendance = get_today_attendance(
                employee[0],
                today
            )

            if attendance:

                tree.insert(
                    "",
                    "end",
                    values=(
                        attendance[1],
                        attendance[2],
                        attendance[3] or "-",
                        attendance[4] or "-",
                        attendance[5] or "-",
                        attendance[6]
                        if len(attendance) > 6
                        else 0
                    )
                )

    # ========================================================
    # REPORTS
    # ========================================================

    def show_reports(self):

        self.clear_content()

        tk.Label(
            self.content,
            text="Reports",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 25, "bold")
        ).pack(
            anchor="w",
            pady=(0, 25)
        )

        card = tk.Frame(
            self.content,
            bg=CARD
        )

        card.pack(
            fill="x",
            padx=10
        )

        tk.Label(
            card,
            text="Export Attendance Reports",
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 16, "bold")
        ).pack(
            pady=(25, 10)
        )

        tk.Label(
            card,
            text="Generate Excel files containing employee attendance records.",
            bg=CARD,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 10)
        ).pack(
            pady=5
        )

        tk.Button(
            card,
            text="Export All Employees",
            command=self.export_company_report,
            bg=PRIMARY,
            fg="white",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            padx=30,
            pady=12
        ).pack(
            pady=20
        )

        employees = get_all_employees()

        tk.Label(
            card,
            text="Individual Employee",
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 12, "bold")
        ).pack(
            pady=(20, 5)
        )

        employee_names = [
            employee[0]
            for employee in employees
        ]

        self.report_employee_var = tk.StringVar()

        combo = ttk.Combobox(
            card,
            textvariable=self.report_employee_var,
            values=employee_names,
            state="readonly",
            width=35
        )

        combo.pack(
            pady=10
        )

        tk.Button(
            card,
            text="Export Selected Employee",
            command=self.export_employee_report,
            bg=SUCCESS,
            fg="white",
            relief="flat",
            font=("Segoe UI", 11, "bold"),
            padx=25,
            pady=10
        ).pack(
            pady=(5, 30)
        )

    # ========================================================
    # EXPORT COMPANY
    # ========================================================

    def export_company_report(self):

        try:

            path = create_company_excel()

            messagebox.showinfo(
                "Export Complete",
                f"Company attendance report created:\n\n{path}"
            )

        except Exception as e:

            messagebox.showerror(
                "Export Error",
                str(e)
            )

    # ========================================================
    # EXPORT EMPLOYEE
    # ========================================================

    def export_employee_report(self):

        name = self.report_employee_var.get()

        if not name:

            messagebox.showwarning(
                "Select Employee",
                "Please select an employee."
            )

            return

        try:

            path = create_employee_excel(
                name
            )

            messagebox.showinfo(
                "Export Complete",
                f"Employee report created:\n\n{path}"
            )

        except Exception as e:

            messagebox.showerror(
                "Export Error",
                str(e)
            )

    # ========================================================
    # ENTRY MODE
    # ========================================================

    def set_entry_mode(self):

        self.mode = "ENTRY"

        self.entry_button.config(
            bg=ENTRY_COLOR,
            fg="white"
        )

        self.exit_button.config(
            bg=CARD_LIGHT,
            fg=TEXT
        )

        self.mode_label.config(
            text="Current: ENTRY",
            fg=SUCCESS
        )

        if hasattr(
            self,
            "result_label"
        ):

            self.result_label.config(
                text="ENTRY MODE — Look at the camera",
                fg=SUCCESS
            )

    # ========================================================
    # EXIT MODE
    # ========================================================

    def set_exit_mode(self):

        self.mode = "EXIT"

        self.entry_button.config(
            bg=CARD_LIGHT,
            fg=TEXT
        )

        self.exit_button.config(
            bg=EXIT_COLOR,
            fg="white"
        )

        self.mode_label.config(
            text="Current: EXIT",
            fg=DANGER
        )

        if hasattr(
            self,
            "result_label"
        ):

            self.result_label.config(
                text="EXIT MODE — Look at the camera",
                fg=DANGER
            )

    # ========================================================
    # LOAD FACE DATABASE
    # ========================================================

    def load_faces_background(self):

        try:

            database = load_face_database()

            self.face_database = database

            print(
                f"Face database loaded: {len(database)} employees"
            )

        except Exception as e:

            print(
                "Face database error:",
                e
            )

    # ========================================================
    # CAMERA MANAGER
    #
    # This keeps checking the camera.
    #
    # If camera disconnects:
    #
    #     release camera
    #     wait
    #     reconnect
    #
    # So the application does not permanently lose
    # the camera.
    # ========================================================

    def camera_manager_loop(self):

        while self.camera_running:

            try:

                # ------------------------------------------------
                # Open camera if it is not available
                # ------------------------------------------------

                if self.camera is None:

                    self.connect_camera()

                    time.sleep(1)

                    continue

                # ------------------------------------------------
                # Check if camera is opened
                # ------------------------------------------------

                if not self.camera.isOpened():

                    self.disconnect_camera()

                    time.sleep(2)

                    continue

                # ------------------------------------------------
                # Read frame
                # ------------------------------------------------

                success, frame = self.camera.read()

                if not success:

                    print(
                        "Camera frame failed. Reconnecting..."
                    )

                    self.disconnect_camera()

                    time.sleep(2)

                    continue

                # ------------------------------------------------
                # Save latest frame
                # ------------------------------------------------

                with self.frame_lock:

                    self.latest_frame = frame.copy()

                time.sleep(
                    0.01
                )

            except Exception as e:

                print(
                    "Camera error:",
                    e
                )

                self.disconnect_camera()

                time.sleep(2)

    # ========================================================
    # CONNECT CAMERA
    # ========================================================

    def connect_camera(self):

        with self.camera_lock:

            try:

                print(
                    "Connecting to camera..."
                )

                # Windows camera backend
                camera = cv2.VideoCapture(
                    0,
                    cv2.CAP_DSHOW
                )

                if not camera.isOpened():

                    print(
                        "CAP_DSHOW failed. Trying default backend..."
                    )

                    camera.release()

                    camera = cv2.VideoCapture(
                        0
                    )

                if camera.isOpened():

                    # Resolution
                    camera.set(
                        cv2.CAP_PROP_FRAME_WIDTH,
                        1280
                    )

                    camera.set(
                        cv2.CAP_PROP_FRAME_HEIGHT,
                        720
                    )

                    # FPS
                    camera.set(
                        cv2.CAP_PROP_FPS,
                        30
                    )

                    self.camera = camera

                    print(
                        "Camera connected successfully."
                    )

                    self.root.after(
                        0,
                        self.camera_status,
                        "Camera Connected",
                        SUCCESS
                    )

                else:

                    print(
                        "Camera could not be opened."
                    )

                    self.camera = None

                    self.root.after(
                        0,
                        self.camera_status,
                        "Camera unavailable - reconnecting...",
                        WARNING
                    )

            except Exception as e:

                print(
                    "Camera connection error:",
                    e
                )

                self.camera = None

    # ========================================================
    # DISCONNECT CAMERA
    # ========================================================

    def disconnect_camera(self):

        with self.camera_lock:

            if self.camera is not None:

                try:

                    self.camera.release()

                except:
                    pass

                self.camera = None

        with self.frame_lock:

            self.latest_frame = None

        self.root.after(
            0,
            self.camera_status,
            "Camera disconnected - reconnecting...",
            WARNING
        )

    # ========================================================
    # CAMERA STATUS
    # ========================================================

       # ========================================================
    # CAMERA STATUS
    # ========================================================

    def camera_status(
        self,
        message,
        color
    ):

        if hasattr(
            self,
            "camera_frame"
        ):

            with self.frame_lock:

                has_frame = (
                    self.latest_frame
                    is not None
                )

            if not has_frame:

                self.camera_frame.config(
                    image="",
                    text=message,
                    fg=color
                )

    # ========================================================
    # FACE RECOGNITION LOOP
    # ========================================================

    def recognition_loop(self):

        while self.camera_running:

            with self.frame_lock:

                if self.latest_frame is None:

                    time.sleep(
                        0.2
                    )

                    continue

                frame = self.latest_frame.copy()

            # ------------------------------------------------
            # Face database not loaded yet
            # ------------------------------------------------

            if not self.face_database:

                time.sleep(
                    0.5
                )

                continue

            try:

                name, distance, face_area = recognize_face(
                    frame,
                    self.face_database
                )

                # ------------------------------------------------
                # No face recognized
                # ------------------------------------------------

                if name is None:

                    self.recognized_name = None
                    self.recognized_distance = None

                    if face_area is not None:

                        current_time = time.time()

                        if (
                            current_time -
                            self.last_unknown_message_time
                            >= self.unknown_message_cooldown
                        ):

                            self.last_unknown_message_time = current_time

                            self.root.after(
                                0,
                                self.show_unknown_message
                            )

                    time.sleep(
                        0.15
                    )

                    continue

                # ------------------------------------------------
                # Convert folder name to database name
                #
                # ubaid_khan
                #       ↓
                # ubaid khan
                # ------------------------------------------------

                employee_name = name.replace(
                    "_",
                    " "
                ).strip()

                self.recognized_name = employee_name
                self.recognized_distance = distance

                print(
                    f"Recognized: {employee_name} | "
                    f"Distance: {distance:.4f}"
                )

                # ------------------------------------------------
                # CHECK EMPLOYEE COOLDOWN
                # ------------------------------------------------

                current_time = time.time()

                last_time = self.employee_cooldowns.get(
                    employee_name,
                    0
                )

                elapsed = (
                    current_time - last_time
                )

                # ------------------------------------------------
                # Employee is still cooling down
                # ------------------------------------------------

                if elapsed < self.cooldown_seconds:

                    remaining = int(
                        self.cooldown_seconds - elapsed
                    )

                    self.root.after(
                        0,
                        self.show_cooldown_message,
                        employee_name,
                        remaining
                    )

                    time.sleep(
                        0.5
                    )

                    continue

                # ------------------------------------------------
                # Employee is allowed to trigger attendance
                # ------------------------------------------------

                if self.mode == "ENTRY":

                    success, message = record_entry(
                        employee_name
                    )

                else:

                    success, message = record_exit(
                        employee_name
                    )

                # ------------------------------------------------
                # IMPORTANT:
                #
                # Start cooldown ONLY after a successful
                # attendance action.
                #
                # This means if ENTRY fails because of a
                # database problem, the employee can retry.
                # ------------------------------------------------

                if success:

                    self.employee_cooldowns[
                        employee_name
                    ] = current_time

                # ------------------------------------------------
                # Update GUI
                # ------------------------------------------------

                self.root.after(
                    0,
                    self.show_attendance_result,
                    success,
                    message,
                    employee_name
                )

            except Exception as e:

                print(
                    "Recognition error:",
                    e
                )

            time.sleep(
                0.2
            )

    # ========================================================
    # UNKNOWN FACE MESSAGE
    # ========================================================

    def show_unknown_message(self):

        if not hasattr(
            self,
            "result_label"
        ):

            return

        self.result_label.config(
            text="Not Recognized\nUnknown Person",
            fg=WARNING
        )

    # ========================================================
    # COOLDOWN MESSAGE
    # ========================================================

    def show_cooldown_message(
        self,
        employee_name,
        remaining
    ):

        if not hasattr(
            self,
            "result_label"
        ):

            return

        self.result_label.config(
            text=(
                f"✓ {employee_name}\n"
                f"Already processed — "
                f"cooldown: {remaining}s"
            ),
            fg=TEXT_SECONDARY
        )

    # ========================================================
    # ATTENDANCE RESULT
    # ========================================================

    def show_attendance_result(
        self,
        success,
        message,
        employee_name
    ):

        if not hasattr(
            self,
            "result_label"
        ):

            return

        if success:

            if self.mode == "ENTRY":

                self.result_label.config(
                    text=(
                        f"✓ {employee_name}\n"
                        f"ENTRY RECORDED\n"
                        f"{message}"
                    ),
                    fg=SUCCESS
                )

            else:

                self.result_label.config(
                    text=(
                        f"✓ {employee_name}\n"
                        f"EXIT RECORDED\n"
                        f"{message}"
                    ),
                    fg=SUCCESS
                )

        else:

            self.result_label.config(
                text=(
                    f"⚠ {employee_name}\n"
                    f"{message}"
                ),
                fg=WARNING
            )

    # ========================================================
    # CAMERA DISPLAY
    # ========================================================

        # ========================================================
    # CAMERA DISPLAY
    # ========================================================

    def update_camera_display(self):

        if not self.camera_running:
            return

        if hasattr(self, "camera_frame"):

            with self.frame_lock:

                if self.latest_frame is not None:
                    frame = self.latest_frame.copy()
                else:
                    frame = None

            if frame is not None:

                try:

                    # ----------------------------------------
                    # BGR -> RGB
                    # ----------------------------------------

                    frame = cv2.cvtColor(
                        frame,
                        cv2.COLOR_BGR2RGB
                    )

                    # ----------------------------------------
                    # Get camera display size
                    # ----------------------------------------

                    width = self.camera_frame.winfo_width()
                    height = self.camera_frame.winfo_height()

                    if width < 100:
                        width = 900

                    if height < 100:
                        height = 450

                    # ----------------------------------------
                    # Maintain aspect ratio
                    # ----------------------------------------

                    h, w = frame.shape[:2]

                    scale = min(
                        width / w,
                        height / h
                    )

                    new_width = max(
                        int(w * scale),
                        1
                    )

                    new_height = max(
                        int(h * scale),
                        1
                    )

                    frame = cv2.resize(
                        frame,
                        (
                            new_width,
                            new_height
                        ),
                        interpolation=cv2.INTER_AREA
                    )

                    # ----------------------------------------
                    # Convert to PIL
                    # ----------------------------------------

                    image = Image.fromarray(
                        frame
                    )

                    photo = ImageTk.PhotoImage(
                        image=image
                    )

                    # ----------------------------------------
                    # Display ONLY inside camera_frame
                    # ----------------------------------------

                    self.camera_frame.config(
                        image=photo,
                        text=""
                    )

                    self.camera_frame.image = photo

                except Exception as e:

                    print(
                        "Display error:",
                        e
                    )

        # ----------------------------------------------------
        # Keep refreshing
        # ----------------------------------------------------

        self.root.after(
            30,
            self.update_camera_display
        )

    # ========================================================
    # CLOSE APPLICATION
    # ========================================================

    def close_application(self):

        print(
            "Closing application..."
        )

        self.camera_running = False

        # ----------------------------------------------------
        # Release camera
        # ----------------------------------------------------

        with self.camera_lock:

            if self.camera is not None:

                try:

                    self.camera.release()

                except:
                    pass

                self.camera = None

        # ----------------------------------------------------
        # Destroy GUI
        # ----------------------------------------------------

        self.root.destroy()


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = AttendanceApp(
        root
    )

    root.mainloop()

