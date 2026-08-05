"""
==========================================================
Face3D Studio AI

Face Manager

Autore:
Marco Cantù

Versione:
1.1.0
==========================================================
"""

from source.ai.models.face import Face


class FaceManager:

    def __init__(self):

        self._faces: list[Face] = []

        self._selected_index: int = -1

    # ---------------------------------------------------------

    def clear(self):

        self._faces.clear()

        self._selected_index = -1

    # ---------------------------------------------------------

    def set_faces(
        self,
        faces: list[Face],
    ):

        self.clear()

        self._faces = faces

        if self._faces:

            self.select(0)

    # ---------------------------------------------------------

    def faces(self) -> list[Face]:

        return self._faces

    # ---------------------------------------------------------

    def face_count(self) -> int:

        return len(self._faces)

    # ---------------------------------------------------------

    def selected_face(self) -> Face | None:

        if self._selected_index < 0:
            return None

        return self._faces[self._selected_index]

    # ---------------------------------------------------------

    def selected_index(self) -> int:

        return self._selected_index

    # ---------------------------------------------------------

    def select(
        self,
        index: int,
    ):

        if index < 0:
            return

        if index >= len(self._faces):
            return

        #
        # Deseleziona tutti
        #

        for face in self._faces:

            face.selected = False

        #
        # Seleziona il nuovo volto
        #

        self._faces[index].selected = True

        self._selected_index = index