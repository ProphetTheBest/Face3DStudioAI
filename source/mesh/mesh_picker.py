"""
==========================================================
Face3D Studio AI

Mesh Picker

Responsabilità:
- gestione delle coordinate dei vertici della mesh;
- proiezione dei vertici 3D sul piano dello schermo;
- ricerca del vertice più vicino al click del mouse;
- restituzione dell'indice e delle coordinate del vertice.

Il MeshPicker non gestisce:
- rendering;
- GUI;
- evidenziazione grafica;
- MediaPipe;
- salvataggio JSON.

Autore:
Marco Cantù

Versione:
1.2.0
==========================================================
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class PickResult:
    """
    Risultato della selezione di un vertice.
    """

    vertex_index: int

    x: float
    y: float
    z: float

    screen_x: float
    screen_y: float

    distance: float


class MeshPicker:
    """
    Algoritmo di selezione dei vertici della mesh.

    Il picker utilizza la matrice di vista e la matrice
    di proiezione del GLViewWidget per proiettare i vertici
    3D nelle coordinate della viewport.

    Successivamente individua il vertice più vicino
    al punto cliccato dall'utente.
    """

    def __init__(
        self,
        view,
        max_distance: float = 15.0,
    ):
        """
        Parameters
        ----------
        view:
            Istanza di pyqtgraph.opengl.GLViewWidget.

        max_distance:
            Distanza massima in pixel entro la quale
            un vertice può essere selezionato.
        """

        self._view = view

        self._max_distance = float(
            max_distance
        )

        self._vertices = None

        self._original_vertices = None

        self._center = np.zeros(
            3,
            dtype=np.float64,
        )

    # ---------------------------------------------------------
    # Mesh
    # ---------------------------------------------------------

    def set_mesh(
        self,
        mesh,
    ):
        """
        Imposta la mesh da utilizzare per il picking.

        La mesh viene centrata esattamente come nel
        MeshViewer.

        La mesh originale non viene modificata.
        """

        if mesh is None:

            self.clear()

            return

        vertices = np.array(
            [
                [
                    vertex.x,
                    vertex.y,
                    vertex.z,
                ]
                for vertex in mesh.vertices
            ],
            dtype=np.float64,
        )

        if vertices.size == 0:

            self.clear()

            return

        #
        # Conserviamo le coordinate originali.
        #

        self._original_vertices = (
            vertices.copy()
        )

        #
        # Bounding box.
        #

        min_corner = vertices.min(
            axis=0
        )

        max_corner = vertices.max(
            axis=0
        )

        #
        # Centro del bounding box.
        #

        self._center = (
            min_corner + max_corner
        ) * 0.5

        #
        # Coordinate utilizzate dal viewer.
        #

        self._vertices = (
            vertices - self._center
        )

    # ---------------------------------------------------------
    # Clear
    # ---------------------------------------------------------

    def clear(self):
        """
        Cancella la mesh attualmente utilizzata.
        """

        self._vertices = None

        self._original_vertices = None

        self._center = np.zeros(
            3,
            dtype=np.float64,
        )

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def vertex_count(self) -> int:
        """
        Numero di vertici disponibili.
        """

        if self._vertices is None:

            return 0

        return len(
            self._vertices
        )

    # ---------------------------------------------------------
    # Qt matrix -> NumPy
    # ---------------------------------------------------------

    @staticmethod
    def _qmatrix4x4_to_numpy(
        matrix,
    ) -> np.ndarray:
        """
        Converte una QMatrix4x4 Qt in una matrice
        NumPy 4x4.

        IMPORTANTE:

        QMatrix4x4 memorizza i dati in ordine column-major.

        Per poter utilizzare la matrice con una normale
        moltiplicazione NumPy:

            matrix @ vector

        dobbiamo quindi effettuare la trasposizione
        dopo il reshape.

        È lo stesso principio utilizzato da pyqtgraph
        quando trasferisce la matrice verso OpenGL.
        """

        data = matrix.copyDataTo()

        values = np.asarray(
            data,
            dtype=np.float64,
        )

        if values.size != 16:

            raise RuntimeError(
                "QMatrix4x4 non contiene "
                "16 elementi."
            )

        return values.reshape(
            (4, 4)
        )

    # ---------------------------------------------------------
    # Projection
    # ---------------------------------------------------------

    def _project_vertex(
        self,
        vertex,
    ):
        """
        Proietta un vertice 3D nelle coordinate 2D
        della viewport.

        Restituisce:

            (screen_x, screen_y)

        oppure None se il vertice non è visibile.
        """

        #
        # Il GLViewWidget di pyqtgraph utilizza il
        # viewport corrente del widget.
        #

        viewport = (
            self._view.getViewport()
        )

        if viewport is None:

            return None

        if len(viewport) != 4:

            return None

        viewport_x = float(
            viewport[0]
        )

        viewport_y = float(
            viewport[1]
        )

        viewport_width = float(
            viewport[2]
        )

        viewport_height = float(
            viewport[3]
        )

        if (
            viewport_width <= 0
            or viewport_height <= 0
        ):

            return None

        #
        # Nelle versioni di pyqtgraph che utilizzano:
        #
        # projectionMatrix(region, viewport)
        #
        # il region deve essere espresso nello stesso
        # sistema del viewport.
        #
        # Non applichiamo quindi devicePixelRatio.
        #

        region = (
            0.0,
            0.0,
            float(
                self._view.width()
            ),
            float(
                self._view.height()
            ),
        )

        #
        # Matrice di vista.
        #

        view_qt = (
            self._view.viewMatrix()
        )

        #
        # Matrice di proiezione.
        #

        projection_qt = (
            self._view.projectionMatrix(
                region,
                viewport,
            )
        )

        #
        # Conversione Qt -> NumPy.
        #

        view_matrix = (
            self._qmatrix4x4_to_numpy(
                view_qt
            )
        )

        projection_matrix = (
            self._qmatrix4x4_to_numpy(
                projection_qt
            )
        )

        #
        # Vertice in coordinate omogenee.
        #

        vertex_homogeneous = np.array(
            [
                float(vertex[0]),
                float(vertex[1]),
                float(vertex[2]),
                1.0,
            ],
            dtype=np.float64,
        )

        #
        # VIEW
        #

        view_position = (
            view_matrix
            @ vertex_homogeneous
        )

        #
        # PROJECTION
        #

        clip_position = (
            projection_matrix
            @ view_position
        )

        w = float(
            clip_position[3]
        )

        if abs(w) < 1e-12:

            return None

        #
        # Normalized Device Coordinates.
        #

        ndc_x = (
            clip_position[0]
            / w
        )

        ndc_y = (
            clip_position[1]
            / w
        )

        ndc_z = (
            clip_position[2]
            / w
        )

        #
        # Scartiamo i punti fuori dal volume visibile.
        #

        if (
            ndc_x < -1.0
            or ndc_x > 1.0
            or ndc_y < -1.0
            or ndc_y > 1.0
            or ndc_z < -1.0
            or ndc_z > 1.0
        ):

            return None

        #
        # NDC -> OpenGL viewport.
        #

        viewport_screen_x = (
            viewport_x
            + (
                ndc_x + 1.0
            )
            * 0.5
            * viewport_width
        )

        viewport_screen_y = (
            viewport_y
            + (
                ndc_y + 1.0
            )
            * 0.5
            * viewport_height
        )

        #
        # OpenGL ha origine Y in basso.
        #
        # Qt ha origine Y in alto.
        #

        screen_x = (
            viewport_screen_x
        )

        screen_y = (
            viewport_y
            + viewport_height
            - (
                viewport_screen_y
                - viewport_y
            )
        )

        return (
            screen_x,
            screen_y,
        )

    # ---------------------------------------------------------
    # Pick
    # ---------------------------------------------------------

    def pick(
        self,
        screen_x: float,
        screen_y: float,
    ):
        """
        Cerca il vertice più vicino al click.

        Parameters
        ----------
        screen_x:
            Coordinata X del mouse.

        screen_y:
            Coordinata Y del mouse.

        Returns
        -------
        PickResult | None
        """

        if self._vertices is None:

            return None

        if self.vertex_count == 0:

            return None

        best_index = None

        best_distance = float(
            "inf"
        )

        best_screen_x = 0.0

        best_screen_y = 0.0

        #
        # Proiettiamo ogni vertice.
        #

        for index, vertex in enumerate(
            self._vertices
        ):

            projected = (
                self._project_vertex(
                    vertex
                )
            )

            if projected is None:

                continue

            projected_x = (
                projected[0]
            )

            projected_y = (
                projected[1]
            )

            dx = (
                projected_x
                - float(screen_x)
            )

            dy = (
                projected_y
                - float(screen_y)
            )

            distance = float(
                np.sqrt(
                    dx * dx
                    + dy * dy
                )
            )

            if distance < best_distance:

                best_distance = distance

                best_index = index

                best_screen_x = (
                    projected_x
                )

                best_screen_y = (
                    projected_y
                )

        #
        # Nessun vertice visibile.
        #

        if best_index is None:

            return None

        #
        # Nessun vertice sufficientemente vicino.
        #

        if (
            best_distance
            > self._max_distance
        ):

            return None

        #
        # Coordinate ORIGINALI del template.
        #

        original_vertex = (
            self._original_vertices[
                best_index
            ]
        )

        return PickResult(
            vertex_index=int(
                best_index
            ),

            x=float(
                original_vertex[0]
            ),

            y=float(
                original_vertex[1]
            ),

            z=float(
                original_vertex[2]
            ),

            screen_x=float(
                best_screen_x
            ),

            screen_y=float(
                best_screen_y
            ),

            distance=float(
                best_distance
            ),
        )