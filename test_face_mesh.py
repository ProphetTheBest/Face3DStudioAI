from source.ai.providers.mediapipe_face_mesh import MediaPipeFaceMesh

mesh = MediaPipeFaceMesh()

faces = mesh.detect("test.jpg")

print()

print("----------------------------------")

print("Volti:", len(faces))

if faces:

    print("Landmark:", len(faces[0]))

    print()

    print(faces[0][0])

print("----------------------------------")