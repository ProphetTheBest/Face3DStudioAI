"""
==========================================================
Face3D Studio AI

Triangle

Autore:
Marco Cantù

Versione:
1.1.0
==========================================================
"""

from dataclasses import dataclass


@dataclass(slots=True)
class Triangle:
    """
    Triangolo della mesh.

    I valori rappresentano gli indici
    dei tre vertici nella lista vertices.
    """

    a: int

    b: int

    c: int