"""
==========================================================
Face3D Studio AI

Detection Service

Autore:
Marco Cantù
==========================================================
"""

from source.ai.detectors.face_detector import FaceDetector
from source.ai.models.face_detection import FaceDetection


class DetectionService:

    def __init__(
        self,
        detector: FaceDetector,
    ):

        self._detector = detector

    # -----------------------------------------------------

    def detect(
        self,
        image_path: str,
    ) -> list[FaceDetection]:

        return self._detector.detect_faces(
            image_path
        )