"""
==========================================================
Face3D Studio AI

Face Mesh Builder

Autore:
Marco Cantù

Versione:
1.1.0
==========================================================
"""

from source.ai.topology.face_mesh_topology import TESSELATION

from source.models.face_mesh import FaceMesh
from source.models.geometry.vertex3d import Vertex3D


class FaceMeshBuilder:
    """
    Costruisce una FaceMesh a partire
    dai vertici 3D.
    """

    @staticmethod
    def build(
        vertices: list[Vertex3D],
    ) -> FaceMesh:

        mesh = FaceMesh()

        mesh.vertices = vertices

        mesh.edges = list(TESSELATION)

        #
        # I triangoli verranno aggiunti
        # nello sprint successivo.
        #

        return mesh