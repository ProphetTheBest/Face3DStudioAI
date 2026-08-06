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
0.0.9
==========================================================
"""

from PySide6.QtGui import QAction

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QMainWindow,
    QMessageBox,
)

from source.controllers.application_controller import ApplicationController
from source.dialogs.new_project_dialog import NewProjectDialog
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

        file_menu = menu_bar.addMenu("&File")

        self.action_new_project = QAction("New Project...", self)
        self.action_open_project = QAction("Open Project...", self)
        self.action_import_photos = QAction("Import Photos...", self)
        self.action_save_project = QAction("Save", self)
        self.action_save_project_as = QAction("Save As...", self)
        self.action_exit = QAction("Exit", self)

        file_menu.addAction(self.action_new_project)
        file_menu.addAction(self.action_open_project)

        file_menu.addSeparator()

        file_menu.addAction(self.action_import_photos)

        file_menu.addSeparator()

        file_menu.addAction(self.action_save_project)
        file_menu.addAction(self.action_save_project_as)

        file_menu.addSeparator()

        file_menu.addAction(self.action_exit)

        self.action_new_project.triggered.connect(
            self._on_new_project
        )

        self.action_open_project.triggered.connect(
            self._on_open_project
        )

        self.action_import_photos.triggered.connect(
            self._on_import_photos
        )

        self.action_exit.triggered.connect(
            self.close
        )

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

        dialog = NewProjectDialog(self)

        if dialog.exec() != QDialog.Accepted:
            return

        project_name = dialog.project_name()
        project_folder = dialog.project_folder()

        project_controller = (
            self.app_controller.get_project_controller()
        )

        try:

            project_controller.create_project(
                project_name,
                project_folder,
            )

            self.central_widget.project_panel.refresh()

            self.central_widget.viewer_panel.image_viewer.clear()
            self.central_widget.viewer_panel.mesh_viewer.clear()

            self.status_bar.showMessage(
                "Project created",
                3000
            )

            QMessageBox.information(
                self,
                "Face3D Studio AI",
                f"Project created successfully.\n\n{project_folder}"
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )

            raise

    # -----------------------------------------------------

    def _on_open_project(self) -> None:
        """
        Gestisce il comando File -> Open Project.
        """

        project_folder = QFileDialog.getExistingDirectory(
            self,
            "Open Project"
        )

        if not project_folder:
            return

        project_controller = (
            self.app_controller.get_project_controller()
        )

        try:

            project_controller.open_project(
                project_folder
            )

            self.central_widget.project_panel.refresh()

            self.central_widget.viewer_panel.image_viewer.clear()
            self.central_widget.viewer_panel.mesh_viewer.clear()

            QMessageBox.information(
                self,
                "Face3D Studio AI",
                "Project loaded successfully."
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )

            raise

    # -----------------------------------------------------

    def _on_import_photos(self) -> None:
        """
        Gestisce il comando File -> Import Photos.
        """

        project_controller = (
            self.app_controller.get_project_controller()
        )

        if project_controller.get_project() is None:

            QMessageBox.warning(
                self,
                "Face3D Studio AI",
                "Create or open a project before importing photos."
            )

            return

        file_list, _ = QFileDialog.getOpenFileNames(
            self,
            "Import Photos",
            "",
            "Images (*.jpg *.jpeg *.png *.bmp *.tif *.tiff)"
        )

        if not file_list:
            return

        try:

            project_controller.import_images(file_list)

            self.central_widget.project_panel.refresh()

            self.status_bar.showMessage(
                f"{len(file_list)} image(s) imported.",
                3000
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                str(e)
            )

            raise