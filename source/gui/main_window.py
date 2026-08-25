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
0.0.11
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
from source.controllers.diagnostics.diagnostics_controller import (
    DiagnosticsController,
)
from source.dialogs.new_project_dialog import NewProjectDialog
from source.dialogs.new_reconstruction_dialog import NewReconstructionDialog
from source.dialogs.vertex_mapper_dialog import (
    VertexMapperDialog,
)

from source.models.mapping.canonical_mapping import (
    CanonicalMapping,
)
from source.widgets.central_widget import CentralWidget
from source.services.exporting.face_export_service import (
    FaceExportService,
)

class MainWindow(QMainWindow):
    """
    Finestra principale dell'applicazione.
    """

    def __init__(self, app_controller: ApplicationController):

        super().__init__()

        self.app_controller = app_controller

        self._vertex_mapper_dialog = None

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
        self.action_new_reconstruction = QAction("New Reconstruction...", self)
        self.action_open_project = QAction("Open Project...", self)
        self.action_import_photos = QAction("Import Photos...", self)
        self.action_export_obj = QAction("Export OBJ...", self)

        self.action_face_diagnostics = QAction(
            "Face Diagnostics...",
            self
        )

        self.action_vertex_mapper = QAction(
            "Vertex Mapper...",
            self
        )

        self.action_save_project = QAction("Save", self)
        self.action_save_project_as = QAction("Save As...", self)
        self.action_exit = QAction("Exit", self)

        file_menu.addAction(self.action_new_project)
        file_menu.addAction(self.action_new_reconstruction)
        file_menu.addAction(self.action_open_project)

        file_menu.addSeparator()

        file_menu.addAction(self.action_import_photos)

        file_menu.addAction(self.action_export_obj)

        file_menu.addSeparator()

        file_menu.addAction(self.action_save_project)
        file_menu.addAction(self.action_save_project_as)

        file_menu.addSeparator()

        file_menu.addAction(self.action_exit)

        self.action_new_project.triggered.connect(
            self._on_new_project
        )

        self.action_new_reconstruction.triggered.connect(
            self._on_new_reconstruction
        )

        self.action_open_project.triggered.connect(
            self._on_open_project
        )

        self.action_import_photos.triggered.connect(
            self._on_import_photos
        )

        self.action_export_obj.triggered.connect(
            self._on_export_obj
        )

        self.action_face_diagnostics.triggered.connect(
            self._on_face_diagnostics
        )

        self.action_vertex_mapper.triggered.connect(
            self._on_vertex_mapper
        )

        self.action_save_project.triggered.connect(
            self._on_save_project
        )

        self.action_exit.triggered.connect(
            self.close
        )

        menu_bar.addMenu("&Edit")
        menu_bar.addMenu("&View")
        menu_bar.addMenu("&AI")

        tools_menu = menu_bar.addMenu("&Tools")

        tools_menu.addAction(
            self.action_face_diagnostics
        )

        tools_menu.addAction(
            self.action_vertex_mapper
        )

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

    def _on_save_project(self) -> None:
        """
        Gestisce il comando File -> Save.
        """

        project_controller = (
            self.app_controller.get_project_controller()
        )

        try:
            project_controller.save_project()

            self.status_bar.showMessage(
                "Project saved successfully.",
                3000,
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Project",
                str(e),
            )

            raise

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

            self._reset_vertex_mapper_dialog()

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

    def _on_new_reconstruction(self) -> None:
        """
        Crea una nuova elaborazione/Subject nel progetto corrente.
        La Canonical viene scelta dalla Canonical Asset Library e
        appartiene alla singola elaborazione, non al Project globale.
        """

        project_controller = (
            self.app_controller.get_project_controller()
        )

        project = project_controller.get_project()

        if project is None:
            QMessageBox.warning(
                self,
                "New Reconstruction",
                "Create or open a project before creating a reconstruction.",
            )
            return

        if not project.assets:
            QMessageBox.warning(
                self,
                "New Reconstruction",
                "Import at least one photo before creating a reconstruction.",
            )
            return

        dialog = NewReconstructionDialog(
            project,
            self,
        )

        if dialog.exec() != QDialog.Accepted:
            return

        try:
            subject = project_controller.create_reconstruction(
                dialog.subject_name(),
                dialog.source_asset_id(),
                dialog.canonical_asset_id(),
                dialog.canonical_asset_type(),
                dialog.canonical_asset_version(),
            )

            self._reset_vertex_mapper_dialog()

            self.central_widget.project_panel.refresh()

            # Il Controller ha impostato Subject e fotografia correnti.
            # Aggiorniamo immediatamente i pannelli per mantenere il
            # comportamento precedente dopo la creazione della
            # Reconstruction.
            self.central_widget.viewer_panel.show_current_asset()
            self.central_widget.properties_panel.show_asset(
                project_controller.get_current_asset()
            )

            self.status_bar.showMessage(
                f"Reconstruction '{subject.name}' created.",
                3000,
            )

            QMessageBox.information(
                self,
                "New Reconstruction",
                (
                    f"Reconstruction created successfully.\n\n"
                    f"Subject: {subject.name}\n"
                    f"Canonical: {subject.canonical_asset_id}"
                ),
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "New Reconstruction",
                str(e),
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

            self._reset_vertex_mapper_dialog()

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
    # -----------------------------------------------------

    def _on_export_obj(self) -> None:
        """
        Gestisce il comando File -> Export OBJ.
        """

        project_controller = (
            self.app_controller.get_project_controller()
        )

        face = project_controller.get_current_face()

        if face is None:

            QMessageBox.warning(
                self,
                "Export OBJ",
                "No face selected."
            )

            return

        if face.mesh is None:

            QMessageBox.warning(
                self,
                "Export OBJ",
                "The selected face has no mesh."
            )

            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export OBJ",
            "face.obj",
            "Wavefront OBJ (*.obj)"
        )

        if not filename:
            return

        try:

            project_controller.export_current_face(
                filename,
            )

            self.status_bar.showMessage(
                "OBJ exported successfully.",
                3000
            )

            QMessageBox.information(
                self,
                "Export OBJ",
                "OBJ exported successfully."
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Export OBJ",
                str(e)
            )

            raise

    # -----------------------------------------------------

    def _on_face_diagnostics(self) -> None:
        """
        Gestisce il comando Tools -> Face Diagnostics.
        """

        project_controller = (
            self.app_controller.get_project_controller()
        )

        face = project_controller.get_current_face()

        DiagnosticsController.show(
            face,
            self,
        )       

    # -----------------------------------------------------

    def _get_or_create_canonical_mapping(
        self,
    ) -> CanonicalMapping | None:
        """
        Restituisce il Canonical Mapping del progetto corrente.

        Se il progetto non possiede ancora un mapping, lo crea
        utilizzando l'identità della Canonical Mesh attualmente
        utilizzata dal Vertex Mapper.

        In questa fase il Vertex Mapper lavora sul template
        MakeHuman male1591.
        """

        project_controller = (
            self.app_controller.get_project_controller()
        )

        project = project_controller.get_project()

        if project is None:
            return None

        if project.has_canonical_mapping():
            return project.canonical_mapping

        canonical_mapping = CanonicalMapping(
            mapping_version="1.0",
            canonical_mesh_id="makehuman_male1591_head",
            canonical_mesh_version="1.0",
            template_id="male1591",
            template_version="1.0",
        )

        project.set_canonical_mapping(
            canonical_mapping
        )

        return canonical_mapping

    # -----------------------------------------------------

    def _reset_vertex_mapper_dialog(
        self,
    ) -> None:
        """
        Chiude e rimuove l'istanza corrente del Vertex Mapper.

        Viene utilizzato quando cambia il progetto, in modo
        da evitare che il dialog continui a utilizzare il
        Canonical Mapping del progetto precedente.
        """

        if self._vertex_mapper_dialog is not None:

            self._vertex_mapper_dialog.close()

            self._vertex_mapper_dialog = None

    # -----------------------------------------------------

    def _on_vertex_mapper(self) -> None:
        """
        Apre il Vertex Mapper utilizzando il Canonical Mapping
        appartenente al progetto corrente.

        Se il progetto non possiede ancora un Canonical Mapping,
        questo viene creato al primo accesso al Vertex Mapper.

        Il dialog viene riutilizzato finché rimane aperto lo
        stesso progetto.
        """

        project_controller = (
            self.app_controller.get_project_controller()
        )

        current_subject = project_controller.get_current_subject()

        if current_subject is not None:
            canonical_asset = project_controller.get_canonical_asset()
            canonical_mapping = (
                canonical_asset.canonical_mapping
                if canonical_asset is not None
                else None
            )
        else:
            canonical_mapping = (
                self._get_or_create_canonical_mapping()
            )

        if canonical_mapping is None:

            QMessageBox.warning(
                self,
                "Vertex Mapper",
                "Create or open a project before opening "
                "the Vertex Mapper.",
            )

            return

        if self._vertex_mapper_dialog is None:

            self._vertex_mapper_dialog = (
                VertexMapperDialog(
                    mapping_collection=canonical_mapping,
                    controller=project_controller,
                    parent=self,
                )
            )

        #
        # Riutilizziamo sempre la stessa istanza finché
        # il progetto corrente non cambia.
        #

        self._vertex_mapper_dialog.show()

        self._vertex_mapper_dialog.raise_()

        self._vertex_mapper_dialog.activateWindow()

        #
        # Richiediamo un nuovo paint della viewport.
        #

        self._vertex_mapper_dialog._refresh_viewer_after_show()

    # -----------------------------------------------------
