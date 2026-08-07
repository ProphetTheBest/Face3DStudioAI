"""
==========================================================
Face3D Studio AI

Mesh Viewer

Autore:
Marco Cantù

Versione:
2.0.0
==========================================================
"""

import numpy as np

import pyqtgraph.opengl as gl

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)

from source.models.face_mesh import FaceMesh


class MeshViewer(QWidget):

    MODE_POINTS = 0
    MODE_WIREFRAME = 1
    MODE_MESH = 2

    # ---------------------------------------------------------

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(parent)

        #
        # Layout
        #

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        #
        # View OpenGL
        #

        self._view = gl.GLViewWidget()

        layout.addWidget(
            self._view
        )

        #
        # Camera
        #

        self._view.setCameraPosition(
            distance=2.0,
            elevation=0,
            azimuth=0,
        )

        #
        # Grid
        #

        self._grid = gl.GLGridItem()

        self._grid.scale(
            0.1,
            0.1,
            0.1,
        )

        self._view.addItem(
            self._grid
        )

        #
        # Modalità rendering
        #

        self._render_mode = self.MODE_MESH

        #
        # Oggetti OpenGL
        #

        self._points_item = None

        self._mesh_item = None

        self._wireframe_item = None

        #
        # Cache mesh
        #

        self._mesh = None

    # ---------------------------------------------------------

    def set_render_mode(
        self,
        mode: int,
    ):

        self._render_mode = mode

        if self._mesh is not None:

            self.show_mesh(
                self._mesh
            )

    # ---------------------------------------------------------

    def clear(self):

        if self._points_item is not None:

            self._view.removeItem(
                self._points_item
            )

            self._points_item = None

        if self._mesh_item is not None:

            self._view.removeItem(
                self._mesh_item
            )

            self._mesh_item = None

        if self._wireframe_item is not None:

            self._view.removeItem(
                self._wireframe_item
            )

            self._wireframe_item = None

    # ---------------------------------------------------------

    def show_mesh(
        self,
        mesh: FaceMesh,
    ):

        self.clear()

        if mesh is None:

            return

        self._mesh = mesh

        #
        # Conversione vertici
        #

        vertices = np.array(

            [

                [
                    v.x,
                    v.y,
                    v.z,
                ]

                for v in mesh.vertices

            ],

            dtype=np.float32,

        )

        #
        # Triangoli
        #

        faces = np.array(

            [

                [
                    t.a,
                    t.b,
                    t.c,
                ]

                for t in mesh.triangles

            ],

            dtype=np.int32,

        )

        #
        # POINT CLOUD
        #

        if self._render_mode == self.MODE_POINTS:

            self._points_item = gl.GLScatterPlotItem(

                pos=vertices,

                size=5,

                color=(1.0, 1.0, 0.0, 1.0),

                pxMode=True,

            )

            self._view.addItem(
                self._points_item
            )

            return

        #
        # MESH TRIANGOLATA
        #

        meshdata = gl.MeshData(

            vertexes=vertices,

            faces=faces,

        )

        #
        # Mesh piena
        #

        if self._render_mode == self.MODE_MESH:

            self._mesh_item = gl.GLMeshItem(

                meshdata=meshdata,

                smooth=False,

                drawFaces=True,

                drawEdges=False,

                shader="shaded",

            )

            self._view.addItem(
                self._mesh_item
            )

            return

        #
        # Wireframe
        #

        if self._render_mode == self.MODE_WIREFRAME:

            self._wireframe_item = gl.GLMeshItem(

                meshdata=meshdata,

                smooth=False,

                drawFaces=False,

                drawEdges=True,

            )

            self._view.addItem(
                self._wireframe_item
            )

            return
		