"""
==========================================================
Face3D Studio AI

Photo Manager

Gestisce l'importazione delle fotografie nel progetto.
==========================================================
"""

from pathlib import Path
import shutil

from source.models.photo import Photo
from source.services.project.project_constants import PHOTOS_FOLDER
from source.services.project.project_manager import ProjectManager


class PhotoManager:
    """
    Gestisce le fotografie del progetto.
    """

    def __init__(self, project_manager: ProjectManager):

        self._project_manager = project_manager

    # ---------------------------------------------------------
    # Import
    # ---------------------------------------------------------

    def import_photos(self, file_list: list[str]) -> None:
        """
        Importa una o più fotografie nel progetto corrente.
        """

        project = self._project_manager.current_project

        if project is None:
            raise RuntimeError("Nessun progetto aperto.")

        for source_filename in file_list:

            source_path = Path(source_filename)

            destination_path = (
                Path(project.project_folder)
                / PHOTOS_FOLDER
                / source_path.name
            )

            shutil.copy2(source_path, destination_path)

            photo = Photo(
                filename=source_path.name,
                relative_path=f"{PHOTOS_FOLDER}/{source_path.name}",
                file_size=destination_path.stat().st_size,
            )

            project.add_photo(photo)

        self._project_manager.save_project(
            project.project_folder
        )

    def import_photo(self, filename: str) -> None:
        """
        Importa una singola fotografia.

        Metodo di comodità che richiama import_photos().
        """
        self.import_photos([filename])        