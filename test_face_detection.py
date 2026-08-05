from source.ai.providers.mediapipe_face_detector import MediaPipeFaceDetector

detector = MediaPipeFaceDetector()

faces = detector.detect_faces(
    "test.jpg"
)

print()

print("--------------------------------")

print(f"Volti trovati: {len(faces)}")

for face in faces:

    print(face)

print("--------------------------------")