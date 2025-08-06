import cv2
import mediapipe as mp
import numpy as np
import os


def eyes_closed(image_path, eye_threshold):
    image = cv2.imread(image_path)
    if image is None:
        return False

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Load Haar cascade for face detection
    face_cascade = cv2.CascadeClassifier("models/haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    if len(faces) == 0:
        print(f"{os.path.basename(image_path)} → No face detected")
        return False

    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(static_image_mode=True) as face_mesh:
        for (x, y, w, h) in faces:
            face_img = image[y:y+h, x:x+w]  # Crop the face

            results = face_mesh.process(cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB))
            if not results.multi_face_landmarks:
                continue  # Skip if MediaPipe doesn't find landmarks in this face

            for face_landmarks in results.multi_face_landmarks:
                left_eye_ids = [33, 160, 158, 133, 153, 144]
                right_eye_ids = [263, 387, 385, 362, 380, 373]

                def eye_aspect_ratio(eye_ids):
                    points = [face_landmarks.landmark[i] for i in eye_ids]
                    coords = [(p.x * face_img.shape[1], p.y * face_img.shape[0]) for p in points]
                    A = np.linalg.norm(np.array(coords[1]) - np.array(coords[5]))
                    B = np.linalg.norm(np.array(coords[2]) - np.array(coords[4]))
                    C = np.linalg.norm(np.array(coords[0]) - np.array(coords[3]))
                    return (A + B) / (2.0 * C)

                left_ear = eye_aspect_ratio(left_eye_ids)
                right_ear = eye_aspect_ratio(right_eye_ids)
                avg_ear = (left_ear + right_ear) / 2.0

                print(f"{os.path.basename(image_path)} EAR: {avg_ear:.3f} → {'Closed' if avg_ear < eye_threshold else 'Open'}")

                if avg_ear < eye_threshold:
                    return True  # If any face has closed eyes, flag the image

    return False  # No face had closed eyes