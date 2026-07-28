"""
Project Manager di Face3D Studio AI.

Responsabile della gestione dei progetti.
"""

from __future__ import annotations

from typing import Optional

from source.models.project import Project
from source.services.project.project_saver import ProjectSaver


class ProjectManager:
    """
    Gestisce il ciclo di vita dei progetti.
    """

    def __init__(self) -> None:

        self._current_project: Optional[Project] = None
        self._project_saver = ProjectSaver()

    # ---------------------------------------------------------
    # Proprietà
    # ---------------------------------------------------------

    @property
    def current_project(self) -> Optional[Project]:
        """
        Restituisce il progetto corrente.
        """
        return self._current_project

    # ---------------------------------------------------------
    # Gestione progetto
    # ---------------------------------------------------------

    def new_project(self, name: str = "Untitled") -> Project:
        """
        Crea un nuovo progetto.
        """

        project = Project(name=name)

        self._current_project = project

        return project

    # ---------------------------------------------------------

    def save_project(self, project_folder: str) -> None:
        """
        Salva il progetto corrente.
        """

        if self._current_project is None:
            raise RuntimeError("Nessun progetto aperto.")

        self._project_saver.save(
            self._current_project,
            project_folder
        )

    # ---------------------------------------------------------

    def set_current_project(self, project: Project) -> None:

        self._current_project = project

    # ---------------------------------------------------------

    def close_project(self) -> None:

        self._current_project = None