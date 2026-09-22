import sqlite3
from datetime import datetime

DATABASE_FILE = "database.db"


def get_connection():
    return sqlite3.connect(DATABASE_FILE)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Employees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_name TEXT PRIMARY KEY,
            start_time TEXT NOT NULL,
            last_allowed_time TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Attendance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT NOT NULL,
            attendance_date TEXT NOT NULL,
            check_in_time TEXT,
            check_out_time TEXT,
            status TEXT,
            late_minutes INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------------- EMPLOYEE FUNCTIONS ----------------

def add_employee(employee_name, start_time, last_allowed_time):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO employees
            (employee_name, start_time, last_allowed_time, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            employee_name,
            start_time,
            last_allowed_time,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def remove_employee(employee_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM employees WHERE employee_name = ?",
        (employee_name,)
    )

    conn.commit()
    conn.close()


def update_employee(employee_name, start_time, last_allowed_time):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE employees
        SET start_time = ?, last_allowed_time = ?
        WHERE employee_name = ?
    """, (
        start_time,
        last_allowed_time,
        employee_name
    ))

    conn.commit()
    conn.close()


def get_employee(employee_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT employee_name, start_time, last_allowed_time
        FROM employees
        WHERE employee_name = ?
    """, (employee_name,))

    employee = cursor.fetchone()

    conn.close()

    return employee


def get_all_employees():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT employee_name, start_time, last_allowed_time
        FROM employees
        ORDER BY employee_name
    """)

    employees = cursor.fetchall()

    conn.close()

    return employees


# ---------------- ATTENDANCE FUNCTIONS ----------------

def get_today_attendance(employee_name, attendance_date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, employee_name, attendance_date,
               check_in_time, check_out_time,
               status, late_minutes
        FROM attendance
        WHERE employee_name = ?
        AND attendance_date = ?
    """, (
        employee_name,
        attendance_date
    ))

    record = cursor.fetchone()

    conn.close()

    return record


def create_attendance(
    employee_name,
    attendance_date,
    check_in_time,
    status,
    late_minutes
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO attendance
        (
            employee_name,
            attendance_date,
            check_in_time,
            check_out_time,
            status,
            late_minutes,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        employee_name,
        attendance_date,
        check_in_time,
        None,
        status,
        late_minutes,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def update_check_out(
    employee_name,
    attendance_date,
    check_out_time
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE attendance
        SET check_out_time = ?
        WHERE employee_name = ?
        AND attendance_date = ?
    """, (
        check_out_time,
        employee_name,
        attendance_date
    ))

    conn.commit()
    conn.close()


def get_all_attendance():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            employee_name,
            attendance_date,
            check_in_time,
            check_out_time,
            status,
            late_minutes
        FROM attendance
        ORDER BY attendance_date DESC, employee_name
    """)

    records = cursor.fetchall()

    conn.close()

    return records


def get_employee_attendance(employee_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            employee_name,
            attendance_date,
            check_in_time,
            check_out_time,
            status,
            late_minutes
        FROM attendance
        WHERE employee_name = ?
        ORDER BY attendance_date DESC
    """, (employee_name,))

    records = cursor.fetchall()

    conn.close()

    return records


# Initialize database when this module is loaded
initialize_database()