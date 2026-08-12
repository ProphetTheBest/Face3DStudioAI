"""
==========================================================
Face3D Studio AI

Mesh Boundary Analyzer

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from source.models.face_mesh import FaceMesh


class MeshBoundaryAnalyzer:
    """
    Analizza il bordo della mesh.

    Questa prima versione costituisce il punto
    di ingresso per tutti gli algoritmi di analisi
    topologica.

    Sprint successivi:

    - rilevamento boundary edges
    - rilevamento boundary vertices
    - rilevamento hole loops
    - verifica mesh chiusa
    """

    @staticmethod
    def analyze(mesh: FaceMesh) -> list[int]:
        """
        Analizza la mesh e restituisce gli indici
        dei vertici appartenenti al bordo.

        Versione 1.1:
        individua gli edge di bordo analizzando
        la topologia triangolare.
        """

        edge_count: dict[tuple[int, int], int] = {}

        for triangle in mesh.triangles:

            edges = (
                (triangle.a, triangle.b),
                (triangle.b, triangle.c),
                (triangle.c, triangle.a),
            )

            for a, b in edges:

                edge = tuple(sorted((a, b)))

                edge_count[edge] = edge_count.get(edge, 0) + 1

        boundary_vertices: set[int] = set()

        for (a, b), count in edge_count.items():

            if count == 1:
                boundary_vertices.add(a)
                boundary_vertices.add(b)

        return sorted(boundary_vertices)