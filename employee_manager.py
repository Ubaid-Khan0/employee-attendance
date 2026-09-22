import os
import shutil

from database import (
    add_employee,
    remove_employee,
    update_employee,
    get_all_employees
)


KNOWN_FACES_DIR = "known_faces"


def create_employee_folder(employee_name):
    safe_name = employee_name.replace(" ", "_")

    folder = os.path.join(
        KNOWN_FACES_DIR,
        safe_name
    )

    os.makedirs(folder, exist_ok=True)

    return folder


def add_employee_with_images(
    employee_name,
    start_time,
    last_allowed_time,
    image_paths
):
    employee_name = employee_name.strip()

    if not employee_name:
        return False, "Employee name is required."

    if not image_paths:
        return False, "At least one face image is required."

    success = add_employee(
        employee_name,
        start_time,
        last_allowed_time
    )

    if not success:
        return False, "An employee with this name already exists."

    folder = create_employee_folder(employee_name)

    for index, image_path in enumerate(image_paths, start=1):

        extension = os.path.splitext(image_path)[1]

        destination = os.path.join(
            folder,
            f"face_{index}{extension}"
        )

        shutil.copy2(
            image_path,
            destination
        )

    return True, "Employee added successfully."


def delete_employee(employee_name):
    remove_employee(employee_name)

    folder = os.path.join(
        KNOWN_FACES_DIR,
        employee_name.replace(" ", "_")
    )

    if os.path.exists(folder):
        shutil.rmtree(folder)

    return True


def edit_employee(
    employee_name,
    start_time,
    last_allowed_time
):
    update_employee(
        employee_name,
        start_time,
        last_allowed_time
    )

    return True


def get_employee_list():
    return get_all_employees()