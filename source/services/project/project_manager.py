"""
==========================================================
Face3D Studio AI

File:
project_manager.py

Descrizione:
Responsabile della gestione del ciclo di vita dei progetti.

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from source.models.project import Project
from source.services.project.project_loader import ProjectLoader
from source.services.project.project_saver import ProjectSaver


class ProjectManager:
    """
    Gestisce il ciclo di vita dei progetti.
    """

    def __init__(self) -> None:

        self._current_project: Optional[Project] = None

        self._project_saver = ProjectSaver()
        self._project_loader = ProjectLoader()

    # =====================================================
    # Proprietà
    # =====================================================

    @property
    def current_project(self) -> Optional[Project]:
        """
        Restituisce il progetto corrente.
        """
        return self._current_project

    # =====================================================
    # API Pubbliche
    # =====================================================

    def create_project(
        self,
        name: str,
        project_folder: str,
    ) -> Project:
        """
        Crea e salva un nuovo progetto.

        Parameters
        ----------
        name : str
            Nome del progetto.

        project_folder : str
            Cartella in cui salvare il progetto.

        Returns
        -------
        Project
            Progetto creato.
        """

        project = self.new_project(name)

        # Costruisce la cartella finale del progetto
        final_folder = Path(project_folder) / name

        self.save_project(str(final_folder))

        return project

    # -----------------------------------------------------

    def new_project(
        self,
        name: str = "Untitled",
    ) -> Project:
        """
        Crea un nuovo progetto in memoria.
        """

        project = Project(name=name)

        self._current_project = project

        return project

    # -----------------------------------------------------

    def save_project(
        self,
        project_folder: str,
    ) -> None:
        """
        Salva il progetto corrente.
        """

        if self._current_project is None:
            raise RuntimeError("Nessun progetto aperto.")

        folder = Path(project_folder)

        self._current_project.project_folder = str(folder)

        self._project_saver.save(
            self._current_project,
            str(folder),
        )

    # -----------------------------------------------------

    def open_project(
        self,
        project_folder: str,
    ) -> Project:
        """
        Apre un progetto esistente.
        """

        folder = Path(project_folder)

        project = self._project_loader.load(
            str(folder)
        )

        self._current_project = project

        return project

    # -----------------------------------------------------

    def close_project(self) -> None:
        """
        Chiude il progetto corrente.
        """

        self._current_project = None

    # -----------------------------------------------------

    def set_current_project(
        self,
        project: Project,
    ) -> None:
        """
        Imposta il progetto corrente.
        """

        self._current_project = project