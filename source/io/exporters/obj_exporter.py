"""
==========================================================
Face3D Studio AI

OBJ Exporter

Autore:
Marco Cantù

==========================================================
"""

from pathlib import Path

from source.models.face_mesh import FaceMesh


class ObjExporter:

    """
    Esporta una FaceMesh nel formato Wavefront OBJ.
    """

    def export(
        self,
        mesh: FaceMesh,
        filename: str,
    ) -> None:

        #
        # Output file
        #

        output_path = Path(filename)

        with output_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            #
            # Header
            #

            file.write("# ======================================\n")
            file.write("# Face3D Studio AI\n")
            file.write("# Wavefront OBJ\n")
            file.write("# ======================================\n")
            file.write("\n")

            #
            # Vertices
            #

            for vertex in mesh.vertices:

                file.write(
                    f"v {vertex.x:.6f} "
                    f"{vertex.y:.6f} "
                    f"{vertex.z:.6f}\n"
                )

            file.write("\n")

            #
            # Faces
            #

            for triangle in mesh.triangles:

                file.write(
                    f"f "
                    f"{triangle.a + 1} "
                    f"{triangle.b + 1} "
                    f"{triangle.c + 1}\n"
                )