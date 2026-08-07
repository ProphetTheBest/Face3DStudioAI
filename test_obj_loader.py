from source.loaders.obj.obj_loader import ObjLoader


mesh = ObjLoader.load(

    "source/resources/mediapipe/canonical_face_model.obj"

)

print()

print("Vertices :", len(mesh.vertices))

print("Triangles:", len(mesh.triangles))

print()