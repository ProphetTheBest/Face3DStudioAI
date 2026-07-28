"""
==========================================================
Face3D Studio AI

Application Controller

Gestisce i controller e i servizi condivisi
dell'intera applicazione.

Autore:
Marco Cantù

Versione:
0.2.0
==========================================================
"""

from source.controllers.project_controller import ProjectController
from source.services.project.project_manager import ProjectManager


class ApplicationController:
    """
    Controller principale dell'applicazione.

    Espone controller e servizi condivisi
    a tutta l'applicazione.
    """

    def __init__(self) -> None:

        # Controller
        self.project_controller = ProjectController()

        # Services
        self.project_manager = ProjectManager()

    # ---------------------------------------------------------
    # Controller
    # ---------------------------------------------------------

    def get_project_controller(self) -> ProjectController:
        """
        Restituisce il ProjectController.
        """
        return self.project_controller

    # ---------------------------------------------------------
    # Services
    # ---------------------------------------------------------

    def get_project_manager(self) -> ProjectManager:
        """
        Restituisce il ProjectManager.
        """
        return self.project_manager