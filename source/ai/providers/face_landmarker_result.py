"""
==========================================================
Face3D Studio AI

Face Landmarker Result

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from dataclasses import dataclass, field

from source.ai.models.face_landmark import FaceLandmark


@dataclass
class FaceLandmarkerFace:
    """
    Contiene tutte le informazioni
    relative ad un volto rilevato.
    """

    landmarks: list[FaceLandmark] = field(default_factory=list)

    blendshapes: list = field(default_factory=list)

    transformation_matrix = None


@dataclass
class FaceLandmarkerResult:
    """
    Risultato completo del Face Landmarker.
    """

    faces: list[FaceLandmarkerFace] = field(default_factory=list)