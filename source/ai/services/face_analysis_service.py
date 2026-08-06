"""
==========================================================
Face3D Studio AI

Face Analysis Service

Autore:
Marco Cantù

Versione:
1.1.0
==========================================================
"""

from source.ai.providers.mediapipe_face_detector import (
    MediaPipeFaceDetector,
)

from source.ai.providers.mediapipe_face_mesh import (
    MediaPipeFaceMesh,
)

from source.ai.services.detection_service import (
    DetectionService,
)

from source.ai.topology.face_mesh_topology import (
    TESSELATION,
)

from source.models.assets.image_asset import ImageAsset
from source.models.face import Face
from source.models.face_mesh import FaceMesh


class FaceAnalysisService:
    """
    Analizza un ImageAsset e costruisce
    il modello dati del volto.
    """

    def __init__(self):

        self._detection_service = DetectionService(
            MediaPipeFaceDetector()
        )

        self._face_mesh = MediaPipeFaceMesh()

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

            #
            # Landmark
            #

            if index < len(mesh_faces):

                landmarks = mesh_faces[index]

                face.landmarks = landmarks

                #
                # Costruzione Mesh
                #

                face.mesh = FaceMesh(

                    vertices=landmarks,

                    edges=TESSELATION,

                )

            image_asset.faces.append(face)