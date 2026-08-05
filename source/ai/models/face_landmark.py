"""
==========================================================
Face3D Studio AI

Face Landmark

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from dataclasses import dataclass


@dataclass(slots=True)
class FaceLandmark:
    """
    Un punto del volto.

    Coordinate normalizzate (0..1)
    restituite da MediaPipe Face Mesh.
    """

    x: float
    y: float
    z: float