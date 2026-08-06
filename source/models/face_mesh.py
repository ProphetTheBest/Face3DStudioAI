"""
==========================================================
Face3D Studio AI

Face Mesh Model

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from dataclasses import dataclass, field

from source.ai.models.face_landmark import FaceLandmark


@dataclass
class FaceMesh:
    """
    Modello geometrico della mesh facciale.

    Contiene la geometria del volto indipendentemente
    dal motore AI utilizzato.
    """

    #
    # Vertici
    #

    vertices: list[FaceLandmark] = field(
        default_factory=list
    )

    #
    # Connessioni MediaPipe
    #

    edges: list[tuple[int, int]] = field(
        default_factory=list
    )

    #
    # Triangoli
    #

    triangles: list[tuple[int, int, int]] = field(
        default_factory=list
    )