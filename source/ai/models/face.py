"""
==========================================================
Face3D Studio AI

Face Model

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from dataclasses import dataclass, field

from source.ai.models.face_detection import FaceDetection


@dataclass
class Face:
    """
    Rappresenta un volto del progetto.
    """

    detection: FaceDetection

    selected: bool = False

    landmarks: list = field(default_factory=list)

    mesh = None

    texture = None