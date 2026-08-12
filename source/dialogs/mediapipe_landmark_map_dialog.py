"""
==========================================================
Face3D Studio AI

MediaPipe Landmark Map Dialog

Responsabilità:
- visualizzazione della mappa grafica dei landmark MediaPipe;
- consultazione visiva della distribuzione dei landmark;
- selezione interattiva dei 25 Control Points;
- evidenziazione del landmark selezionato;
- nessuna modifica alla mesh;
- nessuna modifica al mapping.

Versione:
1.2.0
==========================================================
"""

from pathlib import Path
import math

from PySide6.QtCore import (
    Qt,
    Signal,
)

from PySide6.QtGui import (
    QPainter,
    QPen,
    QPixmap,
)

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


# ==========================================================
# Control Point Map
# ==========================================================

#
# Coordinate dei 25 Control Points sulla PNG originale:
#
#   mediapipe_landmark_map.png
#
# Risoluzione:
#
#   1536 × 1024
#
# Le coordinate sono espresse nello spazio dell'immagine
# originale e NON nello spazio della QLabel.
#
# Questo è fondamentale perché la QLabel viene ridimensionata
# dinamicamente.
#

LANDMARK_MAP_POSITIONS = {

    # ------------------------------------------------------
    # Volto
    # ------------------------------------------------------

    10: (586, 116),
    152: (582, 742),

    # ------------------------------------------------------
    # Naso
    # ------------------------------------------------------

    1: (585, 407),
    2: (585, 437),
    4: (585, 456),
    98: (563, 442),
    327: (607, 442),

    # ------------------------------------------------------
    # Occhio destro
    # ------------------------------------------------------

    33: (468, 316),
    133: (506, 320),
    159: (489, 306),
    145: (489, 334),

    # ------------------------------------------------------
    # Occhio sinistro
    # ------------------------------------------------------

    263: (699, 316),
    362: (661, 320),
    386: (680, 306),
    374: (680, 334),

    # ------------------------------------------------------
    # Bocca
    # ------------------------------------------------------

    61: (458, 527),
    291: (700, 527),
    13: (584, 521),
    14: (584, 542),
    78: (518, 523),
    308: (650, 523),

    # ------------------------------------------------------
    # Sopracciglio destro
    # ------------------------------------------------------

    46: (431, 244),
    55: (528, 227),

    # ------------------------------------------------------
    # Sopracciglio sinistro
    # ------------------------------------------------------

    276: (742, 244),
    285: (800, 230),
}


# ==========================================================
# Clickable Image Label
# ==========================================================


class ClickableImageLabel(QLabel):
    """
    QLabel specializzato per la visualizzazione interattiva
    della mappa MediaPipe.

    Responsabilità:
    - visualizzare l'immagine;
    - intercettare il click;
    - convertire le coordinate;
    - individuare il Control Point più vicino;
    - evidenziare il Control Point selezionato.

    Non contiene:
    - logica della mesh;
    - VertexMappingCollection;
    - MeshViewer;
    - logica di associazione.
    """

    clicked = Signal(
        int,
        int,
    )

    landmark_clicked = Signal(
        int,
    )

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)

        self._pixmap = None

        self._selected_landmark_index = None

        self._selected_point = None

        self.setAlignment(
            Qt.AlignCenter
        )

    # ---------------------------------------------------------
    # Source pixmap
    # ---------------------------------------------------------

    def set_source_pixmap(
        self,
        pixmap: QPixmap,
    ):
        """
        Imposta l'immagine originale.
        """

        self._pixmap = pixmap

        self._update_display()

    # ---------------------------------------------------------
    # Selected landmark
    # ---------------------------------------------------------

    def set_selected_landmark(
        self,
        landmark_index,
    ):
        """
        Imposta il Control Point da evidenziare.

        Parameters
        ----------
        landmark_index:
            Indice MediaPipe del Control Point.
        """

        self._selected_landmark_index = (
            landmark_index
        )

        if (
            landmark_index is None
            or
            landmark_index
            not in LANDMARK_MAP_POSITIONS
        ):
            self._selected_point = None

        else:
            self._selected_point = (
                LANDMARK_MAP_POSITIONS[
                    landmark_index
                ]
            )

        self.update()

    # ---------------------------------------------------------
    # Resize
    # ---------------------------------------------------------

    def resizeEvent(
        self,
        event,
    ):
        """
        Ridimensiona l'immagine mantenendo le proporzioni.
        """

        super().resizeEvent(
            event
        )

        self._update_display()

    # ---------------------------------------------------------
    # Display
    # ---------------------------------------------------------

    def _update_display(
        self,
    ):
        """
        Adatta l'immagine alle dimensioni disponibili.
        """

        if self._pixmap is None:
            return

        scaled = self._pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        self.setPixmap(
            scaled
        )

        self.update()

    # ---------------------------------------------------------
    # Display geometry
    # ---------------------------------------------------------

    def _get_display_geometry(
        self,
    ):
        """
        Restituisce le informazioni necessarie
        per convertire coordinate tra:

            immagine originale
                ↕
            immagine visualizzata
        """

        if self._pixmap is None:
            return None

        displayed_pixmap = self.pixmap()

        if (
            displayed_pixmap is None
            or
            displayed_pixmap.isNull()
        ):
            return None

        displayed_width = (
            displayed_pixmap.width()
        )

        displayed_height = (
            displayed_pixmap.height()
        )

        offset_x = (
            self.width()
            - displayed_width
        ) / 2.0

        offset_y = (
            self.height()
            - displayed_height
        ) / 2.0

        scale_x = (
            self._pixmap.width()
            / displayed_width
        )

        scale_y = (
            self._pixmap.height()
            / displayed_height
        )

        return (
            displayed_pixmap,
            displayed_width,
            displayed_height,
            offset_x,
            offset_y,
            scale_x,
            scale_y,
        )

    # ---------------------------------------------------------
    # Original → display
    # ---------------------------------------------------------

    def _original_to_display(
        self,
        x,
        y,
    ):
        """
        Converte una coordinata dell'immagine originale
        nella coordinata visualizzata nella QLabel.
        """

        geometry = (
            self._get_display_geometry()
        )

        if geometry is None:
            return None

        (
            displayed_pixmap,
            displayed_width,
            displayed_height,
            offset_x,
            offset_y,
            scale_x,
            scale_y,
        ) = geometry

        display_x = (
            x / scale_x
        ) + offset_x

        display_y = (
            y / scale_y
        ) + offset_y

        return (
            display_x,
            display_y,
        )

    # ---------------------------------------------------------
    # Paint
    # ---------------------------------------------------------

    def paintEvent(
        self,
        event,
    ):
        """
        Disegna l'immagine e successivamente
        il marker del Control Point selezionato.
        """

        super().paintEvent(
            event
        )

        if self._selected_point is None:
            return

        display_position = (
            self._original_to_display(
                self._selected_point[0],
                self._selected_point[1],
            )
        )

        if display_position is None:
            return

        x, y = display_position

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.Antialiasing,
            True,
        )

        #
        # Cerchio esterno.
        #

        outer_pen = QPen(
            Qt.cyan,
            3,
        )

        painter.setPen(
            outer_pen
        )

        painter.drawEllipse(
            int(x - 10),
            int(y - 10),
            20,
            20,
        )

        #
        # Punto centrale.
        #

        center_pen = QPen(
            Qt.white,
            2,
        )

        painter.setPen(
            center_pen
        )

        painter.drawEllipse(
            int(x - 3),
            int(y - 3),
            6,
            6,
        )

        painter.end()

    # ---------------------------------------------------------
    # Mouse
    # ---------------------------------------------------------

    def mousePressEvent(
        self,
        event,
    ):
        """
        Gestisce il click sulla mappa.
        """

        if (
            self._pixmap is None
            or
            self._pixmap.isNull()
        ):
            return

        if (
            event.button()
            != Qt.LeftButton
        ):
            return

        geometry = (
            self._get_display_geometry()
        )

        if geometry is None:
            return

        (
            displayed_pixmap,
            displayed_width,
            displayed_height,
            offset_x,
            offset_y,
            scale_x,
            scale_y,
        ) = geometry

        widget_x = (
            event.position().x()
        )

        widget_y = (
            event.position().y()
        )

        #
        # Coordinate relative all'immagine visualizzata.
        #

        image_display_x = (
            widget_x - offset_x
        )

        image_display_y = (
            widget_y - offset_y
        )

        #
        # Click fuori dall'immagine.
        #

        if (
            image_display_x < 0
            or
            image_display_y < 0
            or
            image_display_x >= displayed_width
            or
            image_display_y >= displayed_height
        ):
            return

        #
        # Conversione nell'immagine originale.
        #

        original_x = int(
            image_display_x * scale_x
        )

        original_y = int(
            image_display_y * scale_y
        )

        #
        # Limiti.
        #

        original_x = max(
            0,
            min(
                original_x,
                self._pixmap.width() - 1,
            ),
        )

        original_y = max(
            0,
            min(
                original_y,
                self._pixmap.height() - 1,
            ),
        )

        #
        # Evento generico del click.
        #

        self.clicked.emit(
            original_x,
            original_y,
        )

        #
        # Cerchiamo il Control Point più vicino.
        #

        landmark_index = (
            self._find_nearest_landmark(
                original_x,
                original_y,
            )
        )

        if landmark_index is None:

            self.set_selected_landmark(
                None
            )

            return

        #
        # Evidenziazione.
        #

        self.set_selected_landmark(
            landmark_index
        )

        #
        # Notifica il landmark selezionato.
        #

        self.landmark_clicked.emit(
            landmark_index
        )

    # ---------------------------------------------------------
    # Nearest landmark
    # ---------------------------------------------------------

    def _find_nearest_landmark(
        self,
        x,
        y,
    ):
        """
        Restituisce il Control Point più vicino
        al click.

        Se il punto più vicino è oltre la tolleranza
        massima, restituisce None.
        """

        if not LANDMARK_MAP_POSITIONS:
            return None

        nearest_index = None

        nearest_distance = float(
            "inf"
        )

        for (
            landmark_index,
            point,
        ) in LANDMARK_MAP_POSITIONS.items():

            px, py = point

            distance = math.hypot(
                x - px,
                y - py,
            )

            if distance < nearest_distance:

                nearest_distance = (
                    distance
                )

                nearest_index = (
                    landmark_index
                )

        #
        # Tolleranza nella risoluzione originale
        # della PNG.
        #
        # 22 px rappresentano una zona sufficientemente
        # ampia per facilitare il click ma abbastanza
        # piccola da evitare selezioni casuali.
        #

        if nearest_distance > 22:
            return None

        return nearest_index


# ==========================================================
# MediaPipe Landmark Map Dialog
# ==========================================================


class MediaPipeLandmarkMapDialog(QDialog):
    """
    Finestra interattiva della mappa MediaPipe.

    La finestra:
    - visualizza la mappa;
    - permette di selezionare i 25 Control Points;
    - evidenzia il Control Point selezionato;
    - restituisce l'indice MediaPipe selezionato.

    Non modifica:
    - mesh;
    - VertexMappingCollection;
    - MeshViewer.
    """

    landmark_selected = Signal(
        int,
    )

    # ---------------------------------------------------------
    # Construction
    # ---------------------------------------------------------

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(
            parent
        )

        self.setWindowTitle(
            "Face3D Studio - Mappa Landmark MediaPipe"
        )

        self.resize(
            1200,
            900,
        )

        self.setMinimumSize(
            900,
            700,
        )

        # -----------------------------------------------------
        # Layout principale
        # -----------------------------------------------------

        layout = QVBoxLayout(
            self
        )

        # -----------------------------------------------------
        # Titolo
        # -----------------------------------------------------

        title = QLabel(
            "<h2>Mappa Landmark MediaPipe</h2>"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            title
        )

        # -----------------------------------------------------
        # Immagine
        # -----------------------------------------------------

        self.image_label = (
            ClickableImageLabel()
        )

        self.image_label.setMinimumSize(
            800,
            600,
        )

        self.image_label.setStyleSheet(
            "background-color: white;"
            "border: 1px solid #555;"
        )

        self.image_label.clicked.connect(
            self._on_map_clicked
        )

        self.image_label.landmark_clicked.connect(
            self._on_landmark_clicked
        )

        layout.addWidget(
            self.image_label,
            1,
        )

        # -----------------------------------------------------
        # Landmark selezionato
        # -----------------------------------------------------

        self.landmark_label = QLabel(
            "Landmark selezionato: —"
        )

        self.landmark_label.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            self.landmark_label
        )

        # -----------------------------------------------------
        # Coordinate
        # -----------------------------------------------------

        self.coordinate_label = QLabel(
            "Posizione: —"
        )

        self.coordinate_label.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            self.coordinate_label
        )

        # -----------------------------------------------------
        # Informazioni immagine
        # -----------------------------------------------------

        self.image_info_label = QLabel(
            "Immagine: —"
        )

        self.image_info_label.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            self.image_info_label
        )

        # -----------------------------------------------------
        # Pulsante chiusura
        # -----------------------------------------------------

        self.close_button = QPushButton(
            "Chiudi"
        )

        self.close_button.clicked.connect(
            self.close
        )

        bottom_layout = QHBoxLayout()

        bottom_layout.addStretch()

        bottom_layout.addWidget(
            self.close_button
        )

        layout.addLayout(
            bottom_layout
        )

        # -----------------------------------------------------
        # Stato interno
        # -----------------------------------------------------

        self._pixmap = None

        self._selected_landmark_index = None

        # -----------------------------------------------------
        # Caricamento
        # -----------------------------------------------------

        self._load_map()

    # ---------------------------------------------------------
    # Caricamento mappa
    # ---------------------------------------------------------

    def _load_map(
        self,
    ):
        """
        Carica la mappa dalla directory
        resources/mediapipe.
        """

        image_path = (
            Path(__file__).resolve().parents[1]
            / "resources"
            / "mediapipe"
            / "mediapipe_landmark_map.png"
        )

        if not image_path.exists():

            self.image_label.setText(
                "Mappa MediaPipe non trovata.\n\n"
                "Posizionare il file:\n"
                f"{image_path}"
            )

            self.image_label.setWordWrap(
                True
            )

            self.image_info_label.setText(
                "Immagine non disponibile."
            )

            return

        self._pixmap = QPixmap(
            str(image_path)
        )

        if self._pixmap.isNull():

            self.image_label.setText(
                "Impossibile caricare "
                "la mappa MediaPipe."
            )

            self.image_info_label.setText(
                "Errore caricamento immagine."
            )

            return

        #
        # Passaggio dell'immagine al widget.
        #

        self.image_label.set_source_pixmap(
            self._pixmap
        )

        #
        # Informazioni.
        #

        self.image_info_label.setText(
            "Immagine originale: "
            f"{self._pixmap.width()} × "
            f"{self._pixmap.height()} px"
        )

    # ---------------------------------------------------------
    # Map click
    # ---------------------------------------------------------

    def _on_map_clicked(
        self,
        x: int,
        y: int,
    ):
        """
        Visualizza le coordinate del click.
        """

        self.coordinate_label.setText(
            f"Posizione: X = {x}   Y = {y}"
        )

    # ---------------------------------------------------------
    # Landmark clicked
    # ---------------------------------------------------------

    def _on_landmark_clicked(
        self,
        landmark_index: int,
    ):
        """
        Gestisce il riconoscimento di un Control Point.
        """

        self._selected_landmark_index = (
            landmark_index
        )

        self.image_label.set_selected_landmark(
            landmark_index
        )

        self.landmark_label.setText(
            "Landmark selezionato: "
            f"{landmark_index}"
        )

        self.landmark_selected.emit(
            landmark_index
        )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def get_selected_landmark_index(
        self,
    ):
        """
        Restituisce l'indice MediaPipe
        attualmente selezionato.
        """

        return (
            self._selected_landmark_index
        )

    def select_landmark(
        self,
        landmark_index,
    ):
        """
        Seleziona programmaticamente
        un Control Point.

        Questo metodo verrà utilizzato
        nel prossimo step per sincronizzare
        la ComboBox del Vertex Mapper
        con la mappa.
        """

        if (
            landmark_index is None
            or
            landmark_index
            not in LANDMARK_MAP_POSITIONS
        ):
            return False

        self._selected_landmark_index = (
            landmark_index
        )

        self.image_label.set_selected_landmark(
            landmark_index
        )

        self.landmark_label.setText(
            "Landmark selezionato: "
            f"{landmark_index}"
        )

        return True