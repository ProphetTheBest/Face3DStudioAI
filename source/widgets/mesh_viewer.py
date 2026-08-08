"""
==========================================================
Face3D Studio AI

Mesh Viewer

Autore:
Marco Cantù

Versione:
3.0.0
==========================================================
"""

import numpy as np

import pyqtgraph.opengl as gl

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QToolButton,
    QLabel,
    QButtonGroup,
)

from source.models.face_mesh import FaceMesh


class MeshViewer(QWidget):

    MODE_POINTS = 0
    MODE_WIREFRAME = 1
    MODE_MESH = 2

    # ---------------------------------------------------------
    # Construction
    # ---------------------------------------------------------

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(parent)

        #
        # Widgets
        #

        self._create_widgets()

        #
        # Toolbar configuration
        #

        self._configure_toolbar_buttons()


        #
        # OpenGL Viewer
        #

        self._create_gl_view()

        #
        # Layout
        #

        self._create_layout()

        #
        # Rendering mode
        #

        self._render_mode = self.MODE_MESH

        #
        # OpenGL objects
        #

        self._points_item = None

        self._mesh_item = None

        self._wireframe_item = None

        #
        # Mesh cache
        #

        self._mesh = None
        #
        # Signals
        #

        self._connect_signals()
    # ---------------------------------------------------------
    # Widgets
    # ---------------------------------------------------------

    def _create_widgets(self):

        #
        # Camera toolbar
        #

        self._btn_front = QToolButton()
        self._btn_front.setText("Front")

        self._btn_left = QToolButton()
        self._btn_left.setText("Left")

        self._btn_right = QToolButton()
        self._btn_right.setText("Right")

        self._btn_top = QToolButton()
        self._btn_top.setText("Top")

        self._btn_iso = QToolButton()
        self._btn_iso.setText("Iso")

        self._btn_reset = QToolButton()
        self._btn_reset.setText("Reset")

        #
        # Render toolbar
        #

        self._btn_points = QToolButton()
        self._btn_points.setText("Points")

        self._btn_wire = QToolButton()
        self._btn_wire.setText("Wire")

        self._btn_mesh = QToolButton()
        self._btn_mesh.setText("Mesh")

    # ---------------------------------------------------------
    # Toolbar
    # ---------------------------------------------------------

    def _configure_toolbar_buttons(self):

        buttons = [

            self._btn_front,
            self._btn_left,
            self._btn_right,
            self._btn_top,
            self._btn_iso,
            self._btn_reset,

            self._btn_points,
            self._btn_wire,
            self._btn_mesh,

        ]

        for button in buttons:

            button.setMinimumWidth(70)

            button.setCheckable(True)

            if button is self._btn_reset:
                button.setCheckable(False)

            button.setAutoExclusive(False)	

            #
            # View buttons
            #

            self._view_group = QButtonGroup(self)

            self._view_group.setExclusive(True)

            self._view_group.addButton(self._btn_front)
            self._view_group.addButton(self._btn_left)
            self._view_group.addButton(self._btn_right)
            self._view_group.addButton(self._btn_top)
            self._view_group.addButton(self._btn_iso)

            #
            # Render buttons
            #

            self._render_group = QButtonGroup(self)

            self._render_group.setExclusive(True)

            self._render_group.addButton(self._btn_points)
            self._render_group.addButton(self._btn_wire)
            self._render_group.addButton(self._btn_mesh)

            #
            # Default buttons
            #

            self._btn_iso.setChecked(True)

            self._btn_mesh.setChecked(True)            
    # ---------------------------------------------------------
    # Layout
    # ---------------------------------------------------------

    def _create_layout(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

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

        layout.addLayout(
            toolbar_view
        )

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

        layout.addLayout(
            toolbar_render
        )

        #
        # OpenGL Viewer
        #

        layout.addWidget(
            self._view
        )

    # ---------------------------------------------------------
    # OpenGL
    # ---------------------------------------------------------

    def _create_gl_view(self):

        #
        # Viewer
        #

        self._view = gl.GLViewWidget()

        self._view.setBackgroundColor("k")

        self._view.opts["fov"] = 45

        #
        # Camera
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
        # Axis
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

    # ---------------------------------------------------------
    # Signals
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
    # Rendering
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
    # Utilities
    # ---------------------------------------------------------

    def clear(self):

        #
        # Point Cloud
        #
        if self._points_item is not None:

            self._view.removeItem(
                self._points_item
            )

            self._points_item = None

        #
        # Solid Mesh
        #
        if self._mesh_item is not None:

            self._view.removeItem(
                self._mesh_item
            )

            self._mesh_item = None

        #
        # Wireframe
        #
        if self._wireframe_item is not None:

            self._view.removeItem(
                self._wireframe_item
            )

            self._wireframe_item = None

    # ---------------------------------------------------------
    # Camera
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
    # Rendering
    # ---------------------------------------------------------

    def show_mesh(
        self,
        mesh: FaceMesh,
    ):

        self.clear()

        if mesh is None:
            return

        #
        # Cache
        #

        self._mesh = mesh

        #
        # Vertices
        #

        vertices = np.array(
            [
                [
                    vertex.x,
                    vertex.y,
                    vertex.z,
                ]
                for vertex in mesh.vertices
            ],
            dtype=np.float32,
        )

        #
        # Triangles
        #

        faces = np.array(
            [
                [
                    triangle.a,
                    triangle.b,
                    triangle.c,
                ]
                for triangle in mesh.triangles
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
        # MeshData
        #

        mesh_data = gl.MeshData(
            vertexes=vertices,
            faces=faces,
        )

        #
        # SOLID MESH
        #

        if self._render_mode == self.MODE_MESH:

            self._mesh_item = gl.GLMeshItem(
                meshdata=mesh_data,
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
        # WIREFRAME
        #

        if self._render_mode == self.MODE_WIREFRAME:

            self._wireframe_item = gl.GLMeshItem(
                meshdata=mesh_data,
                smooth=False,
                drawFaces=False,
                drawEdges=True,
            )

            self._view.addItem(
                self._wireframe_item
            )

            return

            #
            # Unknown rendering mode
            #

            raise ValueError(
                f"Unsupported render mode: {self._render_mode}"
            )

			