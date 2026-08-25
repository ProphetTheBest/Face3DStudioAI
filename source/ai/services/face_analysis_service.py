"""
==========================================================
Face3D Studio AI

Face Analysis Service

Autore:
Marco Cantù

Versione:
1.6.0
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

from source.reconstruction.pipeline.head_reconstruction_pipeline import (
    HeadReconstructionPipeline,
)

from source.mapping.uv.uv_mapper import UVMapper

from source.models.assets.image_asset import ImageAsset
from source.models.face import Face
from source.models.geometry.vertex3d import Vertex3D
from source.models.canonical_asset import CanonicalAsset

from source.analysis.geometry.geometry_analyzer import (
    GeometryAnalyzer,
)

from source.analysis.landmarks.landmark_analyzer import (
    LandmarkAnalyzer,
)


class FaceAnalysisService:
    """
    Analizza un'immagine e costruisce
    il modello dati del volto.

    La FaceMesh MediaPipe viene sempre costruita.

    La ricostruzione della testa tramite
    HeadReconstructionPipeline viene eseguita
    esclusivamente quando è disponibile un
    CanonicalAsset valido.

    Il CanonicalAsset rappresenta la sorgente
    canonica completa del Reconstruction Engine
    e contiene:

        - Canonical Mesh;
        - Canonical Mapping.

    Il Service non costruisce né carica
    direttamente la Canonical Mesh.

    Il CanonicalAsset viene ricevuto dal
    livello applicativo e inoltrato alla
    HeadReconstructionPipeline.
    """

    def __init__(self):

        self._detection_service = DetectionService(
            MediaPipeFaceDetector()
        )

        self._face_mesh = MediaPipeFaceLandmarker()

    # ---------------------------------------------------------
    # ANALISI
    # ---------------------------------------------------------

    def analyze(
        self,
        image_asset: ImageAsset,
        filename: str,
        canonical_asset: CanonicalAsset | None = None,
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

                #
                # Salviamo già i dati restituiti
                # da MediaPipe.
                #

                face.pose_matrix = (
                    self._face_mesh.last_pose_matrix
                )

                face.blendshapes = (
                    self._face_mesh.last_blendshapes
                )

                vertices = [

                    Vertex3D(
                        x=(lm.x - 0.5) * 2.0,
                        y=(0.5 - lm.y) * 2.0,
                        z=-lm.z * 2.0,
                    )

                    for lm in landmarks

                ]

                #
                # La FaceMesh MediaPipe viene
                # sempre costruita.
                #
                # Questa è la mesh di base che
                # consente alla GUI di visualizzare
                # il volto anche quando il
                # CanonicalAsset non è disponibile.
                #

                face.mesh = FaceMeshBuilder.build(
                    vertices
                )

                #
                # Reconstruction Engine
                #
                # La ricostruzione avanzata viene
                # eseguita soltanto quando è
                # disponibile un CanonicalAsset
                # valido.
                #
                # Il CanonicalAsset contiene sia
                # la Canonical Mesh sia il
                # Canonical Mapping.
                #
                # Non costruiamo mapping automatici
                # e non bypassiamo le validazioni
                # del Reconstruction Engine.
                #

                if (
                    canonical_asset is not None
                    and canonical_asset.is_valid()
                ):

                    face = HeadReconstructionPipeline.build(
                        face,
                        canonical_asset,
                    )

                #
                # UV
                #

                UVMapper.generate(
                    face
                )

                #
                # Analisi
                #

                face.landmark_report = (
                    LandmarkAnalyzer.analyze(
                        face
                    )
                )

                face.geometry_report = (
                    GeometryAnalyzer.analyze(
                        face
                    )
                )

            image_asset.faces.append(face)