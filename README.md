# Employee Attendance System

A desktop-based **AI Employee Attendance System** built with Python. The system uses **face recognition, SQLite, Tkinter, OpenCV, and Excel reporting** to automatically record employee entry and exit while providing an admin interface for employee management and attendance monitoring.

---

## 🚀 Project Overview

The Employee Attendance System is designed to automate employee attendance using a camera-based face recognition system.

Instead of manually entering attendance, an employee simply looks at the camera. The system identifies the employee and automatically records:

* Employee name
* Date
* Check-in time
* Check-out time
* Attendance status
* Exact late minutes

The system also provides separate **Entry Mode** and **Exit Mode**, allowing the same camera to handle both check-in and check-out.

---

## ✨ Features

### 👤 Employee Management

The Admin can:

* Add new employees
* Edit employee information
* Remove employees
* View all registered employees
* Set employee start time
* Set employee's last allowed arrival time
* Register multiple face images for each employee

Employee face images are stored locally inside the `known_faces` directory.

Example:

```text
known_faces/
│
├── ubaid_khan/
│   ├── face_1.jpg
│   ├── face_2.jpg
│   └── face_3.jpg
│
└── asadullah/
    ├── face1.jpg
    ├── face2.jpg
    ├── face3.jpg
    └── face4.jpg
```

---

## 🤖 AI Face Recognition

The system uses:

* OpenCV
* DeepFace
* FaceNet
* OpenCV face detector
* Cosine distance-based face matching

Multiple images can be registered for each employee to improve recognition reliability.

The system automatically loads the face database when the application starts.

---

## 📷 Automatic Camera Recognition

The camera continuously captures frames and searches for registered employees.

When a recognized employee appears:

```text
Camera
   ↓
Face Detection
   ↓
Face Embedding
   ↓
Face Matching
   ↓
Employee Identified
   ↓
Attendance Recorded
```

The system does not require the employee to press a button.

---

## 🟢 Entry Mode

In **ENTRY MODE**, the system records the employee's check-in.

Example:

```text
Employee: Ubaid Khan
Time: 09:21
Allowed Until: 09:15

Status: Late
Late Minutes: 6
```

If the employee arrives before or at the allowed time:

```text
Status: On Time
Late Minutes: 0
```

---

## 🔴 Exit Mode

In **EXIT MODE**, the system records the employee's check-out time.

Example:

```text
Employee: Ubaid Khan
Check-in: 09:10
Check-out: 17:05
```

The system prevents duplicate check-outs for the same attendance record.

---

## ⏱️ Late Detection

Each employee can have an individual:

* Start Time
* Last Allowed Time

The system calculates the exact number of minutes an employee arrives after the allowed time.

Example:

```text
Last Allowed Time: 09:15
Actual Arrival:    09:27

Late Minutes: 12
```

There is no fixed maximum limit on late minutes.

---

## 🔒 Employee Cooldown

After a successful attendance action, the employee enters a **60-second cooldown period**.

This prevents the same employee from repeatedly triggering attendance while standing in front of the camera.

Example:

```text
09:00 → Entry recorded
09:00–09:59 → Cooldown
10:00 → Can trigger again
```

The cooldown is **per employee**.

Therefore, if Ubaid is in cooldown, another employee can still be recognized and processed.

---

## 🔄 Automatic Camera Reconnection

The system continuously monitors the camera.

If the camera:

* Disconnects
* Stops responding
* Fails to return a frame
* Cannot be opened

the application automatically attempts to reconnect.

```text
Camera Failure
      ↓
Release Camera
      ↓
Wait
      ↓
Reconnect
      ↓
Resume Attendance
```

This prevents the application from permanently losing camera functionality after a temporary camera failure.

---

## 🖥️ Dashboard

The dashboard provides an overview of the current attendance system.

It displays:

* Total employees
* Present employees
* Late employees
* Absent employees
* Live attendance camera
* Recognition/attendance messages
* Current attendance mode

Example:

```text
TOTAL EMPLOYEES    PRESENT TODAY
       10                 8

LATE TODAY         ABSENT TODAY
        2                 2

--------------------------------
     LIVE ATTENDANCE CAMERA
--------------------------------

          Camera Feed

--------------------------------
       Ubaid Khan
       ENTRY RECORDED
--------------------------------
```

The camera and attendance message are displayed in separate areas so the message does not appear behind the camera feed.

---

## 👨‍💼 Admin Modules

The application contains several modules.

### Dashboard

Provides the live attendance camera and daily statistics.

### Employees

Allows the administrator to:

* Add employees
* Edit employees
* Remove employees
* View employee details

### Attendance

Displays today's attendance records.

### Reports

Allows the administrator to export:

* Individual employee attendance
* Complete company attendance

---

## 📊 Attendance Database

The system uses **SQLite** as its main database.

Database file:

```text
database.db
```

The database stores employee information and attendance records.

### Employee Information

```text
Employee Name
Start Time
Last Allowed Time
Created At
```

### Attendance Information

```text
Employee Name
Date
Check-in Time
Check-out Time
Status
Late Minutes
Created At
```

The SQLite database is the permanent source of attendance records.

---

## 📁 Project Structure

```text
employee_attendance/
│
├── app.py
├── database.py
├── employee_manager.py
├── face_recognition.py
├── attendance.py
├── excel_export.py
│
├── database.db
│
├── known_faces/
│   ├── ubaid_khan/
│   │   ├── face_1.jpg
│   │   └── face_2.jpg
│   │
│   └── asadullah/
│       ├── face1.jpg
│       ├── face2.jpg
│       ├── face3.jpg
│       └── face4.jpg
│
└── employee_reports/
```

---

## 🧩 Main Python Modules

### `app.py`

Contains the main Tkinter application and user interface.

Responsible for:

* Dashboard
* Employee management UI
* Attendance UI
* Reports UI
* Camera display
* Entry/Exit modes
* Background camera management
* Recognition loop

---

### `database.py`

Handles SQLite database operations.

Responsible for:

* Creating database tables
* Adding employees
* Updating employees
* Removing employees
* Retrieving employees
* Creating attendance records
* Updating check-out records
* Retrieving attendance

---

### `employee_manager.py`

Handles employee registration and face image management.

Responsible for:

* Creating employee folders
* Saving face images
* Adding employees
* Editing employees
* Removing employees

---

### `face_recognition.py`

Handles AI face recognition.

Responsible for:

* Loading registered face images
* Generating face embeddings
* Detecting faces
* Comparing faces
* Identifying employees

---

### `attendance.py`

Handles attendance logic.

Responsible for:

* Recording entry
* Recording exit
* Calculating late minutes
* Preventing duplicate check-ins
* Preventing duplicate check-outs

---

### `excel_export.py`

Handles attendance report generation.

Responsible for creating:

* Individual employee Excel reports
* Company-wide Excel reports

---

## 📑 Excel Reports

Reports are stored inside:

```text
employee_reports/
```

An individual employee report uses the employee's name.

Example:

```text
employee_reports/
└── Ubaid_Khan.xlsx
```

The Excel report contains:

| Employee Name | Date       | Check-in Time | Check-out Time | Status | Late Minutes |
| ------------- | ---------- | ------------- | -------------- | ------ | ------------ |
| Ubaid Khan    | 2026-09-22 | 09:21         | 17:05          | Late   | 6            |

A company-wide report is also available:

```text
All_Employees_Attendance.xlsx
```

---

## 🛠️ Technologies Used

| Technology | Purpose                                 |
| ---------- | --------------------------------------- |
| Python     | Main programming language               |
| Tkinter    | Desktop GUI                             |
| OpenCV     | Camera processing                       |
| DeepFace   | Face recognition                        |
| FaceNet    | Face embeddings                         |
| SQLite     | Attendance database                     |
| Pillow     | Camera image display                    |
| openpyxl   | Excel report generation                 |
| Threading  | Background camera and recognition tasks |

---

## 📦 Installation

Clone or download the project and open the project directory.

Install the required packages:

```bash
pip install opencv-python
pip install deepface
pip install pillow
pip install openpyxl
```

Tkinter is normally included with standard Python installations on Windows.

---

## ▶️ Running the Application

Open a terminal inside the project folder:

```bash
python app.py
```

The application will:

1. Initialize the database.
2. Load registered employee faces.
3. Start the camera.
4. Start face recognition.
5. Open the attendance dashboard.

---

## 👤 Adding an Employee

From the application:

```text
Employees
    ↓
+ Add Employee
```

Enter:

```text
Employee Full Name
Start Time
Last Allowed Time
```

Then select one or more face images from the computer.

Example:

```text
Name: Asadullah
Start Time: 09:00
Last Allowed Time: 09:15
```

Select:

```text
face1.jpg
face2.jpg
face3.jpg
face4.jpg
```

Then save the employee.

---

## 📸 Recommended Face Images

For better recognition, use multiple clear images.

Recommended:

* Front-facing face
* Good lighting
* Face clearly visible
* Different small changes in angle
* No heavy blur
* No face obstruction

Example:

```text
face1.jpg → Front
face2.jpg → Slight left
face3.jpg → Slight right
face4.jpg → Different lighting
```

---

## 🔐 Attendance Workflow

### Employee Entry

```text
Employee approaches camera
          ↓
Camera captures face
          ↓
Face detected
          ↓
Face compared with database
          ↓
Employee identified
          ↓
Check-in recorded
          ↓
Late time calculated
          ↓
60-second cooldown
```

### Employee Exit

```text
Employee approaches camera
          ↓
Face recognized
          ↓
Exit mode active
          ↓
Check-out recorded
          ↓
60-second cooldown
```

---

## ⚠️ Important Notes

### Camera

The application currently attempts to use camera index:

```python
CAMERA_INDEX = 0
```

The camera manager also attempts to reconnect automatically if the camera fails.

### Face Folder Names

The employee folder name is used as the face recognition identity.

For example:

```text
known_faces/asadullah/
```

will produce:

```text
asadullah
```

The application converts underscores into spaces when matching database employee names.

Example:

```text
ubaid_khan
      ↓
ubaid khan
```

---

## 🔮 Future Improvements

Possible future improvements include:

* Admin login/authentication
* Multiple camera support
* Employee profile photos
* Search and filtering
* Monthly attendance reports
* Attendance analytics
* Cloud database synchronization
* Email notifications
* WhatsApp notifications
* Mobile application
* Advanced anti-spoofing/liveness detection
* More advanced face recognition models
* Attendance charts and analytics

---

## 🎯 Project Objective

The main objective of this project is to create an automated employee attendance solution that reduces manual attendance work and provides accurate digital attendance records.

The system combines **Artificial Intelligence, Computer Vision, Database Management, GUI Development, and Excel Reporting** into a single desktop application.

---

## 👨‍💻 Developer

**Ubaid Khan**

### Skills Demonstrated

* Python
* Artificial Intelligence
* Computer Vision
* Face Recognition
* SQLite Database Management
* Tkinter GUI Development
* OpenCV
* DeepFace
* Excel Automation
* Multithreading

---

## 📌 Project Status

**Status: Functional Prototype**

Current core functionality:

* ✅ Employee management
* ✅ Multiple face registration
* ✅ AI face recognition
* ✅ Automatic entry
* ✅ Automatic exit
* ✅ Late-minute calculation
* ✅ 60-second per-employee cooldown
* ✅ SQLite attendance storage
* ✅ Automatic camera reconnection
* ✅ Dashboard
* ✅ Attendance module
* ✅ Excel reports
* ✅ Individual employee reports
* ✅ Company-wide reports
* ✅ Separate camera and attendance message display

---

## 📄 License

This project is developed as an educational/software development project and can be modified and extended according to project requirements.
