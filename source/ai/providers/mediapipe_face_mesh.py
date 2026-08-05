"""
==========================================================
Face3D Studio AI

MediaPipe Face Mesh

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

import cv2
import mediapipe as mp

from source.ai.models.face_landmark import FaceLandmark


class MediaPipeFaceMesh:

    def __init__(self):

        self._mesh = mp.solutions.face_mesh.FaceMesh(

            static_image_mode=True,

            max_num_faces=5,

            refine_landmarks=True,

            min_detection_confidence=0.5,

        )

    # ---------------------------------------------------------

    def detect(self, image_path: str):

        image = cv2.imread(image_path)

        print("cv2.imread:", image is not None)

        if image is not None:
            print("Shape:", image.shape)        

        if image is None:
            return []

        rgb = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB,
        )

        result = self._mesh.process(rgb)

        if not result.multi_face_landmarks:

            return []

        faces = []

        for face in result.multi_face_landmarks:

            landmarks = []

            for point in face.landmark:

                landmarks.append(

                    FaceLandmark(

                        point.x,

                        point.y,

                        point.z,

                    )

                )

            faces.append(landmarks)

        return faces