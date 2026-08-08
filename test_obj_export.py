from pathlib import Path

from source.io.obj_exporter import ObjExporter
from source.models.face_mesh import FaceMesh
from source.models.vertex import Vertex
from source.models.triangle import Triangle


def create_test_mesh():

    mesh = FaceMesh()

    #
    # Vertices
    #

    mesh.vertices = [

        Vertex(0.0, 0.0, 0.0),

        Vertex(1.0, 0.0, 0.0),

        Vertex(0.0, 1.0, 0.0),

    ]

    #
    # Triangle
    #

    mesh.triangles = [

        Triangle(0, 1, 2),

    ]

    return mesh


def main():

    mesh = create_test_mesh()

    exporter = ObjExporter()

    exporter.export(
        mesh,
        "test_face.obj",
    )

    print("OBJ creato correttamente.")


if __name__ == "__main__":

    main()