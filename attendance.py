from datetime import datetime

from database import (
    get_employee,
    get_today_attendance,
    create_attendance,
    update_check_out
)


def calculate_late_minutes(last_allowed_time, current_time):
    allowed = datetime.strptime(
        last_allowed_time,
        "%H:%M"
    )

    actual = datetime.strptime(
        current_time,
        "%H:%M"
    )

    difference = actual - allowed

    late_minutes = int(
        difference.total_seconds() / 60
    )

    if late_minutes < 0:
        return 0

    return late_minutes


def record_entry(employee_name):
    employee = get_employee(employee_name)

    if employee is None:
        return False, "Employee not found."

    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")

    existing = get_today_attendance(
        employee_name,
        today
    )

    if existing is not None:
        return False, f"{employee_name} has already checked in today."

    last_allowed_time = employee[2]

    late_minutes = calculate_late_minutes(
        last_allowed_time,
        current_time
    )

    if late_minutes > 0:
        status = "Late"
        message = (
            f"{employee_name} checked in late.\n"
            f"Time: {current_time}\n"
            f"Late: {late_minutes} minutes"
        )
    else:
        status = "On Time"
        message = (
            f"{employee_name} checked in successfully.\n"
            f"Time: {current_time}"
        )

    create_attendance(
        employee_name,
        today,
        current_time,
        status,
        late_minutes
    )

    return True, message


def record_exit(employee_name):
    employee = get_employee(employee_name)

    if employee is None:
        return False, "Employee not found."

    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")

    existing = get_today_attendance(
        employee_name,
        today
    )

    if existing is None:
        return False, (
            f"{employee_name} has no check-in record for today."
        )

    check_out_time = existing[4]

    if check_out_time is not None:
        return False, (
            f"{employee_name} has already checked out today."
        )

    update_check_out(
        employee_name,
        today,
        current_time
    )

    return True, (
        f"{employee_name} checked out successfully.\n"
        f"Time: {current_time}"
    )