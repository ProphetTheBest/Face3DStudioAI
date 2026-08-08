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
    QHBoxLayout,
    QPushButton,
    QLabel,
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

        self._create_widgets()

        self._create_layout()

        #
        # Layout
        #

        # layout = QVBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        #
        # Toolbar - View
        #

        # toolbar_view = QHBoxLayout()

        toolbar_view.addWidget(
            QLabel("View:")
        )

        # self._btn_front = QPushButton("Front")
        # self._btn_left = QPushButton("Left")
        # self._btn_right = QPushButton("Right")
        # self._btn_top = QPushButton("Top")
        # self._btn_iso = QPushButton("Iso")
        # self._btn_reset = QPushButton("Reset")

        toolbar_view.addWidget(self._btn_front)
        toolbar_view.addWidget(self._btn_left)
        toolbar_view.addWidget(self._btn_right)
        toolbar_view.addWidget(self._btn_top)
        toolbar_view.addWidget(self._btn_iso)
        toolbar_view.addWidget(self._btn_reset)

        toolbar_view.addStretch()

        layout.addLayout(toolbar_view)

        #
        # Toolbar - Render
        #

        # toolbar_render = QHBoxLayout()

        toolbar_render.addWidget(
            QLabel("Render:")
        )

        self._btn_points = QPushButton("Points")
        self._btn_wire = QPushButton("Wire")
        self._btn_mesh = QPushButton("Mesh")

        toolbar_render.addWidget(self._btn_points)
        toolbar_render.addWidget(self._btn_wire)
        toolbar_render.addWidget(self._btn_mesh)

        toolbar_render.addStretch()

        layout.addLayout(toolbar_render)

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

        #

        self.reset_camera()

        #
        # Grid
        #

        self._grid = gl.GLGridItem()

        self._grid.setSize(
            2,
            2,
        )

        self._grid.setSpacing(
            0.1,
            0.1,
        )

        self._view.addItem(
            self._grid
        )

        #
        # Assi XYZ
        #

        self._axis = gl.GLAxisItem()

        self._axis.setSize(
            0.5,
            0.5,
            0.5,
        )

        self._view.addItem(
            self._axis
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

        #
        # Signals
        #

        self._connect_signals()
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

    def _create_widgets(self):

        #
        # Toolbar - View
        #

        self._btn_front = QPushButton("Front")
        self._btn_left = QPushButton("Left")
        self._btn_right = QPushButton("Right")
        self._btn_top = QPushButton("Top")
        self._btn_iso = QPushButton("Iso")
        self._btn_reset = QPushButton("Reset")

        #
        # Toolbar - Render
        #

        self._btn_points = QPushButton("Points")
        self._btn_wire = QPushButton("Wire")
        self._btn_mesh = QPushButton("Mesh")

    # ---------------------------------------------------------

    def _create_layout(self):

        layout = QVBoxLayout(self)

        #
        # Toolbar - View
        #

        toolbar_view = QHBoxLayout()

        toolbar_view.addWidget(
            QLabel("View:")
        )

        toolbar_view.addWidget(self._btn_front)
        toolbar_view.addWidget(self._btn_left)
        toolbar_view.addWidget(self._btn_right)
        toolbar_view.addWidget(self._btn_top)
        toolbar_view.addWidget(self._btn_iso)
        toolbar_view.addWidget(self._btn_reset)

        toolbar_view.addStretch()

        layout.addLayout(toolbar_view)

        #
        # Toolbar - Render
        #

        toolbar_render = QHBoxLayout()

        toolbar_render.addWidget(
            QLabel("Render:")
        )

        toolbar_render.addWidget(self._btn_points)
        toolbar_render.addWidget(self._btn_wire)
        toolbar_render.addWidget(self._btn_mesh)

        toolbar_render.addStretch()

        layout.addLayout(toolbar_render)

        #
        # OpenGL Viewer
        #

        layout.addWidget(
            self._view
        )

    # ---------------------------------------------------------

    def _connect_signals(self):

        #
        # Camera
        #

        self._btn_front.clicked.connect(
            self.set_front_view
        )

        self._btn_left.clicked.connect(
            self.set_left_view
        )

        self._btn_right.clicked.connect(
            self.set_right_view
        )

        self._btn_top.clicked.connect(
            self.set_top_view
        )

        self._btn_iso.clicked.connect(
            self.set_isometric_view
        )

        self._btn_reset.clicked.connect(
            self.reset_camera
        )

        #
        # Rendering
        #

        self._btn_points.clicked.connect(
            lambda: self.set_render_mode(
                self.MODE_POINTS
            )
        )

        self._btn_wire.clicked.connect(
            lambda: self.set_render_mode(
                self.MODE_WIREFRAME
            )
        )

        self._btn_mesh.clicked.connect(
            lambda: self.set_render_mode(
                self.MODE_MESH
            )
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

    def reset_camera(self):

        self.set_isometric_view()
        
    # ---------------------------------------------------------


    def set_front_view(self):

        self._view.setCameraPosition(
            distance=2.0,
            elevation=0,
            azimuth=0,
        )

    # ---------------------------------------------------------

    def set_left_view(self):

        self._view.setCameraPosition(
            distance=2.0,
            elevation=0,
            azimuth=90,
        )

    # ---------------------------------------------------------

    def set_right_view(self):

        self._view.setCameraPosition(
            distance=2.0,
            elevation=0,
            azimuth=-90,
        )

    # ---------------------------------------------------------

    def set_top_view(self):

        self._view.setCameraPosition(
            distance=2.0,
            elevation=90,
            azimuth=0,
        )

    # ---------------------------------------------------------

    def set_isometric_view(self):

        self._view.setCameraPosition(
            distance=2.0,
            elevation=30,
            azimuth=45,
        )

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
		