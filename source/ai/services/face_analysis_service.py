"""
==========================================================
Face3D Studio AI

Face Analysis Service

Autore:
Marco Cantù

Versione:
1.4.0
==========================================================
"""

from source.ai.providers.mediapipe_face_detector import (
    MediaPipeFaceDetector,
)

from source.ai.providers.mediapipe_face_landmarker import (
    MediaPipeFaceLandmarker,
)

from source.ai.services.detection_service import (
    DetectionService,
)

from source.models.geometry.builders.face_mesh_builder import (
    FaceMeshBuilder,
)

from source.models.assets.image_asset import ImageAsset
from source.models.face import Face
from source.models.geometry.vertex3d import Vertex3D


class FaceAnalysisService:
    """
    Analizza un'immagine e costruisce
    il modello dati del volto.
    """

    def __init__(self):

        self._detection_service = DetectionService(
            MediaPipeFaceDetector()
        )

        self._face_mesh = MediaPipeFaceLandmarker()

    # ---------------------------------------------------------

    def analyze(
        self,
        image_asset: ImageAsset,
        filename: str,
    ) -> None:

        detections = self._detection_service.detect(
            filename
        )

        mesh_faces = self._face_mesh.detect(
            filename
        )

        image_asset.faces.clear()

        for index, detection in enumerate(detections):

            face = Face(
                detection=detection
            )

            if index < len(mesh_faces):

                landmarks = mesh_faces[index]

                face.landmarks = landmarks

                print("Landmarks:", len(face.landmarks))

                vertices = [

                    Vertex3D(
                        x=(lm.x - 0.5) * 2.0,
                        y=(0.5 - lm.y) * 2.0,
                        z=-lm.z * 2.0,
                    )

                    for lm in landmarks

                ]

                print("\n===== PRIMA DEL BUILDER =====")

                v = vertices[0]

                print(v.x, v.y, v.z)

                face.mesh = FaceMeshBuilder.build(
                    vertices
                )

            print("===== DOPO IL BUILDER =====")

            v = face.mesh.vertices[0]

            print(v.x, v.y, v.z)

            print("Vertices mesh:", len(face.mesh.vertices))

            print("Primo vertice mesh:")
            v = face.mesh.vertices[0]
            print(v.x, v.y, v.z)

            print("Primo landmark:")
            lm = landmarks[0]
            print(lm.x, lm.y, lm.z)

            image_asset.faces.append(face)