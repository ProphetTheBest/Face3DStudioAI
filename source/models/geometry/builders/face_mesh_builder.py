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
from source.models.geometry.geometry_normalizer import GeometryNormalizer
from source.ai.topology.canonical_face_model import (
    CanonicalFaceModel,
)

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

        #
        # Il Canonical Face Model utilizza
        # solamente i primi 468 landmark.
        #

        mesh.vertices = [

            Vertex3D(
                x=v.x,
                y=v.y,
                z=v.z,
            )

            for v in vertices[:468]

        ]

        mesh.edges = list(TESSELATION)

        canonical = CanonicalFaceModel.mesh()

        mesh.triangles = canonical.triangles
        #
        # Centro e scala
        #

        # GeometryNormalizer.normalize(mesh)

        return mesh