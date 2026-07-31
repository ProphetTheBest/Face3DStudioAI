"""
==========================================================
Face3D Studio AI

Project Controller

Autore:
Marco Cantù

Versione:
1.1.0
==========================================================
"""

from source.models.assets.asset import Asset
from source.models.project import Project
from source.services.asset.image_importer import ImageImporter
from source.services.project.project_manager import ProjectManager


class ProjectController:
    """
    Controller del progetto.
    """

    def __init__(
        self,
        project_manager: ProjectManager,
    ) -> None:

        self._project_manager = project_manager
        self._image_importer = ImageImporter()

    # ---------------------------------------------------------
    # Gestione progetto
    # ---------------------------------------------------------

    def create_project(
        self,
        project_name: str,
        project_folder: str,
    ) -> None:

        self._project_manager.create_project(
            project_name,
            project_folder,
        )

    # ---------------------------------------------------------

    def open_project(
        self,
        project_folder: str,
    ) -> None:

        self._project_manager.open_project(project_folder)

    # ---------------------------------------------------------

    def get_project(self) -> Project | None:

        return self._project_manager.current_project

    # ---------------------------------------------------------

    def get_project_name(self) -> str:

        project = self.get_project()

        return project.name if project else "Untitled"

    # ---------------------------------------------------------

    def get_project_folder(self) -> str:

        project = self.get_project()

        return project.project_folder if project else ""

    # =========================================================
    # Asset
    # =========================================================

    def get_assets(self) -> list[Asset]:

        project = self.get_project()

        return project.assets if project else []

    # ---------------------------------------------------------

    def add_asset(self, asset: Asset) -> None:

        self._project_manager.add_asset(asset)

    # ---------------------------------------------------------

    def remove_asset(self, asset: Asset) -> None:

        self._project_manager.remove_asset(asset)

    # ---------------------------------------------------------

    def import_images(self, file_list: list[str]) -> None:

        project = self.get_project()

        if project is None:
            raise RuntimeError("Nessun progetto aperto.")

        for filename in file_list:

            asset = self._image_importer.import_image(
                filename,
                project.project_folder,
            )

            self._project_manager.add_asset(asset)

        self._project_manager.save_project(
            project.project_folder
        )

    # =========================================================
    # Conteggi
    # =========================================================

    def get_asset_count(self) -> int:

        return self._project_manager.asset_count()