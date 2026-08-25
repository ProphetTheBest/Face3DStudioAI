"""
==========================================================
Face3D Studio AI

Project Tree Widget

Visualizza la struttura gerarchica del progetto.

Autore:
Marco Cantù

Versione:
1.1.0
==========================================================
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem


class ProjectTreeWidget(QTreeWidget):
    """
    Albero del progetto.

    Il widget mantiene la compatibilità con la struttura precedente,
    ma supporta anche una rappresentazione gerarchica delle fotografie
    organizzate per Subject.

    Struttura prevista:

        Project
        ├── Photos
        │   ├── Subject
        │   │   ├── Photo
        │   │   └── Canonical Asset
        │   └── Subject
        │       └── Photo
        ├── Videos
        ├── Frames
        ├── Landmarks
        ├── Meshes
        └── Exports

    La singola fotografia continua ad avere il proprio asset_id
    memorizzato in Qt.UserRole, quindi la selezione della fotografia
    rimane compatibile con il comportamento esistente.
    """

    def __init__(self) -> None:
        super().__init__()

        self._create_tree()

    # ---------------------------------------------------------
    # CREAZIONE ALBERO
    # ---------------------------------------------------------

    def _create_tree(self) -> None:
        """
        Costruisce la struttura iniziale del progetto.
        """

        self.setHeaderHidden(True)

        self.project_item = QTreeWidgetItem(["📁 Untitled"])
        self.addTopLevelItem(self.project_item)

        self.photos_item = self._create_folder_item("📷 Photos")
        self.videos_item = self._create_folder_item("🎥 Videos")
        self.frames_item = self._create_folder_item("🖼 Frames")
        self.landmarks_item = self._create_folder_item("🧠 Landmarks")
        self.meshes_item = self._create_folder_item("🔺 Meshes")
        self.exports_item = self._create_folder_item("📦 Exports")

        self.project_item.setExpanded(True)

        self.update_counts()

    # ---------------------------------------------------------
    # FOLDER
    # ---------------------------------------------------------

    def _create_folder_item(self, text: str) -> QTreeWidgetItem:
        """
        Crea una voce cartella principale.
        """

        item = QTreeWidgetItem([f"{text} (0)"])
        self.project_item.addChild(item)

        return item

    # ---------------------------------------------------------
    # PROJECT NAME
    # ---------------------------------------------------------

    def set_project_name(self, name: str) -> None:
        """
        Imposta il nome del progetto.
        """

        self.project_item.setText(
            0,
            f"📁 {name}"
        )

    # ---------------------------------------------------------
    # COUNTS
    # ---------------------------------------------------------

    def update_counts(
        self,
        photos: int = 0,
        videos: int = 0,
        frames: int = 0,
        landmarks: int = 0,
        meshes: int = 0,
        exports: int = 0,
    ) -> None:
        """
        Aggiorna i contatori delle cartelle principali.
        """

        self.photos_item.setText(
            0,
            f"📷 Photos ({photos})"
        )

        self.videos_item.setText(
            0,
            f"🎥 Videos ({videos})"
        )

        self.frames_item.setText(
            0,
            f"🖼 Frames ({frames})"
        )

        self.landmarks_item.setText(
            0,
            f"🧠 Landmarks ({landmarks})"
        )

        self.meshes_item.setText(
            0,
            f"🔺 Meshes ({meshes})"
        )

        self.exports_item.setText(
            0,
            f"📦 Exports ({exports})"
        )

    # ---------------------------------------------------------
    # PHOTOS
    # ---------------------------------------------------------

    def set_photos(self, photos) -> None:
        """
        Imposta le fotografie del progetto.

        Formato legacy supportato:

            [
                (filename, asset_id),
                ...
            ]

        Formato esteso supportato:

            [
                (
                    filename,
                    asset_id,
                    subject_name,
                    canonical_asset_name
                ),
                ...
            ]

        Esempio:

            [
                (
                    "papa_01.jpg",
                    "image_001",
                    "Papà",
                    "MakeHuman Male 1591 Head"
                ),
                (
                    "papa_02.jpg",
                    "image_002",
                    "Papà",
                    "MakeHuman Male 1591 Head"
                ),
                (
                    "figlio_01.jpg",
                    "image_003",
                    "Figlio",
                    "MakeHuman Child Head"
                ),
            ]

        Se vengono utilizzati tuple legacy a due elementi, il
        comportamento rimane quello precedente.

        Se sono presenti Subject, le fotografie vengono raggruppate
        gerarchicamente per Subject.
        """

        self.photos_item.takeChildren()

        if not photos:
            self.photos_item.setText(
                0,
                "📷 Photos (0)"
            )
            return

        # -----------------------------------------------------
        # RICONOSCIMENTO FORMATO
        # -----------------------------------------------------

        has_subject_information = any(
            len(photo) >= 3 and photo[2]
            for photo in photos
        )

        # -----------------------------------------------------
        # COMPATIBILITÀ LEGACY
        # -----------------------------------------------------

        if not has_subject_information:
            self._set_legacy_photos(photos)
            return

        # -----------------------------------------------------
        # STRUTTURA PER SUBJECT
        # -----------------------------------------------------

        subjects = {}

        for photo in photos:

            filename = photo[0]
            asset_id = photo[1]

            subject_name = (
                photo[2]
                if len(photo) >= 3 and photo[2]
                else "Senza Subject"
            )

            canonical_name = (
                photo[3]
                if len(photo) >= 4 and photo[3]
                else None
            )

            if subject_name not in subjects:
                subjects[subject_name] = {
                    "photos": [],
                    "canonical": canonical_name,
                }

            subjects[subject_name]["photos"].append(
                (
                    filename,
                    asset_id,
                )
            )

            # Se una fotografia successiva contiene
            # l'informazione Canonical Asset e quella precedente
            # non la conteneva, conserviamo quella disponibile.
            if (
                canonical_name
                and not subjects[subject_name]["canonical"]
            ):
                subjects[subject_name]["canonical"] = canonical_name

        # -----------------------------------------------------
        # CREAZIONE NODI SUBJECT
        # -----------------------------------------------------

        for subject_name, subject_data in subjects.items():

            subject_item = QTreeWidgetItem(
                [
                    f"👤 {subject_name}"
                ]
            )

            self.photos_item.addChild(subject_item)

            # -------------------------------------------------
            # FOTOGRAFIE DEL SUBJECT
            # -------------------------------------------------

            for filename, asset_id in subject_data["photos"]:

                photo_item = QTreeWidgetItem(
                    [
                        f"    {filename}"
                    ]
                )

                photo_item.setData(
                    0,
                    Qt.UserRole,
                    asset_id
                )

                subject_item.addChild(photo_item)

            # -------------------------------------------------
            # CANONICAL ASSET
            # -------------------------------------------------

            canonical_name = subject_data["canonical"]

            if canonical_name:

                canonical_item = QTreeWidgetItem(
                    [
                        f"    🔷 Canonical Asset: "
                        f"{canonical_name}"
                    ]
                )

                # Il nodo Canonical Asset NON rappresenta una
                # fotografia e quindi non deve avere asset_id.
                canonical_item.setData(
                    0,
                    Qt.UserRole,
                    None
                )

                subject_item.addChild(canonical_item)

            subject_item.setExpanded(True)

        self.photos_item.setText(
            0,
            f"📷 Photos ({len(photos)})"
        )

        self.photos_item.setExpanded(True)

    # ---------------------------------------------------------
    # LEGACY PHOTOS
    # ---------------------------------------------------------

    def _set_legacy_photos(self, photos) -> None:
        """
        Mantiene esattamente la vecchia rappresentazione quando
        il chiamante fornisce solamente:

            (filename, asset_id)
        """

        for filename, asset_id in photos:

            item = QTreeWidgetItem(
                [
                    filename
                ]
            )

            item.setData(
                0,
                Qt.UserRole,
                asset_id
            )

            self.photos_item.addChild(item)

        self.photos_item.setText(
            0,
            f"📷 Photos ({len(photos)})"
        )

        self.photos_item.setExpanded(True)

    # ---------------------------------------------------------
    # CURRENT ASSET
    # ---------------------------------------------------------

    def current_asset_id(self) -> str | None:
        """
        Restituisce l'id dell'asset selezionato.

        Solo le fotografie possiedono un asset_id.
        Subject e Canonical Asset restituiscono None.
        """

        item = self.currentItem()

        if item is None:
            return None

        return item.data(
            0,
            Qt.UserRole
        )

    # ---------------------------------------------------------
    # CLEAR
    # ---------------------------------------------------------

    def clear_project(self) -> None:
        """
        Svuota il contenuto del progetto mantenendo la struttura
        principale dell'albero.
        """

        self.set_project_name("Untitled")

        self.photos_item.takeChildren()

        self.update_counts()