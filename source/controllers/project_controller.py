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
        
        self._current_asset: Asset | None = None
        self._image_importer = ImageImporter()
        self._project_manager = project_manager

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
        
        self.clear_current_asset()
    # ---------------------------------------------------------

    def open_project(
        self,
        project_folder: str,
    ) -> None:

        self._project_manager.open_project(project_folder)
        self.clear_current_asset()
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

    def get_asset_by_id(
        self,
        asset_id: str,
    ) -> Asset | None:
        """
        Restituisce un asset tramite il suo identificativo.
        """

        for asset in self.get_assets():

            if asset.id == asset_id:
                return asset

        return None
    # ---------------------------------------------------------

    def add_asset(self, asset: Asset) -> None:

        self._project_manager.add_asset(asset)

    # ---------------------------------------------------------

    def remove_asset(self, asset: Asset) -> None:

        self._project_manager.remove_asset(asset)

    # ---------------------------------------------------------
    # ---------------------------------------------------------

    def set_current_asset(
        self,
        asset: Asset | None,
    ) -> None:
        """
        Imposta l'asset attualmente selezionato.
        """

        self._current_asset = asset

    # ---------------------------------------------------------

    def get_current_asset(self) -> Asset | None:
        """
        Restituisce l'asset attualmente selezionato.
        """

        return self._current_asset
    # ---------------------------------------------------------

    def get_current_asset_path(self) -> str | None:
        """
        Restituisce il percorso completo dell'asset corrente.
        """

        asset = self.get_current_asset()

        if asset is None:
            return None

        project = self.get_project()

        if project is None:
            return None

        from pathlib import Path

        return str(
            Path(project.project_folder) / asset.relative_path
        )
    # ---------------------------------------------------------

    def clear_current_asset(self) -> None:
        """
        Deseleziona l'asset corrente.
        """

        self._current_asset = None

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