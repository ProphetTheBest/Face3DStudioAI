"""
==========================================================
Face3D Studio AI

Head Template

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from dataclasses import dataclass, field

from source.models.geometry.vertex3d import Vertex3D
from source.models.geometry.triangle import Triangle


@dataclass
class HeadTemplate:
    """
    Rappresenta un template anatomico caricato
    dal Reconstruction Engine.

    Il template è indipendente dal formato del file
    (OBJ, GLTF, FBX, ecc.).
    """

    name: str

    vertices: list[Vertex3D] = field(default_factory=list)

    triangles: list[Triangle] = field(default_factory=list)