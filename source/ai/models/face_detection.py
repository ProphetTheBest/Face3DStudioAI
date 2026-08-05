"""
==========================================================
Face3D Studio AI

Face Detection Model

Autore:
Marco Cantù
==========================================================
"""

from dataclasses import dataclass


@dataclass
class FaceDetection:
    """
    Rappresenta un volto rilevato.
    Coordinate espresse in pixel.
    """

    x: int
    y: int

    width: int
    height: int

    score: float