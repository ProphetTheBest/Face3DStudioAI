"""
==========================================================
Face3D Studio AI

Application Controller

Gestisce i controller e i servizi condivisi
dell'intera applicazione.

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from source.controllers.project_controller import ProjectController
from source.services.project.project_manager import ProjectManager


class ApplicationController:
    """
    Controller principale dell'applicazione.

    Istanzia i servizi condivisi e i controller
    dell'intera applicazione.
    """

    def __init__(self) -> None:

        #
        # Services
        #

        self.project_manager = ProjectManager()

        #
        # Controllers
        #

        self.project_controller = ProjectController(
            self.project_manager
        )

    # ---------------------------------------------------------
    # Controllers
    # ---------------------------------------------------------

    def get_project_controller(self) -> ProjectController:

        return self.project_controller

    # ---------------------------------------------------------
    # Services
    # ---------------------------------------------------------

    def get_project_manager(self) -> ProjectManager:

        return self.project_manager