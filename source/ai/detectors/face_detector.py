"""
==========================================================
Face3D Studio AI

Face Detector Interface

Autore:
Marco Cantù
==========================================================
"""

from abc import ABC, abstractmethod

from source.ai.models.face_detection import FaceDetection


class FaceDetector(ABC):

    @abstractmethod
    def detect_faces(
        self,
        image_path: str,
    ) -> list[FaceDetection]:
        """
        Restituisce tutti i volti trovati.
        """
        raise NotImplementedError