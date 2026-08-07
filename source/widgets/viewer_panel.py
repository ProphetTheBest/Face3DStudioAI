"""
==========================================================
Face3D Studio AI

Viewer Panel

Autore:
Marco Cantù

Versione:
0.6.0
==========================================================
"""

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QSplitter,
    QWidget,
    QVBoxLayout,
)

from source.ai.services.face_analysis_service import (
    FaceAnalysisService,
)

from source.controllers.project_controller import (
    ProjectController,
)

from source.models import face
from source.models.assets.image_asset import (
    ImageAsset,
)

from source.widgets.base_panel import BasePanel

from source.widgets.image_viewer import ImageViewer

from source.widgets.mesh_viewer import MeshViewer


class ViewerPanel(BasePanel):

    def __init__(
        self,
        controller: ProjectController,
    ):

        super().__init__("VIEWER")

        self._controller = controller

        self._analysis_service = FaceAnalysisService()

        #
        # Viewer
        #

        self.image_viewer = ImageViewer()

        self.mesh_viewer = MeshViewer()

        #
        # Splitter verticale
        #

        splitter = QSplitter(Qt.Vertical)

        splitter.addWidget(
            self.image_viewer
        )

        splitter.addWidget(
            self.mesh_viewer
        )

        splitter.setStretchFactor(0, 3)

        splitter.setStretchFactor(1, 2)

        splitter.setSizes([500, 300])        

        container = QWidget()

        layout = QVBoxLayout(container)

        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(splitter)

        self.add_content_widget(container)
    # ---------------------------------------------------------

    # ---------------------------------------------------------

    def show_current_asset(self) -> None:

        filename = self._controller.get_current_asset_path()

        if filename is None:

            self.image_viewer.clear()

            self.mesh_viewer.clear()

            return

        asset = self._controller.get_current_asset()

        if not isinstance(asset, ImageAsset):

            self.image_viewer.clear()

            self.mesh_viewer.clear()

            return

        #
        # Visualizza immagine
        #

        self.image_viewer.show_image(
            filename
        )

        #
        # Analisi AI
        #

        self._analysis_service.analyze(
            asset,
            filename,
        )

        #
        # Bounding Box
        #

        self.image_viewer.show_faces(

            [
                face.detection

                for face in asset.faces
            ]

        )

        #
        # Primo volto
        #

        if asset.faces:

            face = asset.faces[0]

            #
            # Wireframe 2D
            #

            if face.mesh is not None:

                self.image_viewer.show_face_mesh(
                    face.landmarks,
                    face.mesh.edges,
                )

                #
                # Viewer 3D
                #

                self.mesh_viewer.show_mesh(
                    face.mesh
                )

            #
            # Landmark
            #

            self.image_viewer.show_landmarks(
                face.landmarks
            )

        else:

            self.mesh_viewer.clear()