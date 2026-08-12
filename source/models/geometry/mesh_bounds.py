"""
==========================================================
Face3D Studio AI

Mesh Bounds

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from dataclasses import dataclass

from source.models.geometry.vertex3d import Vertex3D


@dataclass(slots=True)
class MeshBounds:
    """
    Bounding box di una mesh.

    Contiene tutte le informazioni
    geometriche fondamentali utilizzate
    dagli algoritmi di allineamento
    e deformazione.
    """

    min_x: float
    max_x: float

    min_y: float
    max_y: float

    min_z: float
    max_z: float

    width: float
    height: float
    depth: float

    center: Vertex3D