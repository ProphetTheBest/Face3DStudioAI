"""
==========================================================
Face3D Studio AI

Project Loader

Responsabile del caricamento dei progetti.

Autore:
Marco Cantù

Versione:
0.1.0
==========================================================
"""

from __future__ import annotations

import json
from pathlib import Path

from source.models.project import Project
from source.models.photo import Photo

from source.services.project.project_constants import (
    PROJECT_FILE,
)

class ProjectLoader:
    """
    Carica un progetto dal disco.
    """

    def load(self, project_folder: str) -> Project:
        """
        Carica un progetto dalla cartella indicata.
        """

        project_folder = Path(project_folder)

        if not project_folder.exists():
            raise FileNotFoundError(
                f"Project folder not found:\n{project_folder}"
            )

        project_file = project_folder / PROJECT_FILE

        if not project_file.exists():
            raise FileNotFoundError(
                f"File not found:\n{project_file}"
            )

        with project_file.open(
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        #
        # Rimuove informazioni non appartenenti al modello
        #

        data.pop("format_version", None)

        #
        # Ricostruisce gli oggetti Photo
        #

        photos = [
            Photo.from_dict(photo_data)
            for photo_data in data.get("photos", [])
        ]

        data["photos"] = photos

        #
        # Crea il progetto
        #

        project = Project(**data)

        return project