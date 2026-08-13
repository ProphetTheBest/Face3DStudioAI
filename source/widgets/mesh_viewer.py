"""
==========================================================
Face3D Studio AI

Mesh Viewer

Autore:
Marco Cantù

Versione:
3.3.0
==========================================================
"""

import numpy as np
import pyqtgraph.opengl as gl
from OpenGL.GL import (
    GL_ALPHA_TEST,
    GL_BLEND,
    GL_CULL_FACE,
    GL_DEPTH_TEST,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_SRC_ALPHA,
)
from pyqtgraph.opengl import shaders as gl_shaders

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QToolButton,
    QLabel,
    QButtonGroup,
)

from PySide6.QtCore import (
    Qt,
    Signal,
)

from source.models.face_mesh import FaceMesh


# -------------------------------------------------------------
# Face shading
# -------------------------------------------------------------
#
# PyQtGraph 0.14.0's built-in "shaded" shader uses a fixed
# light direction of (1, -1, -1) and only 20% ambient light.
# For a face/landmark inspection viewer this produces very
# dark areas on the mesh.
#
# This shader keeps the same PyQtGraph shader interface but
# uses a soft camera-relative key + fill light and a much
# stronger ambient component.
#
_FACE_INSPECTION_SHADER = None


def _get_face_inspection_shader():
    """
    Return the custom face-inspection shader.

    The shader is intentionally small and self-contained.
    It uses exactly the attributes/uniforms expected by
    GLMeshItem in PyQtGraph 0.14.0.
    """

    global _FACE_INSPECTION_SHADER

    if _FACE_INSPECTION_SHADER is None:

        _FACE_INSPECTION_SHADER = (
            gl_shaders.ShaderProgram(
                "faceInspectionShaded",
                [
                    gl_shaders.VertexShader(
                        """
                        uniform mat4 u_mvp;
                        uniform mat3 u_normal;

                        attribute vec4 a_position;
                        attribute vec3 a_normal;
                        attribute vec4 a_color;

                        varying vec4 v_color;
                        varying vec3 v_normal;

                        void main()
                        {
                            v_normal =
                                normalize(
                                    u_normal * a_normal
                                );

                            v_color = a_color;

                            gl_Position =
                                u_mvp * a_position;
                        }
                        """
                    ),

                    gl_shaders.FragmentShader(
                        """
                        #ifdef GL_ES
                        precision mediump float;
                        #endif

                        varying vec4 v_color;
                        varying vec3 v_normal;

                        void main()
                        {
                            /*
                             * The normal is already in view space.
                             * The camera looks toward -Z, therefore
                             * +Z is the useful front-light direction.
                             */

                            vec3 keyDirection =
                                normalize(
                                    vec3(
                                        0.15,
                                        -0.20,
                                        1.0
                                    )
                                );

                            vec3 fillDirection =
                                normalize(
                                    vec3(
                                        -0.55,
                                        0.30,
                                        0.75
                                    )
                                );

                            float key =
                                max(
                                    dot(
                                        v_normal,
                                        keyDirection
                                    ),
                                    0.0
                                );

                            float fill =
                                max(
                                    dot(
                                        v_normal,
                                        fillDirection
                                    ),
                                    0.0
                                );

                            /*
                             * Strong ambient component:
                             * no part of the face can fall into
                             * the almost-black range of the
                             * original shader.
                             */

                            float lighting =
                                0.55
                                + (0.32 * key)
                                + (0.18 * fill);

                            lighting =
                                clamp(
                                    lighting,
                                    0.0,
                                    1.0
                                );

                            vec3 rgb =
                                v_color.rgb
                                * lighting;

                            gl_FragColor =
                                vec4(
                                    rgb,
                                    v_color.a
                                );
                        }
                        """
                    ),
                ]
            )
        )

    return _FACE_INSPECTION_SHADER


class MeshViewer(QWidget):
    """
    Viewer 3D della mesh facciale.

    Responsabilità:
    - visualizzazione della mesh;
    - visualizzazione point cloud;
    - visualizzazione wireframe;
    - gestione della camera;
    - gestione della selezione di un vertice;
    - visualizzazione dei vertici associati ai landmark.

    Il MeshViewer non modifica la mesh originale.
    """

    viewport_clicked = Signal(int, int)

    MODE_POINTS = 0
    MODE_WIREFRAME = 1
    MODE_MESH = 2

    # ---------------------------------------------------------
    # Construction
    # ---------------------------------------------------------

    def __init__(
        self,
        parent=None,
        show_guides=True,
    ):

        super().__init__(parent)

        self._show_guides = show_guides

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
        # Selected vertex marker
        #

        self._selected_vertex_item = None
        self._selected_vertex_index = None

        #
        # Vertice associato attualmente visualizzato.
        #
        # È separato da _selected_vertex_index perché il marker
        # azzurro è una visualizzazione di controllo di una
        # mappatura esistente e NON una selezione temporanea.
        #
        self._mapped_vertex_index = None
        self._mapped_vertex_indices = []
        self._mapped_vertex_item = None

        #
        # Stato del mouse.
        #
        # Il click sinistro ha due possibili significati:
        #
        # - click semplice -> selezione/picking del vertice;
        # - trascinamento -> rotazione della mesh.
        #
        # Il picking viene quindi deciso al rilascio del mouse,
        # dopo aver verificato se il puntatore si è mosso oltre
        # una piccola soglia.
        #

        self._mouse_press_pos = None
        self._mouse_dragging = False
        self._mouse_drag_threshold = 5

        #
        # Stato del PAN.
        #
        # Il pan viene attivato in due modi:
        #
        # - tasto centrale del mouse + trascinamento;
        # - CTRL + tasto sinistro + trascinamento.
        #
        # In entrambi i casi spostiamo il centro della camera
        # mantenendo invariati distanza, azimut ed elevazione.
        #
        self._mouse_pan_active = False
        self._mouse_pan_pos = None

        #
        # Mesh cache
        #

        self._mesh = None

        #
        # Centered vertex positions
        #
        # Queste sono le coordinate realmente utilizzate
        # dal renderer OpenGL.
        #

        self._vertex_positions = None

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

        self._view.mousePressEvent = self._mouse_press_event
        self._view.mouseMoveEvent = self._mouse_move_event
        self._view.mouseReleaseEvent = self._mouse_release_event

        self._view.setBackgroundColor("k")

        self._view.opts["fov"] = 45

        #
        # Camera
        #

        self.reset_camera()

        #
        # Grid
        #

        if self._show_guides:

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

        else:

            self._grid = None

        #
        # Axis
        #

        if self._show_guides:

            self._axis = gl.GLAxisItem()

            self._axis.setSize(
                0.5,
                0.5,
                0.5,
            )

            self._view.addItem(
                self._axis
            )

        else:

            self._axis = None

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
    # Vertex selection
    # ---------------------------------------------------------

    def select_vertex(
        self,
        vertex_index: int,
    ):
        """
        Seleziona visivamente un vertice della mesh.

        Parameters
        ----------
        vertex_index:
            Indice del vertice nella lista mesh.vertices.

        La selezione non modifica la mesh.
        Viene semplicemente aggiunto un marker
        tridimensionale nel punto corrispondente.
        """

        #
        # Nessuna mesh caricata
        #

        if self._mesh is None:

            self.clear_selected_vertex()

            return

        #
        # Nessuna posizione disponibile
        #

        if self._vertex_positions is None:

            self.clear_selected_vertex()

            return

        #
        # Controllo indice
        #

        if vertex_index < 0:

            self.clear_selected_vertex()

            return

        if vertex_index >= len(
            self._vertex_positions
        ):

            self.clear_selected_vertex()

            return

        #
        # Rimuove il marker precedente
        #

        self.clear_selected_vertex()

        #
        # Memorizza l'indice
        #

        self._selected_vertex_index = vertex_index

        #
        # Recupera la posizione OpenGL
        #

        position = self._vertex_positions[
            vertex_index
        ]

        #
        # Crea il marker
        #

        marker_position = np.array(
            [position],
            dtype=np.float32,
        )

        self._selected_vertex_item = (
            gl.GLScatterPlotItem(
                pos=marker_position,
                size=16,
                color=(
                    1.0,
                    0.0,
                    0.0,
                    1.0,
                ),
                pxMode=True,
            )
        )

        self._selected_vertex_item.setGLOptions(
            {
                GL_DEPTH_TEST: False,
                GL_BLEND: True,
                GL_ALPHA_TEST: False,
                GL_CULL_FACE: False,
                "glBlendFunc": (
                    GL_SRC_ALPHA,
                    GL_ONE_MINUS_SRC_ALPHA,
                ),
            }
        )

        self._selected_vertex_item.setDepthValue(
            110
        )

        #
        # Aggiunge il marker alla scena
        #

        self._view.addItem(
            self._selected_vertex_item
        )

    # ---------------------------------------------------------

    def select_mapped_vertex(
        self,
        vertex_index: int,
    ):
        """
        Visualizza in AZZURRO un singolo vertice già associato.

        Questo metodo mantiene la compatibilità con il comportamento
        precedente del MeshViewer. Internamente utilizza la nuova
        gestione multipla dei vertici associati.
        """

        self.show_mapped_vertices(
            [vertex_index]
        )

    # ---------------------------------------------------------

    def show_mapped_vertices(
        self,
        vertex_indices,
    ):
        """
        Visualizza contemporaneamente più vertici associati.

        Parameters
        ----------
        vertex_indices:
            Iterable di indici di vertice della mesh.

        Notes
        -----
        I marker associati sono indipendenti dalla selezione temporanea
        del vertice corrente. È quindi possibile visualizzare tutti i
        punti associati e, contemporaneamente, selezionare un nuovo
        vertice con il marker rosso.
        """

        if self._mesh is None:
            self.clear_mapped_vertices()
            return

        if self._vertex_positions is None:
            self.clear_mapped_vertices()
            return

        normalized_indices = []

        if vertex_indices is None:
            vertex_indices = []

        for value in vertex_indices:

            try:
                vertex_index = int(value)
            except (
                TypeError,
                ValueError,
            ):
                continue

            if vertex_index < 0:
                continue

            if vertex_index >= len(
                self._vertex_positions
            ):
                continue

            if vertex_index not in normalized_indices:
                normalized_indices.append(
                    vertex_index
                )

        self.clear_mapped_vertices()

        if not normalized_indices:
            return

        self._mapped_vertex_indices = (
            normalized_indices
        )

        self._mapped_vertex_index = (
            normalized_indices[0]
        )

        positions = np.array(
            [
                self._vertex_positions[
                    vertex_index
                ]
                for vertex_index in normalized_indices
            ],
            dtype=np.float32,
        )

        self._mapped_vertex_item = (
            gl.GLScatterPlotItem(
                pos=positions,
                size=18,
                color=(
                    0.0,
                    0.85,
                    1.0,
                    1.0,
                ),
                pxMode=True,
            )
        )

        self._mapped_vertex_item.setGLOptions(
            {
                GL_DEPTH_TEST: False,
                GL_BLEND: True,
                GL_ALPHA_TEST: False,
                GL_CULL_FACE: False,
                "glBlendFunc": (
                    GL_SRC_ALPHA,
                    GL_ONE_MINUS_SRC_ALPHA,
                ),
            }
        )

        self._mapped_vertex_item.setDepthValue(
            100
        )

        self._view.addItem(
            self._mapped_vertex_item
        )

    # ---------------------------------------------------------

    def clear_mapped_vertices(self):
        """
        Rimuove tutti i marker dei vertici associati.

        La mappatura nel modello non viene modificata.
        Viene rimossa esclusivamente la visualizzazione.
        """

        if self._mapped_vertex_item is not None:

            self._view.removeItem(
                self._mapped_vertex_item
            )

            self._mapped_vertex_item = None

        self._mapped_vertex_indices = []
        self._mapped_vertex_index = None

    # ---------------------------------------------------------

    def clear_selected_vertex(self):
        """
        Rimuove esclusivamente il marker del vertice
        selezionato temporaneamente.

        I marker dei vertici associati rimangono visibili.
        """

        if self._selected_vertex_item is not None:

            self._view.removeItem(
                self._selected_vertex_item
            )

            self._selected_vertex_item = None

        self._selected_vertex_index = None

    # ---------------------------------------------------------

    def selected_vertex_index(self):
        """
        Restituisce l'indice del vertice selezionato.

        Returns
        -------
        int | None
            Indice del vertice oppure None.
        """

        return self._selected_vertex_index

    # ---------------------------------------------------------

    def mapped_vertex_indices(self):
        """
        Restituisce gli indici dei vertici associati
        attualmente visualizzati.
        """

        return list(
            self._mapped_vertex_indices
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

        #
        # Selected vertex
        #

        self.clear_selected_vertex()

        #
        # Mapped vertices
        #

        self.clear_mapped_vertices()

        #
        # Coordinate cache
        #

        self._vertex_positions = None

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

        #
        # Memorizziamo l'indice selezionato prima
        # di ricostruire la scena.
        #

        selected_vertex_index = (
            self._selected_vertex_index
        )

        #
        # Memorizziamo anche gli eventuali vertici associati
        # visualizzati in AZZURRO.
        #
        mapped_vertex_indices = list(
            self._mapped_vertex_indices
        )

        #
        # Pulizia della scena
        #

        self.clear()

        if mesh is None:

            self._mesh = None

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
        # Controllo mesh vuota
        #

        if len(vertices) == 0:

            self._vertex_positions = None

            return

        #
        # Center mesh for visualization
        #

        min_corner = vertices.min(axis=0)

        max_corner = vertices.max(axis=0)

        center = (
            min_corner
            + max_corner
        ) * 0.5

        vertices = vertices - center

        #
        # Memorizza le coordinate effettivamente
        # utilizzate dal renderer.
        #

        self._vertex_positions = vertices.copy()

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

            self._points_item = (
                gl.GLScatterPlotItem(
                    pos=vertices,
                    size=5,
                    color=(
                        1.0,
                        1.0,
                        0.0,
                        1.0,
                    ),
                    pxMode=True,
                )
            )

            self._view.addItem(
                self._points_item
            )

        #
        # MeshData
        #

        else:

            mesh_data = gl.MeshData(
                vertexes=vertices,
                faces=faces,
            )

            #
            # SOLID MESH
            #

            if self._render_mode == self.MODE_MESH:

                self._mesh_item = (
                    gl.GLMeshItem(
                        meshdata=mesh_data,
                        smooth=True,
                        drawFaces=True,
                        drawEdges=False,
                        shader=_get_face_inspection_shader(),
                    )
                )

                self._view.addItem(
                    self._mesh_item
                )

            #
            # WIREFRAME
            #

            elif (
                self._render_mode
                == self.MODE_WIREFRAME
            ):

                self._wireframe_item = (
                    gl.GLMeshItem(
                        meshdata=mesh_data,
                        smooth=False,
                        drawFaces=False,
                        drawEdges=True,
                    )
                )

                self._view.addItem(
                    self._wireframe_item
                )

            #
            # Unknown rendering mode
            #

            else:

                raise ValueError(
                    "Unsupported render mode: "
                    f"{self._render_mode}"
                )

        #
        # Ripristina la selezione precedente.
        #
        # Questo è importante quando l'utente cambia
        # modalità di rendering.
        #

        if mapped_vertex_indices:

            self.show_mapped_vertices(
                mapped_vertex_indices
            )

        if selected_vertex_index is not None:

            self.select_vertex(
                selected_vertex_index
            )

    # ---------------------------------------------------------
    # Mouse
    # ---------------------------------------------------------

    def _mouse_press_event(self, event):
        """
        Gestisce l'inizio dell'interazione con il mouse.

        Modalità supportate:

        1. Click sinistro semplice:
           selezione/picking del vertice.

        2. Click sinistro + trascinamento:
           rotazione della mesh.

        3. Tasto centrale + trascinamento:
           PAN della mesh.

        4. CTRL + tasto sinistro + trascinamento:
           PAN della mesh.

        Il PAN viene gestito esplicitamente da MeshViewer invece
        di delegarlo completamente a GLViewWidget. In questo modo
        il comportamento rimane deterministico anche dopo zoom,
        rotazioni e riapertura del Vertex Mapper.
        """

        #
        # Tasto centrale -> PAN.
        #
        if event.button() == Qt.MiddleButton:

            self._mouse_pan_active = True
            self._mouse_pan_pos = event.position()

            event.accept()

            return

        #
        # Tasto sinistro + CTRL -> PAN.
        #
        if (
            event.button() == Qt.LeftButton
            and event.modifiers() & Qt.ControlModifier
        ):

            self._mouse_pan_active = True
            self._mouse_pan_pos = event.position()

            #
            # Non impostiamo _mouse_press_pos perché questo
            # gesto non deve mai generare un picking.
            #

            event.accept()

            return

        #
        # Tasto sinistro normale.
        #
        if event.button() == Qt.LeftButton:

            self._mouse_press_pos = event.position()
            self._mouse_dragging = False

        #
        # Rotazione / gestione standard di GLViewWidget.
        #
        gl.GLViewWidget.mousePressEvent(
            self._view,
            event,
        )

    # ---------------------------------------------------------

    def _mouse_move_event(self, event):
        """
        Gestisce il trascinamento del mouse.

        PAN:
            tasto centrale
            oppure CTRL + tasto sinistro.

        ROTAZIONE:
            tasto sinistro normale.

        PICKING:
            viene deciso esclusivamente al rilascio del tasto
            sinistro quando non è stato effettuato un trascinamento.
        """

        #
        # PAN esplicito.
        #
        if self._mouse_pan_active:

            if self._mouse_pan_pos is None:
                return

            current_pos = event.position()

            delta = (
                current_pos
                - self._mouse_pan_pos
            )

            #
            # Aggiorniamo subito il riferimento per ottenere
            # un movimento fluido e proporzionale al mouse.
            #
            self._mouse_pan_pos = current_pos

            #
            # Pan relativo alla vista:
            #
            #   +X -> destra
            #   +Y -> alto
            #
            # Il metodo pan() di GLViewWidget modifica il
            # centro della camera senza alterare zoom e
            # orientamento.
            #
            self._view.pan(
                delta.x(),
                delta.y(),
                0,
                relative="view",
            )

            event.accept()

            return

        #
        # ROTAZIONE.
        #
        if (
            self._mouse_press_pos is not None
            and event.buttons() & Qt.LeftButton
        ):

            delta = (
                event.position()
                - self._mouse_press_pos
            )

            if (
                abs(delta.x()) >= self._mouse_drag_threshold
                or
                abs(delta.y()) >= self._mouse_drag_threshold
            ):

                self._mouse_dragging = True

        gl.GLViewWidget.mouseMoveEvent(
            self._view,
            event,
        )

    # ---------------------------------------------------------

    def _mouse_release_event(self, event):
        """
        Completa l'interazione con il mouse.

        PAN:
            termina il gesto e non produce picking.

        CLICK:
            se il tasto sinistro viene rilasciato senza
            trascinamento, viene emesso viewport_clicked.

        ROTAZIONE:
            se il mouse è stato trascinato, nessun picking.
        """

        #
        # Fine PAN.
        #
        if (
            self._mouse_pan_active
            and (
                event.button() == Qt.MiddleButton
                or event.button() == Qt.LeftButton
            )
        ):

            self._mouse_pan_active = False
            self._mouse_pan_pos = None

            event.accept()

            return

        #
        # Picking soltanto per il click sinistro normale.
        #
        should_pick = (
            event.button() == Qt.LeftButton
            and self._mouse_press_pos is not None
            and not self._mouse_dragging
        )

        if should_pick:

            self.viewport_clicked.emit(
                int(event.position().x()),
                int(event.position().y()),
            )

        #
        # Lasciamo completare a GLViewWidget la normale
        # gestione del rilascio dopo il picking.
        #
        gl.GLViewWidget.mouseReleaseEvent(
            self._view,
            event,
        )

        #
        # Reset stato click/rotazione.
        #
        if event.button() == Qt.LeftButton:

            self._mouse_press_pos = None
            self._mouse_dragging = False

