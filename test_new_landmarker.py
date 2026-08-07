from source.ai.providers.mediapipe_face_landmarker import (
    MediaPipeFaceLandmarker,
)

provider = MediaPipeFaceLandmarker()

faces = provider.detect(
    r"C:\Progetti\Face3DStudio\test.jpg"
)

print()

print("Faces:", len(faces))

if faces:

    print(
        "Landmarks:",
        len(faces[0])
    )

print()