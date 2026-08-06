"""
==========================================================
Face3D Studio AI

Vertex 3D

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from dataclasses import dataclass


@dataclass(slots=True)
class Vertex3D:
    """
    Vertice tridimensionale.
    """

    x: float
    y: float
    z: float