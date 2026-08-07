"""
==========================================================
Face3D Studio AI

OBJ Loader

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from pathlib import Path

from source.models.face_mesh import FaceMesh
from source.models.geometry.vertex3d import Vertex3D
from source.models.geometry.triangle import Triangle


class ObjLoader:
    """
    Carica un file OBJ.
    """

    @staticmethod
    def load(filename: str) -> FaceMesh:

        mesh = FaceMesh()

        path = Path(filename)

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            for line in file:

                line = line.strip()

                if not line:

                    continue

                #
                # Vertice
                #

                if line.startswith("v "):

                    values = line.split()

                    mesh.vertices.append(

                        Vertex3D(

                            float(values[1]),
                            float(values[2]),
                            float(values[3]),

                        )

                    )

                #
                # Triangolo
                #

                elif line.startswith("f "):

                    values = line.split()

                    indices = []

                    for value in values[1:]:

                        #
                        # Supporta anche:
                        #
                        # f 1/2/3
                        #

                        index = value.split("/")[0]

                        indices.append(

                            int(index) - 1

                        )

                    if len(indices) == 3:

                        mesh.triangles.append(

                            Triangle(

                                indices[0],
                                indices[1],
                                indices[2],

                            )

                        )

        return mesh