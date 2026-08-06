"""
==========================================================
Face3D Studio AI

OBJ Exporter

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from pathlib import Path

from source.models.face_mesh import FaceMesh


class ObjExporter:
    """
    Esporta una FaceMesh nel formato OBJ.
    """

    @staticmethod
    def export(
        mesh: FaceMesh,
        filename: str,
    ) -> None:

        path = Path(filename)

        with path.open(
            "w",
            encoding="utf-8",
        ) as file:

            file.write("# Face3D Studio AI\n")
            file.write("# OBJ Export\n\n")

            #
            # Vertici
            #

            for vertex in mesh.vertices:

                file.write(

                    f"v {vertex.x:.6f} "
                    f"{vertex.y:.6f} "
                    f"{vertex.z:.6f}\n"

                )

            #
            # Triangoli
            #

            for triangle in mesh.triangles:

                file.write(

                    f"f "
                    f"{triangle.a+1} "
                    f"{triangle.b+1} "
                    f"{triangle.c+1}\n"

                )