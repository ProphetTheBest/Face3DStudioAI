from pathlib import Path

import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


MODEL = "source/resources/mediapipe/face_landmarker.task"

IMAGE = "test.jpg"      # <-- sostituisci con una tua foto


base_options = python.BaseOptions(
    model_asset_path=MODEL,
)

options = vision.FaceLandmarkerOptions(

    base_options=base_options,

    output_face_blendshapes=True,

    output_facial_transformation_matrixes=True,

    num_faces=5,

)

detector = vision.FaceLandmarker.create_from_options(
    options
)

image = mp.Image.create_from_file(IMAGE)

result = detector.detect(image)

print()

print("Faces:", len(result.face_landmarks))

print("BlendShapes:", len(result.face_blendshapes))

print(
    "Transformation Matrix:",
    len(result.facial_transformation_matrixes),
)

if result.face_landmarks:

    print()

    print(
        "Landmark:",
        len(result.face_landmarks[0]),
    )

print()