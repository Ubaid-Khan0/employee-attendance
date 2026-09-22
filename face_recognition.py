import os
import cv2
import numpy as np
from deepface import DeepFace


KNOWN_FACES_DIR = "known_faces"

MODEL_NAME = "Facenet"
DETECTOR_BACKEND = "opencv"

# Lower value = stricter matching
FACE_DISTANCE_THRESHOLD = 0.40


def cosine_distance(vector1, vector2):
    vector1 = np.asarray(vector1, dtype=np.float32)
    vector2 = np.asarray(vector2, dtype=np.float32)

    denominator = (
        np.linalg.norm(vector1) *
        np.linalg.norm(vector2)
    )

    if denominator == 0:
        return 1.0

    similarity = np.dot(
        vector1,
        vector2
    ) / denominator

    return 1.0 - similarity


def get_face_embedding(face_image):
    try:
        result = DeepFace.represent(
            img_path=face_image,
            model_name=MODEL_NAME,
            detector_backend="skip",
            enforce_detection=False
        )

        if not result:
            return None

        return np.array(
            result[0]["embedding"],
            dtype=np.float32
        )

    except Exception:
        return None


def extract_face(image):
    try:
        faces = DeepFace.extract_faces(
            img_path=image,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=False,
            align=True
        )

        valid_faces = []

        for face_data in faces:

            facial_area = face_data.get(
                "facial_area",
                {}
            )

            width = facial_area.get("w", 0)
            height = facial_area.get("h", 0)

            if width > 0 and height > 0:

                valid_faces.append(
                    face_data
                )

        if not valid_faces:
            return None, None

        # If multiple faces exist,
        # use the largest face.
        largest_face = max(
            valid_faces,
            key=lambda item:
                item["facial_area"]["w"] *
                item["facial_area"]["h"]
        )

        face = largest_face["face"]

        # DeepFace normally returns the
        # extracted face normalized between 0 and 1.
        if face.max() <= 1.0:
            face = (
                face * 255
            ).astype(np.uint8)
        else:
            face = face.astype(np.uint8)

        facial_area = largest_face[
            "facial_area"
        ]

        return face, facial_area

    except Exception:
        return None, None


def load_face_database():
    face_database = []

    if not os.path.exists(KNOWN_FACES_DIR):
        os.makedirs(
            KNOWN_FACES_DIR,
            exist_ok=True
        )

        return face_database

    for employee_name in os.listdir(
        KNOWN_FACES_DIR
    ):

        employee_folder = os.path.join(
            KNOWN_FACES_DIR,
            employee_name
        )

        if not os.path.isdir(
            employee_folder
        ):
            continue

        for filename in os.listdir(
            employee_folder
        ):

            if not filename.lower().endswith(
                (".jpg", ".jpeg", ".png")
            ):
                continue

            image_path = os.path.join(
                employee_folder,
                filename
            )

            image = cv2.imread(
                image_path
            )

            if image is None:
                continue

            face, _ = extract_face(
                image
            )

            if face is None:
                continue

            embedding = get_face_embedding(
                face
            )

            if embedding is None:
                continue

            face_database.append({
                "employee_name": employee_name,
                "image_path": image_path,
                "embedding": embedding
            })

    return face_database


def recognize_face(
    frame,
    face_database
):

    if not face_database:
        return None, None, None

    face, facial_area = extract_face(
        frame
    )

    if face is None:
        return None, None, None

    current_embedding = get_face_embedding(
        face
    )

    if current_embedding is None:
        return None, None, None

    best_employee = None
    best_distance = float("inf")

    for person in face_database:

        distance = cosine_distance(
            current_embedding,
            person["embedding"]
        )

        if distance < best_distance:
            best_distance = distance
            best_employee = (
                person["employee_name"]
            )

    if (
        best_employee is not None
        and best_distance <= FACE_DISTANCE_THRESHOLD
    ):
        return (
            best_employee,
            best_distance,
            facial_area
        )

    return (
        None,
        best_distance,
        facial_area
    )