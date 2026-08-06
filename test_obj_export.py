from source.exporters.obj.obj_exporter import ObjExporter

from source.models.geometry.vertex3d import Vertex3D
from source.models.face_mesh import FaceMesh


mesh = FaceMesh()

mesh.vertices = [

    Vertex3D(0, 0, 0),

    Vertex3D(1, 0, 0),

    Vertex3D(0, 1, 0),

]

ObjExporter.export(

    mesh,

    "test.obj",

)

print("OBJ creato.")