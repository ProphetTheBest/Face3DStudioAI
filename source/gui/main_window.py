"""
==========================================================
Face3D Studio AI

File:
main_window.py

Descrizione:
Finestra principale dell'applicazione.

Autore:
Marco Cantù

Versione:
0.0.3
==========================================================
"""

from PySide6.QtWidgets import QMainWindow

from source.controllers.application_controller import ApplicationController
from source.widgets.central_widget import CentralWidget

class MainWindow(QMainWindow):
    """
    Finestra principale dell'applicazione.
    """

    def __init__(self, app_controller: ApplicationController):

        super().__init__()

        self.app_controller = app_controller

        self._create_window()
        self._create_menu()
        self._create_statusbar()
        self._create_central_widget()

    # -----------------------------------------------------

    def _create_window(self):
        """Configura la finestra principale."""

        self.setWindowTitle("Face3D Studio AI")

        self.resize(1400, 900)

    # -----------------------------------------------------

    def _create_menu(self):
        """Crea la barra dei menu."""

        menu = self.menuBar()

        menu.addMenu("File")
        menu.addMenu("Edit")
        menu.addMenu("View")
        menu.addMenu("AI")
        menu.addMenu("Tools")
        menu.addMenu("Help")

    # -----------------------------------------------------

    def _create_statusbar(self):
        """Crea la barra di stato."""

        self.status_bar = self.statusBar()

        self.status_bar.showMessage("Ready")

    # -----------------------------------------------------

    def _create_central_widget(self):
        """Crea il widget centrale."""

        self.central_widget = CentralWidget(
            self.app_controller
        )

        self.setCentralWidget(self.central_widget)