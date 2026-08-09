"""
==========================================================
Face3D Studio AI

File:
uv_mapper.py

Descrizione:
Genera le coordinate UV della mesh del volto.

Autore:
Marco Cantù

==========================================================
"""

from source.models.face import Face
from source.models.uv_coordinate import UVCoordinate


class UVMapper:
    """
    Genera le coordinate UV della FaceMesh.
    """

    # ---------------------------------------------------------

    @staticmethod
    def generate(face: Face) -> None:
        """
        Genera le coordinate UV della mesh.

        Per ora il metodo è solo uno scheletro.
        Verrà implementato nello step successivo.
        """

        if face is None:
            raise ValueError("Face is None.")

        if face.mesh is None:
            raise ValueError("Face mesh is None.")

        if not face.landmarks:
            raise ValueError("Face contains no landmarks.")

        face.mesh.uv_coordinates.clear()

        for index in range(len(face.mesh.vertices)):

            landmark = face.landmarks[index]

            uv = UVCoordinate(

                u=landmark.x,

                v=1.0 - landmark.y,

            )

            face.mesh.uv_coordinates.append(
                uv
            )

        if len(face.mesh.vertices) != len(face.mesh.uv_coordinates):
            raise RuntimeError(
                "Vertex count and UV count do not match."
            )