"""
==========================================================
Face3D Studio AI

Project Tree Widget

Visualizza la struttura del progetto.

Autore:
Marco Cantù

Versione:
0.1.2
==========================================================
"""

from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt, Signal

class ProjectTreeWidget(QTreeWidget):
    """
    Albero del progetto.
    """
    photo_selected = Signal(str)

    def __init__(self) -> None:

        super().__init__()

        self._create_tree()
        self.itemClicked.connect(self._on_item_clicked)
    # ---------------------------------------------------------

    def _create_tree(self) -> None:
        """
        Costruisce la struttura iniziale.
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

    def _create_folder_item(self, text: str) -> QTreeWidgetItem:
        """
        Crea un nodo figlio del progetto.
        """

        item = QTreeWidgetItem([f"{text} (0)"])

        self.project_item.addChild(item)

        return item

    # ---------------------------------------------------------

    def set_project_name(self, name: str) -> None:
        """
        Aggiorna il nome del progetto.
        """

        self.project_item.setText(0, f"📁 {name}")

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
        Aggiorna i contatori delle cartelle.
        """

        self.photos_item.setText(0, f"📷 Photos ({photos})")
        self.videos_item.setText(0, f"🎥 Videos ({videos})")
        self.frames_item.setText(0, f"🖼 Frames ({frames})")
        self.landmarks_item.setText(0, f"🧠 Landmarks ({landmarks})")
        self.meshes_item.setText(0, f"🔺 Meshes ({meshes})")
        self.exports_item.setText(0, f"📦 Exports ({exports})")

    # ---------------------------------------------------------

    def set_photos(self, photos) -> None:
        """
        Aggiorna il contenuto della cartella Photos.

        photos:
            [
                ("IMG001.jpg", "C:/.../IMG001.jpg"),
                ...
            ]
        """

        self.photos_item.takeChildren()

        for filename, full_path in photos:

            item = QTreeWidgetItem([filename])

            item.setData(0, Qt.UserRole, full_path)

            self.photos_item.addChild(item)

        self.photos_item.setText(
            0,
            f"📷 Photos ({len(photos)})"
        )

        self.photos_item.setExpanded(True)

    def clear_project(self) -> None:
        """
        Ripristina il contenuto dell'albero.
        """

        self.set_project_name("Untitled")

        self.update_counts()

    # ---------------------------------------------------------

    def _on_item_clicked(self, item, column):
        """
        Gestisce il click su un elemento dell'albero.
        """

        path = item.data(0, Qt.UserRole)

        if path:

            self.photo_selected.emit(path)