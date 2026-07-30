"""
==========================================================
Face3D Studio AI

Application Controller

Gestisce i controller e i servizi condivisi
dell'intera applicazione.

Autore:
Marco Cantù

Versione:
0.5.0
==========================================================
"""

from source.controllers.photo_controller import PhotoController
from source.controllers.project_controller import ProjectController
from source.services.photo.photo_manager import PhotoManager
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

        self.photo_manager = PhotoManager(
            self.project_manager
        )

        #
        # Controllers
        #

        self.project_controller = ProjectController(
            self.project_manager
        )

        self.photo_controller = PhotoController(
            self.photo_manager
        )

    # ---------------------------------------------------------
    # Controllers
    # ---------------------------------------------------------

    def get_project_controller(self) -> ProjectController:
        """
        Restituisce il ProjectController.
        """
        return self.project_controller

    # ---------------------------------------------------------

    def get_photo_controller(self) -> PhotoController:
        """
        Restituisce il PhotoController.
        """
        return self.photo_controller

    # ---------------------------------------------------------
    # Services
    # ---------------------------------------------------------
    #
    # Utilizzati internamente dall'applicazione.
    # La GUI deve accedere esclusivamente ai Controller.
    #

    def get_project_manager(self) -> ProjectManager:
        """
        Restituisce il ProjectManager.
        """
        return self.project_manager

    # ---------------------------------------------------------

    def get_photo_manager(self) -> PhotoManager:
        """
        Restituisce il PhotoManager.
        """
        return self.photo_manager