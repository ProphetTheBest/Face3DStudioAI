"""
==========================================================
Face3D Studio AI

Application Controller

Gestisce i controller condivisi
dell'intera applicazione.

Autore:
Marco Cantù

Versione:
0.1.0
==========================================================
"""

from source.controllers.project_controller import ProjectController


class ApplicationController:
    """
    Controller principale dell'applicazione.
    """

    def __init__(self) -> None:

        self.project_controller = ProjectController()

    # ---------------------------------------------------------

    def get_project_controller(self) -> ProjectController:
        """
        Restituisce il controller del progetto.
        """

        return self.project_controller