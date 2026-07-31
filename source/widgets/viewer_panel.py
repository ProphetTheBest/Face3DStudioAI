"""
==========================================================
Face3D Studio AI

Viewer Panel

Autore:
Marco Cantù

Versione:
0.2.0
==========================================================
"""

from source.widgets.base_panel import BasePanel
from source.widgets.image_viewer import ImageViewer


class ViewerPanel(BasePanel):

    def __init__(self):

        super().__init__("VIEWER")

        self.viewer = ImageViewer()

        self.add_content_widget(self.viewer)

    # ---------------------------------------------------------

    def show_photo(self, filename: str):

        self.viewer.show_image(filename)