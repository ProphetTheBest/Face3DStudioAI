"""
==========================================================
Face3D Studio AI

Face Model

Autore:
Marco Cantù

Versione:
1.1.0
==========================================================
"""

from dataclasses import dataclass, field

from source.ai.models.face_detection import FaceDetection
from source.ai.models.face_landmark import FaceLandmark

from source.models.face_mesh import FaceMesh


@dataclass
class Face:
    """
    Rappresenta un volto rilevato all'interno
    di un ImageAsset.
    """

    #
    # Risultato Face Detection
    #

    detection: FaceDetection

    #
    # Stato GUI
    #

    selected: bool = False

    #
    # Landmark MediaPipe
    #

    landmarks: list[FaceLandmark] = field(
        default_factory=list
    )

    #
    # Mesh geometrica
    #

    mesh: FaceMesh | None = None

    #
    # Texture futura
    #

    texture = None