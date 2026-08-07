"""
==========================================================
Face3D Studio AI

MediaPipe Face Landmarker

Autore:
Marco Cantù

Versione:
2.0.0
==========================================================
"""

from pathlib import Path

import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from source.ai.models.face_landmark import FaceLandmark


class MediaPipeFaceLandmarker:

    def __init__(self):

        MODEL = (
            Path(__file__).resolve().parents[2]
            / "resources"
            / "mediapipe"
            / "face_landmarker.task"
        )

        self.last_pose_matrix = None
        self.last_blendshapes = None

        print("MODEL EXISTS :", MODEL.exists())
        print("MODEL PATH   :", MODEL)

        with open(MODEL, "rb") as f:
            model_data = f.read()

        base_options = python.BaseOptions(
            model_asset_buffer=model_data
        )

        options = vision.FaceLandmarkerOptions(

            base_options=base_options,

            num_faces=5,

            output_face_blendshapes=True,

            output_facial_transformation_matrixes=True,

        )

        self._detector = (
            vision.FaceLandmarker.create_from_options(
                options
            )
        )

    # -----------------------------------------------------

    def detect(
        self,
        filename: str,
    ):

        image = mp.Image.create_from_file(
            filename
        )

        result = self._detector.detect(
            image
        )

        if result.facial_transformation_matrixes:
            self.last_pose_matrix = result.facial_transformation_matrixes[0]
        else:
            self.last_pose_matrix = None

        if result.face_blendshapes:
            self.last_blendshapes = result.face_blendshapes[0]
        else:
            self.last_blendshapes = None

        print()

        print("========== FACE LANDMARKER ==========")

        print("Faces :", len(result.face_landmarks))

        print(
            "Matrices :",
            len(result.facial_transformation_matrixes)
        )

        if result.facial_transformation_matrixes:

            matrix = result.facial_transformation_matrixes[0]

            print()

            print(type(matrix))

            print(matrix)

        print()

        print("=====================================")

        faces = []

        for landmarks in result.face_landmarks:

            face = []

            for lm in landmarks:

                face.append(

                    FaceLandmark(

                        lm.x,

                        lm.y,

                        lm.z,

                    )

                )

            faces.append(
                face
            )

        return faces