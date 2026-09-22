import cv2
from face_recognition import load_face_database, recognize_face

print("Loading registered faces...")
face_database = load_face_database()

print(f"Loaded {len(face_database)} face images.")
print("Starting camera...")
print("Look at the camera. Press Q to quit.")

camera = cv2.VideoCapture(0)

while True:
    ret, frame = camera.read()

    if not ret:
        print("Could not read camera.")
        break

    name, distance, face_area = recognize_face(frame, face_database)

    if name:
        text = f"{name} | Distance: {distance:.3f}"
        print(text, end="\r")
    else:
        text = "Not recognized"

    cv2.putText(
        frame,
        text,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 0) if name else (0, 0, 255),
        2
    )

    cv2.imshow("Face Recognition Test", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()