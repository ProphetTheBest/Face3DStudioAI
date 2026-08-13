"""
==========================================================
Face3D Studio AI

Vertex Mapper Dialog

Responsabilità:
- visualizzazione del template della testa;
- gestione dei click nella viewport;
- selezione dei vertici tramite MeshPicker;
- visualizzazione delle informazioni del vertice selezionato;
- gestione della selezione temporanea del vertice;
- gestione della VertexMappingCollection;
- selezione del landmark MediaPipe;
- creazione delle associazioni landmark ↔ vertice.

Autore:
Marco Cantù

Versione:
1.8.0
==========================================================
"""

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QGroupBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from PySide6.QtCore import QTimer

from source.widgets.mesh_viewer import MeshViewer

from source.mesh.mesh_picker import (
    MeshPicker,
)

from source.reconstruction.loaders.template_loader import (
    TemplateLoader,
)

from source.models.geometry.vertex3d import (
    Vertex3D,
)

from source.models.mapping.vertex_mapping import (
    VertexMapping,
)

from source.models.mapping.vertex_mapping_collection import (
    VertexMappingCollection,
)

from source.models.landmarks.landmark_catalog import (
    LandmarkCatalog,
)

from source.models.landmarks.standard_landmarks import (
    create_standard_landmarks,
)

from source.dialogs.mapping_report_dialog import (
    MappingReportDialog,
)

from source.dialogs.mediapipe_landmark_map_dialog import (
    MediaPipeLandmarkMapDialog,
)


class VertexMapperDialog(QDialog):
    """
    Dialog per la costruzione della mappatura
    MediaPipe ↔ template anatomico.

    La GUI gestisce esclusivamente:

    - visualizzazione;
    - interazione con l'utente;
    - selezione del vertice;
    - selezione del landmark;
    - richiesta di creazione della mappatura.

    La raccolta delle mappature è mantenuta
    nel modello VertexMappingCollection.
    """

    def __init__(
        self,
        mapping_collection=None,
        parent=None,
    ):

        super().__init__(parent)

        # -----------------------------------------------------
        # Finestra
        # -----------------------------------------------------

        self.setWindowTitle(
            "Face3D Studio - Vertex Mapper"
        )

        self.resize(
            1100,
            800,
        )

        self.setMinimumSize(
            900,
            650,
        )

        # -----------------------------------------------------
        # Stato della selezione del vertice
        # -----------------------------------------------------

        #
        # Indice dell'ultimo vertice selezionato.
        #

        self._selected_vertex_index = None

        #
        # Coordinate del vertice selezionato.
        #

        self._selected_vertex = None

        #
        # Risultato completo dell'ultimo picking.
        #

        self._selected_pick_result = None

        # -----------------------------------------------------
        # Mapping collection
        # -----------------------------------------------------

        #
        # Contiene le mappature definitive.
        #

        if mapping_collection is None:
            self.mapping_collection = VertexMappingCollection()
        else:
            self.mapping_collection = mapping_collection

        # -----------------------------------------------------
        # Landmark catalog
        # -----------------------------------------------------

        #
        # Catalogo dei landmark MediaPipe utilizzati
        # da Face3D Studio.
        #

        self.landmark_catalog = (
            LandmarkCatalog()
        )

        #
        # Popolamento del catalogo.
        #

        for landmark in create_standard_landmarks():

            self.landmark_catalog.add(
                landmark
            )

        #
        # Landmark attualmente selezionato.
        #

        self._selected_landmark_index = None

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
            "<h2>Vertex Mapper</h2>"
        )

        layout.addWidget(
            title
        )

        self.progress_label = QLabel()
        layout.addWidget(self.progress_label)

        # -----------------------------------------------------
        # Landmark selector
        # -----------------------------------------------------

        landmark_label = QLabel(
            "Landmark MediaPipe:"
        )

        layout.addWidget(
            landmark_label
        )

        self.landmark_combo = QComboBox()

        #
        # Inseriamo tutti i landmark ordinati
        # per indice.
        #

        for landmark in self.landmark_catalog.all():

            self.landmark_combo.addItem(
                f"{landmark.name} "
                f"({landmark.index})",
                landmark.index,
            )

        #
        # Selezioniamo il primo landmark come valore
        # iniziale.
        #

        if self.landmark_combo.count() > 0:

            self.landmark_combo.setCurrentIndex(
                0
            )

            self._selected_landmark_index = (
                self.landmark_combo.currentData()
            )

        #
        # Segnale di cambio selezione.
        #

        self.landmark_combo.currentIndexChanged.connect(
            self._on_landmark_changed
        )

        layout.addWidget(
            self.landmark_combo
        )

        # -----------------------------------------------------
        # Visualizzazione delle mappature
        # -----------------------------------------------------
        #
        # Il MeshViewer supporta la visualizzazione contemporanea
        # di più vertici associati.
        #
        # In questa versione offriamo la visualizzazione:
        #
        # - Nessuno
        # - Solo landmark corrente
        # - Tutti
        # - per gruppo anatomico
        #
        # I gruppi vengono determinati dal nome semantico del
        # LandmarkDefinition già presente nel catalogo. In questo
        # modo non introduciamo una seconda lista di landmark nella
        # GUI e non modifichiamo la persistenza del mapping.
        #

        mapping_display_label = QLabel(
            "Visualizzazione mapping:"
        )

        layout.addWidget(
            mapping_display_label
        )

        self.mapping_display_combo = QComboBox()

        self.mapping_display_combo.addItem(
            "Nessuno",
            "none",
        )

        self.mapping_display_combo.addItem(
            "Solo landmark corrente",
            "current",
        )

        self.mapping_display_combo.addItem(
            "Tutti",
            "all",
        )

        self.mapping_display_combo.addItem(
            "Volto",
            "face",
        )

        self.mapping_display_combo.addItem(
            "Naso",
            "nose",
        )

        self.mapping_display_combo.addItem(
            "Occhio destro",
            "right_eye",
        )

        self.mapping_display_combo.addItem(
            "Occhio sinistro",
            "left_eye",
        )

        self.mapping_display_combo.addItem(
            "Bocca",
            "mouth",
        )

        self.mapping_display_combo.addItem(
            "Sopracciglio destro",
            "right_eyebrow",
        )

        self.mapping_display_combo.addItem(
            "Sopracciglio sinistro",
            "left_eyebrow",
        )

        #
        # Manteniamo come comportamento predefinito quello
        # precedente: mostrare il mapping del landmark corrente.
        #

        self.mapping_display_combo.setCurrentIndex(
            self.mapping_display_combo.findData(
                "current"
            )
        )

        self.mapping_display_combo.currentIndexChanged.connect(
            self._on_mapping_display_changed
        )

        layout.addWidget(
            self.mapping_display_combo
        )

        #
        # Mappa grafica dei landmark MediaPipe.
        #
        # La finestra è separata dal MeshViewer e serve
        # esclusivamente come riferimento visivo.
        #

        self.landmark_map_button = QPushButton(
            "Apri mappa landmark MediaPipe"
        )

        self.landmark_map_button.clicked.connect(
            self._on_show_landmark_map
        )

        layout.addWidget(
            self.landmark_map_button
        )

        # -----------------------------------------------------
        # Mesh Viewer
        # -----------------------------------------------------

        self.mesh_viewer = MeshViewer(
            show_guides=False
        )

        self.mesh_viewer.viewport_clicked.connect(
            self._on_viewport_clicked
        )

        layout.addWidget(
            self.mesh_viewer,
            1,
        )

        # -----------------------------------------------------
        # Load template
        # -----------------------------------------------------

        template = TemplateLoader.load(
            "male1591",
            "head",
        )

        self.mesh_viewer.show_mesh(
            template
        )

        # -----------------------------------------------------
        # Mesh Picker
        # -----------------------------------------------------

        self.mesh_picker = MeshPicker(
            self.mesh_viewer._view
        )

        self.mesh_picker.set_mesh(
            template
        )

        # -----------------------------------------------------
        # Associazione landmark → vertice
        # -----------------------------------------------------

        self.map_button = QPushButton(
            "Associa landmark → vertice"
        )

        self.map_button.clicked.connect(
            self._on_create_mapping
        )

        self.map_button.setEnabled(
            False
        )

        layout.addWidget(
            self.map_button
        )

        #
        # Pulsante dissociazione.
        #
        # Viene abilitato solo quando il landmark selezionato
        # possiede già una mappatura.
        #

        self.unmap_button = QPushButton(
            "Dissocia landmark"
        )

        self.unmap_button.clicked.connect(
            self._on_remove_mapping
        )

        self.unmap_button.setEnabled(
            False
        )

        layout.addWidget(
            self.unmap_button
        )

        # -----------------------------------------------------
        # Informazioni statiche del landmark corrente
        # -----------------------------------------------------

        info_box = QGroupBox(
            "Informazioni landmark corrente"
        )

        info_layout = QGridLayout(info_box)

        self._info_index = QLabel("—")
        self._info_name = QLabel("—")
        self._info_description = QLabel("—")
        self._info_status = QLabel("—")
        self._info_vertex = QLabel("—")
        self._info_x = QLabel("—")
        self._info_y = QLabel("—")
        self._info_z = QLabel("—")

        rows = [
            ("Indice:", self._info_index),
            ("Nome:", self._info_name),
            ("Descrizione:", self._info_description),
            ("Stato:", self._info_status),
            ("Vertex:", self._info_vertex),
            ("X:", self._info_x),
            ("Y:", self._info_y),
            ("Z:", self._info_z),
        ]

        for row,(label,value) in enumerate(rows):
            info_layout.addWidget(QLabel(label),row,0)
            info_layout.addWidget(value,row,1)

        layout.addWidget(info_box)

        # Log interno non più visualizzato.
        self.info = QTextEdit()
        self.info.setReadOnly(True)
        self.info.hide()

        self.report_button = QPushButton(
            "Visualizza report mappatura"
        )
        self.report_button.clicked.connect(self._on_show_report)
        layout.addWidget(self.report_button)

        # -----------------------------------------------------
        # Pulsante chiusura
        # -----------------------------------------------------

        self.close_button = QPushButton(
            "Chiudi"
        )

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.close_button)
        layout.addLayout(bottom_layout)

        self.close_button.clicked.connect(self.close)

        self._refresh_progress_label()
        self._refresh_landmark_panel()
        self._update_map_button_state()

        QTimer.singleShot(0, self._refresh_viewer_after_show)

    # ---------------------------------------------------------
    # Landmark changed
    # ---------------------------------------------------------

    def _on_landmark_changed(
        self,
        combo_index: int,
    ):
        """
        Gestisce il cambio del landmark selezionato
        nella ComboBox.
        """

        #
        # Nessun elemento.
        #

        if combo_index < 0:

            self._selected_landmark_index = None

            self._update_map_button_state()

            return

        #
        # Recuperiamo l'indice MediaPipe memorizzato
        # come userData della ComboBox.
        #

        landmark_index = (
            self.landmark_combo.itemData(
                combo_index
            )
        )

        if landmark_index is None:

            self._selected_landmark_index = None

            self._update_map_button_state()

            return

        #
        # Memorizziamo l'indice.
        #

        self._selected_landmark_index = (
            int(landmark_index)
        )

        #
        # Recuperiamo la definizione completa.
        #

        landmark = (
            self.landmark_catalog.get_by_index(
                self._selected_landmark_index
            )
        )

        #
        # Aggiorniamo le informazioni.
        #

        #
        # Cambiando landmark, la selezione temporanea del vertice
        # precedente non deve essere riutilizzata.
        #

        self.mesh_viewer.clear_selected_vertex()

        #
        # I marker blu dei mapping sono gestiti separatamente
        # dalla selezione temporanea rossa.
        #
        # La loro visualizzazione viene aggiornata alla fine
        # del metodo in base alla modalità scelta dall'utente.
        #

        self._selected_vertex_index = None
        self._selected_vertex = None
        self._selected_pick_result = None

        if landmark is not None:

            self.info.append(
                ""
            )

            self.info.append(
                "========== LANDMARK SELEZIONATO =========="
            )

            self.info.append(
                f"Indice      : {landmark.index}"
            )

            self.info.append(
                f"Nome        : {landmark.name}"
            )

            if landmark.description:

                self.info.append(
                    f"Descrizione : "
                    f"{landmark.description}"
                )

            mapping = (
                self.mapping_collection.get_by_landmark(
                    landmark.index
                )
            )

            if mapping is not None:

                self.mesh_viewer.select_mapped_vertex(
                    mapping.vertex_index
                )

                self.info.append(
                    ""
                )

                self.info.append(
                    "STATO: ASSOCIATO"
                )

                self.info.append(
                    f"Vertex associato: "
                    f"{mapping.vertex_index}"
                )

                self.info.append(
                    "Usa 'Dissocia landmark' "
                    "per poter creare una nuova associazione."
                )

            else:

                self.info.append(
                    ""
                )

                self.info.append(
                    "STATO: NON ASSOCIATO"
                )

            self.info.append(
                "=========================================="
            )

        self._refresh_landmark_panel()
        self._refresh_progress_label()
        self._update_map_button_state()
        self._refresh_mapped_markers()

    # ---------------------------------------------------------
    # Viewport click
    # ---------------------------------------------------------

    def _refresh_landmark_panel(self):
        """Aggiorna il pannello statico del landmark corrente."""
        landmark=None
        if self._selected_landmark_index is not None:
            landmark=self.landmark_catalog.get_by_index(self._selected_landmark_index)

        if landmark is None:
            for value in (self._info_index,self._info_name,self._info_description,self._info_status,self._info_vertex,self._info_x,self._info_y,self._info_z):
                value.setText("—")
            return

        self._info_index.setText(str(landmark.index))
        self._info_name.setText(landmark.name)
        self._info_description.setText(landmark.description or "—")
        mapping=self.mapping_collection.get_by_landmark(landmark.index)

        if mapping is None:
            self._info_status.setText("NON ASSOCIATO")
            self._info_vertex.setText("—")
            self._info_x.setText("—")
            self._info_y.setText("—")
            self._info_z.setText("—")
        else:
            self._info_status.setText("ASSOCIATO")
            self._info_vertex.setText(str(mapping.vertex_index))
            if mapping.vertex is not None:
                self._info_x.setText(f"{mapping.vertex.x:.6f}")
                self._info_y.setText(f"{mapping.vertex.y:.6f}")
                self._info_z.setText(f"{mapping.vertex.z:.6f}")
            else:
                self._info_x.setText("—")
                self._info_y.setText("—")
                self._info_z.setText("—")

    def _refresh_progress_label(self):
        total=self.landmark_combo.count()
        mapped=self.mapping_collection.count()
        self.progress_label.setText(f"Mappatura volto: <b>{mapped} / {total}</b> landmark associati")

    def _on_mapping_display_changed(
        self,
        combo_index: int,
    ):
        """
        Aggiorna la visualizzazione dei marker associati
        quando l'utente cambia la modalità di visualizzazione.
        """

        self._refresh_mapped_markers()

    # ---------------------------------------------------------

    def _refresh_mapped_markers(self):
        """
        Aggiorna esclusivamente i marker blu dei mapping.

        La mappatura nel modello non viene modificata.

        Modalità supportate
        -------------------
        none
            Nessun marker associato.

        current
            Solo il marker del landmark correntemente selezionato,
            se esiste una mappatura.

        all
            Tutti i vertici associati presenti nella collection.

        face / nose / right_eye / left_eye / mouth /
        right_eyebrow / left_eyebrow
            Solo i vertici associati appartenenti al gruppo
            anatomico selezionato.
        """

        if not hasattr(
            self,
            "mapping_display_combo",
        ):
            return

        mode = (
            self.mapping_display_combo.currentData()
        )

        if mode == "none":

            self.mesh_viewer.clear_mapped_vertices()

            return

        if mode == "current":

            if self._selected_landmark_index is None:

                self.mesh_viewer.clear_mapped_vertices()

                return

            mapping = (
                self.mapping_collection.get_by_landmark(
                    self._selected_landmark_index
                )
            )

            if mapping is None:

                self.mesh_viewer.clear_mapped_vertices()

                return

            self.mesh_viewer.show_mapped_vertices(
                [mapping.vertex_index]
            )

            return

        if mode == "all":

            vertex_indices = [
                mapping.vertex_index
                for mapping in self.mapping_collection.all()
            ]

            self.mesh_viewer.show_mapped_vertices(
                vertex_indices
            )

            return

        #
        # Filtri anatomici.
        #
        # Il filtro lavora sui LandmarkDefinition del catalogo,
        # non sui vertex index. Questo mantiene separati:
        #
        #   landmark semantico -> vertex associato -> visualizzazione
        #
        # e permette di cambiare un'associazione senza dover
        # modificare la logica della GUI.
        #

        anatomical_modes = {
            "face",
            "nose",
            "right_eye",
            "left_eye",
            "mouth",
            "right_eyebrow",
            "left_eyebrow",
        }

        if mode in anatomical_modes:

            vertex_indices = []

            for mapping in self.mapping_collection.all():

                landmark = (
                    self.landmark_catalog.get_by_index(
                        mapping.landmark_index
                    )
                )

                if landmark is None:
                    continue

                if (
                    self._get_landmark_group(landmark)
                    == mode
                ):
                    vertex_indices.append(
                        mapping.vertex_index
                    )

            self.mesh_viewer.show_mapped_vertices(
                vertex_indices
            )

            return

        #
        # Modalità sconosciuta: per sicurezza non mostriamo
        # marker associati.
        #

        self.mesh_viewer.clear_mapped_vertices()

    # ---------------------------------------------------------

    def _get_landmark_group(
        self,
        landmark,
    ) -> str | None:
        """
        Restituisce il gruppo anatomico del landmark.

        Il catalogo standard usa nomi semantici coerenti per i
        25 Control Points. Il raggruppamento della GUI viene quindi
        ricavato da tali nomi, evitando una duplicazione degli
        indici MediaPipe.

        Gruppi restituiti
        ------------------
        face
        nose
        right_eye
        left_eye
        mouth
        right_eyebrow
        left_eyebrow
        """

        name = landmark.name

        if name in {
            "forehead_center",
            "chin",
        }:
            return "face"

        if name.startswith("nose_"):
            return "nose"

        if name.startswith("right_eye_"):
            return "right_eye"

        if name.startswith("left_eye_"):
            return "left_eye"

        if name.startswith("mouth_"):
            return "mouth"

        if name in {
            "upper_lip_center",
            "lower_lip_center",
            "upper_lip_left",
            "upper_lip_right",
        }:
            return "mouth"

        if name.startswith("right_eyebrow_"):
            return "right_eyebrow"

        if name.startswith("left_eyebrow_"):
            return "left_eyebrow"

        return None

    # ---------------------------------------------------------

    # Manteniamo il metodo per compatibilità con il flusso
    # esistente del dialog.
    def _show_existing_mapping_marker(self):
        self._refresh_mapped_markers()

    # ---------------------------------------------------------

    def _refresh_viewer_after_show(self):
        self._refresh_mapped_markers()

    def _on_show_report(self):
        dialog=MappingReportDialog(self.landmark_catalog,self.mapping_collection,self)
        dialog.exec()

    def _on_show_landmark_map(self):
        """
        Apre la mappa grafica dei landmark MediaPipe.

        La mappa rimane una finestra grafica separata
        dal MeshViewer, ma la selezione effettuata sulla
        mappa viene sincronizzata con la ComboBox del
        Vertex Mapper.

        Il mapping e la mesh non vengono modificati
        dalla semplice selezione del landmark.
        """

        dialog = MediaPipeLandmarkMapDialog(
            self
        )

        # -----------------------------------------------------
        # Sincronizzazione mappa → Vertex Mapper
        # -----------------------------------------------------

        dialog.landmark_selected.connect(
            self._on_landmark_selected_from_map
        )

        # -----------------------------------------------------
        # Allineamento iniziale della mappa
        # -----------------------------------------------------

        if self._selected_landmark_index is not None:
            dialog.select_landmark(
                self._selected_landmark_index
            )

        dialog.exec()

    # ---------------------------------------------------------
    # Landmark selected from map
    # ---------------------------------------------------------

    def _on_landmark_selected_from_map(
        self,
        landmark_index: int,
    ):
        """
        Sincronizza la selezione effettuata sulla mappa
        grafica con la ComboBox del Vertex Mapper.

        La ComboBox rimane la sorgente dello stato GUI:
        impostando il relativo indice viene infatti attivato
        il normale flusso _on_landmark_changed().
        """

        combo_index = self.landmark_combo.findData(
            int(landmark_index)
        )

        if combo_index < 0:
            return

        if (
            self.landmark_combo.currentIndex()
            != combo_index
        ):
            self.landmark_combo.setCurrentIndex(
                combo_index
            )

    # ---------------------------------------------------------

    def _on_viewport_clicked(
        self,
        x,
        y,
    ):
        """
        Gestisce il click del mouse sulla mesh.

        Le coordinate ricevute provengono direttamente dal
        GLViewWidget, quindi sono già nel sistema di coordinate
        utilizzato dal MeshPicker.
        """

        if self._selected_landmark_index is not None:

            existing_mapping = (
                self.mapping_collection.get_by_landmark(
                    self._selected_landmark_index
                )
            )

            if existing_mapping is not None:

                self.info.append(
                    ""
                )

                self.info.append(
                    "Landmark già associato: "
                    f"{existing_mapping.vertex_index}"
                )

                self.info.append(
                    "Usa 'Dissocia landmark' "
                    "per poter creare una nuova associazione."
                )

                return

        result = self.mesh_picker.pick(
            x,
            y,
        )

        # -----------------------------------------------------
        # Nessun vertice trovato
        # -----------------------------------------------------

        if result is None:

            self.info.append(
                ""
            )

            self.info.append(
                "Nessun vertice trovato."
            )

            self.info.append(
                f"Click: "
                f"({int(x)}, {int(y)})"
            )

            return

        # -----------------------------------------------------
        # Vertice trovato
        # -----------------------------------------------------

        #
        # Evidenziazione grafica.
        #

        self.mesh_viewer.select_vertex(
            result.vertex_index
        )

        #
        # Memorizzazione della selezione.
        #

        self._selected_vertex_index = (
            result.vertex_index
        )

        #
        # Creiamo un Vertex3D indipendente
        # dal risultato del picker.
        #

        self._selected_vertex = Vertex3D(
            x=result.x,
            y=result.y,
            z=result.z,
        )

        #
        # Conserviamo anche il risultato completo
        # del picking.
        #

        self._selected_pick_result = result

        # -----------------------------------------------------
        # Informazioni
        # -----------------------------------------------------

        self.info.append(
            ""
        )

        self.info.append(
            "========== VERTEX SELEZIONATO =========="
        )

        self.info.append(
            f"Index    : {result.vertex_index}"
        )

        self.info.append(
            f"X        : {result.x:.6f}"
        )

        self.info.append(
            f"Y        : {result.y:.6f}"
        )

        self.info.append(
            f"Z        : {result.z:.6f}"
        )

        self.info.append(
            f"Screen X : {result.screen_x:.2f}"
        )

        self.info.append(
            f"Screen Y : {result.screen_y:.2f}"
        )

        self.info.append(
            f"Distance : {result.distance:.2f} px"
        )

        self.info.append(
            "========================================"
        )

        self.info.append(
            "Vertice memorizzato."
        )

        #
        # Informiamo l'utente quale landmark è
        # attualmente selezionato.
        #

        landmark = (
            self.landmark_catalog.get_by_index(
                self._selected_landmark_index
            )
        )

        if landmark is not None:

            self.info.append(
                f"Landmark corrente: "
                f"{landmark.name} "
                f"({landmark.index})"
            )

        self.info.append(
            "Premi "
            "'Associa landmark → vertice' "
            "per creare la mappatura."
        )

        self._refresh_landmark_panel()
        self._refresh_progress_label()
        self._update_map_button_state()

    # ---------------------------------------------------------
    # Update map button state
    # ---------------------------------------------------------

    def _update_map_button_state(
        self,
    ):
        """
        Aggiorna lo stato dei pulsanti di associazione.

        - Landmark non associato + vertice selezionato:
          Associa abilitato.

        - Landmark associato:
          Associa disabilitato e Dissocia abilitato.

        - Landmark non associato senza vertice:
          entrambi disabilitati.
        """

        existing_mapping = None

        if self._selected_landmark_index is not None:

            existing_mapping = (
                self.mapping_collection.get_by_landmark(
                    self._selected_landmark_index
                )
            )

        landmark_is_mapped = (
            existing_mapping is not None
        )

        can_create = (
            not landmark_is_mapped
            and
            self._selected_landmark_index is not None
            and
            self._selected_vertex_index is not None
            and
            self._selected_vertex is not None
        )

        self.map_button.setEnabled(
            can_create
        )

        self.unmap_button.setEnabled(
            landmark_is_mapped
        )

    # ---------------------------------------------------------
    # Create mapping button
    # ---------------------------------------------------------

    def _on_create_mapping(
        self,
    ):
        """
        Crea una nuova VertexMapping utilizzando:

        - il landmark selezionato nella ComboBox;
        - il vertice selezionato sulla mesh.
        """

        #
        # Controllo landmark.
        #

        if (
            self._selected_landmark_index
            is None
        ):

            self.info.append(
                ""
            )

            self.info.append(
                "Nessun landmark selezionato."
            )

            return

        #
        # Recuperiamo la definizione del landmark.
        #

        landmark = (
            self.landmark_catalog.get_by_index(
                self._selected_landmark_index
            )
        )

        if landmark is None:

            self.info.append(
                ""
            )

            self.info.append(
                "Errore: definizione del landmark "
                "non trovata."
            )

            return

        #
        # Controllo vertice.
        #

        if (
            self._selected_vertex_index
            is None
            or
            self._selected_vertex is None
        ):

            self.info.append(
                ""
            )

            self.info.append(
                "Nessun vertice selezionato."
            )

            return

        # -----------------------------------------------------
        # Creazione mapping
        # -----------------------------------------------------

        try:

            mapping = self.create_mapping(
                landmark_index=(
                    landmark.index
                ),
                landmark_name=(
                    landmark.name
                ),
            )

        except ValueError as error:

            #
            # Il ValueError viene generato dalla
            # VertexMappingCollection quando:
            #
            # - il landmark è già mappato;
            # - il vertice è già utilizzato.
            #

            self.info.append(
                ""
            )

            self.info.append(
                "========== MAPPING NON CREATO =========="
            )

            self.info.append(
                str(error)
            )

            self.info.append(
                "========================================="
            )

            return

        except RuntimeError as error:

            self.info.append(
                ""
            )

            self.info.append(
                "========== MAPPING NON CREATO =========="
            )

            self.info.append(
                str(error)
            )

            self.info.append(
                "========================================="
            )

            return

        # -----------------------------------------------------
        # Mapping creato correttamente
        # -----------------------------------------------------

        self.info.append(
            ""
        )

        self.info.append(
            "Mapping creato correttamente."
        )

        #
        # La selezione del vertice è temporanea.
        #
        # Dopo aver creato con successo la mappatura
        # non deve più rimanere attiva:
        #
        # - rimuoviamo il marker rosso dal viewer;
        # - azzeriamo l'indice del vertice;
        # - azzeriamo il Vertex3D temporaneo;
        # - azzeriamo il risultato del picking.
        #
        # Il landmark rimane invece selezionato nella ComboBox,
        # così l'utente può selezionare il vertice successivo.
        #

        self.mesh_viewer.clear_selected_vertex()

        self._selected_vertex_index = None
        self._selected_vertex = None
        self._selected_pick_result = None

        #
        # Ora il pulsante deve tornare disabilitato.
        # Si riabiliterà soltanto dopo una nuova selezione
        # di un vertice.
        #

        self._refresh_landmark_panel()
        self._refresh_progress_label()
        self._update_map_button_state()
        self._refresh_mapped_markers()

    # ---------------------------------------------------------
    # Remove mapping
    # ---------------------------------------------------------

    def _on_remove_mapping(
        self,
    ):
        """
        Rimuove la mappatura del landmark attualmente selezionato.
        """

        if self._selected_landmark_index is None:

            return

        mapping = (
            self.mapping_collection.get_by_landmark(
                self._selected_landmark_index
            )
        )

        if mapping is None:

            self.info.append(
                ""
            )

            self.info.append(
                "Il landmark selezionato non è associato."
            )

            self._update_map_button_state()

            return

        removed = (
            self.mapping_collection.remove_by_landmark(
                self._selected_landmark_index
            )
        )

        if not removed:

            self.info.append(
                ""
            )

            self.info.append(
                "Impossibile rimuovere la mappatura."
            )

            self._update_map_button_state()

            return

        #
        # La selezione grafica del vertice è temporanea.
        #

        self.mesh_viewer.clear_selected_vertex()

        self._selected_vertex_index = None
        self._selected_vertex = None
        self._selected_pick_result = None

        self.info.append(
            ""
        )

        self.info.append(
            "========== MAPPING RIMOSSO =========="
        )

        self.info.append(
            f"Landmark : {mapping.landmark_index}"
        )

        if mapping.landmark_name:

            self.info.append(
                f"Nome     : {mapping.landmark_name}"
            )

        self.info.append(
            f"Vertex   : {mapping.vertex_index}"
        )

        self.info.append(
            f"Totale mapping: "
            f"{self.mapping_collection.count()}"
        )

        self.info.append(
            "====================================="
        )

        self.info.append(
            "Il landmark è nuovamente disponibile "
            "per una nuova associazione."
        )

        self._refresh_landmark_panel()
        self._refresh_progress_label()
        self._update_map_button_state()
        self._refresh_mapped_markers()

    # ---------------------------------------------------------
    # Selected vertex
    # ---------------------------------------------------------

    def get_selected_vertex_index(self):
        """
        Restituisce l'indice dell'ultimo vertice selezionato.

        Returns
        -------
        int | None
        """

        return self._selected_vertex_index

    # ---------------------------------------------------------

    def get_selected_vertex(self):
        """
        Restituisce il Vertex3D dell'ultimo vertice selezionato.

        Returns
        -------
        Vertex3D | None
        """

        return self._selected_vertex

    # ---------------------------------------------------------

    def get_selected_pick_result(self):
        """
        Restituisce il risultato completo dell'ultimo picking.

        Returns
        -------
        PickResult | None
        """

        return self._selected_pick_result

    # ---------------------------------------------------------
    # Selected landmark
    # ---------------------------------------------------------

    def get_selected_landmark_index(self):
        """
        Restituisce l'indice MediaPipe attualmente selezionato.

        Returns
        -------
        int | None
        """

        return self._selected_landmark_index

    # ---------------------------------------------------------

    def get_selected_landmark(self):
        """
        Restituisce la definizione del landmark
        attualmente selezionato.

        Returns
        -------
        LandmarkDefinition | None
        """

        if self._selected_landmark_index is None:

            return None

        return (
            self.landmark_catalog.get_by_index(
                self._selected_landmark_index
            )
        )

    # ---------------------------------------------------------
    # Create mapping
    # ---------------------------------------------------------

    def create_mapping(
        self,
        landmark_index: int,
        landmark_name: str = "",
    ):
        """
        Crea una VertexMapping utilizzando il vertice
        attualmente selezionato.

        Parameters
        ----------
        landmark_index:
            Indice del landmark MediaPipe.

        landmark_name:
            Nome opzionale del landmark.

        Returns
        -------
        VertexMapping

        Raises
        ------
        RuntimeError
            Se non è stato selezionato alcun vertice.
        """

        #
        # Controllo selezione.
        #

        if (
            self._selected_vertex_index
            is None
        ):

            raise RuntimeError(
                "Nessun vertice selezionato."
            )

        if (
            self._selected_vertex
            is None
        ):

            raise RuntimeError(
                "Coordinate del vertice "
                "selezionato non disponibili."
            )

        #
        # Creazione della mappatura.
        #

        mapping = VertexMapping(
            landmark_index=landmark_index,
            landmark_name=landmark_name,
            vertex_index=(
                self._selected_vertex_index
            ),
            vertex=self._selected_vertex,
        )

        #
        # Inserimento nella collection.
        #

        self.mapping_collection.add(
            mapping
        )

        #
        # Aggiornamento informazioni.
        #

        self.info.append(
            ""
        )

        self.info.append(
            "========== MAPPING CREATO =========="
        )

        self.info.append(
            f"Landmark : {landmark_index}"
        )

        if landmark_name:

            self.info.append(
                f"Nome     : {landmark_name}"
            )

        self.info.append(
            f"Vertex   : "
            f"{self._selected_vertex_index}"
        )

        self.info.append(
            f"Totale mapping: "
            f"{self.mapping_collection.count()}"
        )

        self.info.append(
            "===================================="
        )

        return mapping