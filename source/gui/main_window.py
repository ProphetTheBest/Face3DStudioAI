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
0.0.5
==========================================================
"""

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QMessageBox,
)

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

        self.setWindowTitle("Face3D Studio AI")

        self.resize(1400, 900)

    # -----------------------------------------------------

    def _create_menu(self):

        menu_bar = self.menuBar()

        #
        # File
        #
        file_menu = menu_bar.addMenu("&File")

        self.action_new_project = QAction("New Project...", self)
        self.action_open_project = QAction("Open Project...", self)
        self.action_save_project = QAction("Save", self)
        self.action_save_project_as = QAction("Save As...", self)
        self.action_exit = QAction("Exit", self)

        file_menu.addAction(self.action_new_project)
        file_menu.addAction(self.action_open_project)

        file_menu.addSeparator()

        file_menu.addAction(self.action_save_project)
        file_menu.addAction(self.action_save_project_as)

        file_menu.addSeparator()

        file_menu.addAction(self.action_exit)

        #
        # Collegamenti
        #
        self.action_new_project.triggered.connect(
            self._on_new_project
        )

        self.action_exit.triggered.connect(
            self.close
        )

        #
        # Altri menu
        #
        menu_bar.addMenu("&Edit")
        menu_bar.addMenu("&View")
        menu_bar.addMenu("&AI")
        menu_bar.addMenu("&Tools")
        menu_bar.addMenu("&Help")

    # -----------------------------------------------------

    def _create_statusbar(self):

        self.status_bar = self.statusBar()

        self.status_bar.showMessage("Ready")

    # -----------------------------------------------------

    def _create_central_widget(self):

        self.central_widget = CentralWidget(
            self.app_controller
        )

        self.setCentralWidget(self.central_widget)

    # -----------------------------------------------------
    # Eventi
    # -----------------------------------------------------

    def _on_new_project(self) -> None:
        """
        Gestisce il comando File -> New Project.
        """

        project_name, ok = QInputDialog.getText(
            self,
            "New Project",
            "Project name:"
        )

        if not ok:
            return

        project_name = project_name.strip()

        if not project_name:
            QMessageBox.warning(
                self,
                "Face3D Studio AI",
                "Project name cannot be empty."
            )
            return

        #
        # Selezione cartella
        #
        parent_folder = QFileDialog.getExistingDirectory(
            self,
            "Select destination folder"
        )

        if not parent_folder:
            return

        #
        # Crea il progetto
        #
        self.app_controller.get_project_manager().new_project(project_name)

        #
        # Percorso finale
        #
        project_folder = (
            f"{parent_folder}/{project_name}.face3d"
        )

        #
        # Salvataggio
        #
        self.app_controller.get_project_manager().save_project(
            project_folder
        )

        QMessageBox.information(
            self,
            "Face3D Studio AI",
            "Project created successfully."
        )