"""
==========================================================
Face3D Studio AI

File:
uv_coordinate.py

Descrizione:
Coordinata UV di una mesh.

Autore:
Marco Cantù

==========================================================
"""

from dataclasses import dataclass


@dataclass(slots=True)
class UVCoordinate:
    """
    Coordinata UV.

    U = coordinata orizzontale della texture.
    V = coordinata verticale della texture.
    """

    u: float
    v: float