"""
==========================================================
Face3D Studio AI

Project Controller

Autore:
Marco Cantù

Versione:
0.5.0
==========================================================
"""

from source.models.project import Project
from source.services.project.project_manager import ProjectManager


class ProjectController:
    """
    Controller del progetto.

    Coordina la logica relativa al progetto e rappresenta
    il punto di accesso della GUI per tutte le operazioni
    sul progetto.
    """

    def __init__(
        self,
        project_manager: ProjectManager,
    ) -> None:

        self._project_manager = project_manager

    # ---------------------------------------------------------
    # Gestione progetto
    # ---------------------------------------------------------

    def create_project(
        self,
        project_name: str,
        project_folder: str,
    ) -> None:
        """
        Crea un nuovo progetto.
        """

        self._project_manager.create_project(
            project_name,
            project_folder,
        )

    # ---------------------------------------------------------

    def open_project(
        self,
        project_folder: str,
    ) -> None:
        """
        Apre un progetto esistente.
        """

        self._project_manager.open_project(project_folder)

    # ---------------------------------------------------------

    def get_project(self) -> Project | None:
        """
        Restituisce il progetto corrente.
        """

        return self._project_manager.current_project

    # ---------------------------------------------------------

    def get_project_name(self) -> str:
        """
        Restituisce il nome del progetto corrente.
        """

        project = self.get_project()

        if project is None:
            return "Untitled"

        return project.name
    

    def get_project_folder(self) -> str:
        """
        Restituisce la cartella del progetto.
        """

        project = self.get_project()

        if project is None:
            return ""

        return project.project_folder
    # ---------------------------------------------------------
    # Foto
    # ---------------------------------------------------------

    def get_photos(self):
        """
        Restituisce la lista delle fotografie del progetto.
        """

        project = self.get_project()

        if project is None:
            return []

        return project.photos
    # ---------------------------------------------------------
    # Conteggi
    # ---------------------------------------------------------

    def get_photo_count(self) -> int:

        project = self.get_project()

        return len(project.photos) if project else 0

    # ---------------------------------------------------------

    def get_video_count(self) -> int:

        project = self.get_project()

        return len(project.videos) if project else 0

    # ---------------------------------------------------------

    def get_frame_count(self) -> int:

        project = self.get_project()

        return len(project.frames) if project else 0

    # ---------------------------------------------------------

    def get_landmark_count(self) -> int:

        project = self.get_project()

        return len(project.landmarks) if project else 0

    # ---------------------------------------------------------

    def get_mesh_count(self) -> int:

        project = self.get_project()

        return len(project.meshes) if project else 0

    # ---------------------------------------------------------

    def get_export_count(self) -> int:

        project = self.get_project()

        return len(project.exports) if project else 0