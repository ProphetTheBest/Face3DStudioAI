from source.ai.topology.canonical_face_model import (
    CanonicalFaceModel,
)

mesh = CanonicalFaceModel.mesh()

print()

print("Vertices :", len(mesh.vertices))
print("Triangles:", len(mesh.triangles))

print()