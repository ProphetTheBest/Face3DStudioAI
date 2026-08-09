"""
==========================================================
Face3D Studio AI

Face Mesh Model

Autore:
Marco Cantù

Versione:
1.1.0
==========================================================
"""

from dataclasses import dataclass, field

from source.models.geometry.vertex3d import Vertex3D
from source.models.geometry.triangle import Triangle
from source.models.uv_coordinate import UVCoordinate


@dataclass(slots=True)
class FaceMesh:
    """
    Mesh geometrica del volto.

    Questa classe è indipendente dal provider AI.
    Contiene esclusivamente dati geometrici.
    """

    #
    # Vertici 3D
    #

    vertices: list[Vertex3D] = field(
        default_factory=list
    )

    #
    # Connessioni (wireframe)
    #

    edges: list[tuple[int, int]] = field(
        default_factory=list
    )

    #
    # Triangoli
    #

    triangles: list[Triangle] = field(
        default_factory=list
    )

    #
    # Coordinate UV
    #

    uv_coordinates: list[UVCoordinate] = field(
        default_factory=list
    )