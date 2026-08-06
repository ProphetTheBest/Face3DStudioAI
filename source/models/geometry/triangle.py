"""
==========================================================
Face3D Studio AI

Triangle

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from dataclasses import dataclass


@dataclass(slots=True)
class Triangle:
    """
    Triangolo della mesh.
    """

    v1: int
    v2: int
    v3: int