"""
==========================================================
Face3D Studio AI

Project Controller

Autore:
Marco Cantù

Versione:
0.2.0
==========================================================
"""

from source.models.project import Project


class ProjectController:
    """
    Controller del progetto.

    Gestisce tutte le operazioni
    sul Project Model.
    """

    def __init__(self) -> None:

        self.project = Project()

    # ---------------------------------------------------------
    # Gestione progetto
    # ---------------------------------------------------------

    def new_project(self, name: str = "Untitled") -> None:

        self.project = Project(name=name)

    # ---------------------------------------------------------

    def get_project(self) -> Project:

        return self.project

    # ---------------------------------------------------------

    def get_project_name(self) -> str:

        return self.project.name

    # ---------------------------------------------------------
    # Conteggi
    # ---------------------------------------------------------

    def get_photo_count(self) -> int:

        return len(self.project.photos)

    # ---------------------------------------------------------

    def get_video_count(self) -> int:

        return len(self.project.videos)

    # ---------------------------------------------------------

    def get_frame_count(self) -> int:

        return len(self.project.frames)

    # ---------------------------------------------------------

    def get_landmark_count(self) -> int:

        return len(self.project.landmarks)

    # ---------------------------------------------------------

    def get_mesh_count(self) -> int:

        return len(self.project.meshes)

    # ---------------------------------------------------------

    def get_export_count(self) -> int:

        return len(self.project.exports)