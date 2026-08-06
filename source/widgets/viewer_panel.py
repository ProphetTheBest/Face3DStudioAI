"""
==========================================================
Face3D Studio AI

Viewer Panel

Autore:
Marco Cantù

Versione:
0.5.0
==========================================================
"""

from source.ai.services.face_analysis_service import (
    FaceAnalysisService,
)

from source.controllers.project_controller import (
    ProjectController,
)

from source.models.assets.image_asset import (
    ImageAsset,
)

from source.widgets.base_panel import BasePanel
from source.widgets.image_viewer import ImageViewer


class ViewerPanel(BasePanel):

    def __init__(
        self,
        controller: ProjectController,
    ):

        super().__init__("VIEWER")

        self._controller = controller

        self.viewer = ImageViewer()

        self._analysis_service = FaceAnalysisService()

        self.add_content_widget(
            self.viewer
        )

    # ---------------------------------------------------------

    def show_current_asset(self) -> None:

        filename = self._controller.get_current_asset_path()

        if filename is None:

            self.viewer.clear()

            return

        asset = self._controller.get_current_asset()

        if not isinstance(asset, ImageAsset):

            self.viewer.clear()

            return

        #
        # Visualizza immagine
        #

        self.viewer.show_image(
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

        self.viewer.show_faces(

            [
                face.detection

                for face in asset.faces
            ]

        )

        #
        # Mesh
        #

        if asset.faces:

            face = asset.faces[0]

            #
            # Wireframe
            #

            if face.mesh is not None:

                self.viewer.show_face_mesh(
                    face.mesh
                )

            #
            # Landmark (temporaneo)
            #

            self.viewer.show_landmarks(
                face.landmarks
            )