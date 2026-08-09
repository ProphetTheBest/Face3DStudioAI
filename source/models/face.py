"""
==========================================================
Face3D Studio AI

Face Model

Autore:
Marco Cantù

Versione:
1.2.0
==========================================================
"""

from dataclasses import dataclass, field

import numpy as np

from source.ai.models.face_detection import FaceDetection
from source.ai.models.face_landmark import FaceLandmark

from source.models.face_mesh import FaceMesh


@dataclass
class Face:
    """
    Rappresenta un volto rilevato
    all'interno di una immagine.
    """

    #
    # Face Detection
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
    # Matrice di posa MediaPipe (4x4)
    #

    pose_matrix: np.ndarray | None = None

    #
    # BlendShapes
    #

    blendshapes: list | None = None

    #
    # Analysis Reports
    #

    geometry_report = None

    landmark_report = None

    #
    # Texture futura
    #

    texture = None