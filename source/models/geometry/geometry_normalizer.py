"""
==========================================================
Face3D Studio AI

Geometry Normalizer

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from source.models.face_mesh import FaceMesh


class GeometryNormalizer:
    """
    Normalizza una mesh geometrica.

    - centra il modello
    - uniforma la scala
    """

    @staticmethod
    def normalize(mesh: FaceMesh) -> None:

        if not mesh.vertices:
            return

        #
        # Bounding Box
        #

        min_x = min(v.x for v in mesh.vertices)
        max_x = max(v.x for v in mesh.vertices)

        min_y = min(v.y for v in mesh.vertices)
        max_y = max(v.y for v in mesh.vertices)

        min_z = min(v.z for v in mesh.vertices)
        max_z = max(v.z for v in mesh.vertices)

        #
        # Centro
        #

        cx = (min_x + max_x) / 2
        cy = (min_y + max_y) / 2
        cz = (min_z + max_z) / 2

        print("\n===== NORMALIZER =====")
        print(f"Center : {cx:.6f} {cy:.6f} {cz:.6f}")

        #
        # Scala
        #

        size = max(

            max_x - min_x,
            max_y - min_y,
            max_z - min_z,

        )

        if size == 0:
            size = 1.0

        print(f"Size   : {size:.6f}")
        print("======================")

        #
        # Normalizzazione
        #

        for vertex in mesh.vertices:

            vertex.x = (vertex.x - cx) / size
            vertex.y = (vertex.y - cy) / size
            vertex.z = (vertex.z - cz) / size