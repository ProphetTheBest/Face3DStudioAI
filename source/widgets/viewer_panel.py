"""
==========================================================
Face3D Studio AI

Viewer Panel

Autore:
Marco Cantù

Versione:
0.3.0
==========================================================
"""

from source.controllers.project_controller import ProjectController
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

        self.add_content_widget(self.viewer)

    # ---------------------------------------------------------

    def show_current_asset(self) -> None:

        filename = self._controller.get_current_asset_path()

        if filename is None:

            self.viewer.clear()

            return

        self.viewer.show_image(filename)