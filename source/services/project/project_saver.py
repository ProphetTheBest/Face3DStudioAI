"""
==========================================================
Face3D Studio AI

Project Saver

Salva un progetto sul disco.

Autore:
Marco Cantù

Versione:
0.2.0
==========================================================
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

from source.models.project import Project
from source.services.project.project_serializer import ProjectSerializer

from source.services.project.project_constants import (
    CACHE_FOLDER,
    EXPORTS_FOLDER,
    FORMAT_VERSION,
    FRAMES_FOLDER,
    LANDMARKS_FOLDER,
    MESHES_FOLDER,
    PHOTOS_FOLDER,
    PROJECT_FILE,
    TEXTURES_FOLDER,
    VIDEOS_FOLDER,
)


class ProjectSaver:
    """
    Salva un progetto sul disco.
    """

    def save(self, project: Project, project_folder: str) -> None:
        """
        Crea la struttura del progetto e salva project.json.
        """

        root = Path(project_folder)

        # Cartella principale
        root.mkdir(parents=True, exist_ok=True)

        # Sottocartelle
        folders = [
            PHOTOS_FOLDER,
            VIDEOS_FOLDER,
            FRAMES_FOLDER,
            LANDMARKS_FOLDER,
            MESHES_FOLDER,
            TEXTURES_FOLDER,
            EXPORTS_FOLDER,
            CACHE_FOLDER,
        ]

        for folder in folders:
            (root / folder).mkdir(exist_ok=True)

        # Aggiorna il modello
        project.project_folder = str(root)
        project.modified = datetime.now().isoformat(timespec="seconds")

        # Metadata
        
        data = ProjectSerializer.to_dict(project)

        data["format_version"] = FORMAT_VERSION

        with open(root / PROJECT_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)