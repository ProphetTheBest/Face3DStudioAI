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

            mtl_name = path.with_suffix(
                ".mtl"
            ).name

            file.write(
                f"mtllib {mtl_name}\n\n"
            )

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
            # Coordinate UV
            #

            for uv in mesh.uv_coordinates:

                file.write(

                    f"vt {uv.u:.6f} "
                    f"{uv.v:.6f}\n"

                )

            file.write("\n")

            #
            # Triangoli
            #

            file.write(
                "usemtl FaceMaterial\n\n"
            )

            for triangle in mesh.triangles:

                a = triangle.a + 1
                b = triangle.b + 1
                c = triangle.c + 1

                file.write(

                    f"f "

                    f"{a}/{a} "

                    f"{b}/{b} "

                    f"{c}/{c}\n"

                )