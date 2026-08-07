"""
==========================================================
Face3D Studio AI

Canonical Face Model

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from pathlib import Path

from source.loaders.obj.obj_loader import ObjLoader
from source.models.face_mesh import FaceMesh


class CanonicalFaceModel:
    """
    Singleton che carica una sola volta
    il modello canonico di MediaPipe.
    """

    _mesh: FaceMesh | None = None

    @classmethod
    def mesh(cls) -> FaceMesh:

        if cls._mesh is None:

            filename = (
                Path(__file__)
                .parent.parent.parent
                / "resources"
                / "mediapipe"
                / "canonical_face_model.obj"
            )

            cls._mesh = ObjLoader.load(
                str(filename)
            )

        return cls._mesh