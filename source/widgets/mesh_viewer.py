"""
==========================================================
Face3D Studio AI

Mesh Viewer

Autore:
Marco Cantù

Versione:
1.1.0
==========================================================
"""

import numpy as np
import pyqtgraph.opengl as gl

from PySide6.QtWidgets import QWidget, QVBoxLayout

from source.models.face_mesh import FaceMesh


class MeshViewer(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)

        self._view = gl.GLViewWidget()

        layout.addWidget(self._view)

        #
        # Camera
        #

        self._view.setCameraPosition(
            distance=2.0,
        )

        #
        # Griglia
        #

        grid = gl.GLGridItem()

        grid.scale(
            0.1,
            0.1,
            0.1,
        )

        self._view.addItem(grid)

        #
        # Point Cloud
        #

        self._points_item = None

    # ---------------------------------------------------------

    def clear(self):

        if self._points_item is not None:

            self._view.removeItem(
                self._points_item
            )

            self._points_item = None

    # ---------------------------------------------------------

    def show_mesh(
        self,
        mesh: FaceMesh,
    ):

        self.clear()

        if mesh is None:

            return

        points = np.array(
            [
                [
                    v.x,
                    v.y,
                    v.z,
                ]
                for v in mesh.vertices
            ],
            dtype=float,
        )

        self._points_item = gl.GLScatterPlotItem(

            pos=points,

            size=6,

            color=(1.0, 1.0, 0.0, 1.0),

            pxMode=True,

        )

        self._view.addItem(
            self._points_item
        )