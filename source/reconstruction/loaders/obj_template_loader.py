"""
==========================================================
Face3D Studio AI

OBJ Template Loader

Autore:
Marco Cantù

Versione:
1.1.0
==========================================================
"""

from pathlib import Path

from source.models.geometry.triangle import Triangle
from source.models.geometry.vertex3d import Vertex3D


class ObjTemplateLoader:
    """
    Caricatore di template OBJ.

    Versione 1.1

    Supporta:

    - vertici
    - triangoli
    - quad (triangolati automaticamente)
    """

    @staticmethod
    def load_vertices(
        obj_path: Path,
    ) -> list[Vertex3D]:

        vertices: list[Vertex3D] = []

        with obj_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            for line in file:

                if not line.startswith("v "):
                    continue

                parts = line.split()

                vertices.append(
                    Vertex3D(
                        x=float(parts[1]),
                        y=float(parts[2]),
                        z=float(parts[3]),
                    )
                )

        return vertices

    @staticmethod
    def load_triangles(
        obj_path: Path,
    ) -> list[Triangle]:

        triangles: list[Triangle] = []

        with obj_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            for line in file:

                if not line.startswith("f "):
                    continue

                #
                # Esempi supportati:
                #
                # f 1 2 3
                # f 1/1 2/2 3/3
                # f 1/1/1 2/2/2 3/3/3
                # f 1/1 2/2 3/3 4/4
                #

                parts = line.split()[1:]

                indices: list[int] = []

                for part in parts:

                    vertex_index = int(
                        part.split("/")[0]
                    ) - 1

                    indices.append(vertex_index)

                #
                # Triangolo
                #

                if len(indices) == 3:

                    triangles.append(
                        Triangle(
                            a=indices[0],
                            b=indices[1],
                            c=indices[2],
                        )
                    )

                #
                # Quad
                #

                elif len(indices) == 4:

                    #
                    # 0-----1
                    # |   / |
                    # |  /  |
                    # | /   |
                    # 3-----2
                    #

                    triangles.append(
                        Triangle(
                            a=indices[0],
                            b=indices[1],
                            c=indices[2],
                        )
                    )

                    triangles.append(
                        Triangle(
                            a=indices[0],
                            b=indices[2],
                            c=indices[3],
                        )
                    )

                #
                # Poligoni con più di 4 lati
                #

                else:

                    print(
                        f"ATTENZIONE: poligono con {len(indices)} lati ignorato."
                    )

        return triangles