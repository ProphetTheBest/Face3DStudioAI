"""
==========================================================
Face3D Studio AI

New Reconstruction Dialog
==========================================================
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from source.models.assets.image_asset import ImageAsset
from source.services.canonical.canonical_asset_loader import CanonicalAssetLoader
from source.services.canonical.canonical_asset_repository import CanonicalAssetRepository


class NewReconstructionDialog(QDialog):
    """
    Crea una nuova elaborazione/Subject associando una o più
    immagini del progetto a un Canonical Asset della Library.
    """

    DEFAULT_CANONICAL_ASSET_ID = "makehuman_male1591_head"
    DEFAULT_CANONICAL_ASSET_TYPE = "HEAD"

    def __init__(self, project, parent=None):
        super().__init__(parent)
        self._project = project
        self._selected_canonical_asset = None

        self.setWindowTitle("New Reconstruction")
        self.resize(650, 280)

        self.name_edit = QLineEdit()
        self.image_combo = QComboBox()
        self.canonical_combo = QComboBox()

        self.asset_info = QLabel()
        self.asset_info.setWordWrap(True)

        form = QFormLayout()
        form.addRow("Subject name:", self.name_edit)
        form.addRow("Source photo:", self.image_combo)
        form.addRow("Canonical Asset:", self.canonical_combo)
        form.addRow("Asset details:", self.asset_info)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.button(QDialogButtonBox.Ok).setText("Create")
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addStretch()
        layout.addWidget(buttons)

        self._populate_images()
        self._populate_canonical_assets()

        self.canonical_combo.currentIndexChanged.connect(
            self._canonical_changed
        )

        if self.canonical_combo.currentIndex() >= 0:
            self._canonical_changed(
                self.canonical_combo.currentIndex()
            )

    def _populate_images(self) -> None:
        self.image_combo.clear()

        for asset in self._project.assets:
            if not isinstance(asset, ImageAsset):
                continue

            self.image_combo.addItem(
                asset.filename,
                asset.id,
            )

    def _populate_canonical_assets(self) -> None:
        self.canonical_combo.clear()

        repository = CanonicalAssetRepository(
            CanonicalAssetLoader.CANONICAL_ROOT
        )

        asset_ids = repository.list_assets("HEAD")

        if not asset_ids:
            self.canonical_combo.addItem(
                "No HEAD Canonical Asset available",
                None,
            )
            return

        preferred = (
            self.DEFAULT_CANONICAL_ASSET_ID
            if self.DEFAULT_CANONICAL_ASSET_ID in asset_ids
            else asset_ids[0]
        )

        ordered = [preferred] + [
            asset_id for asset_id in asset_ids
            if asset_id != preferred
        ]

        for asset_id in ordered:
            try:
                asset = CanonicalAssetLoader.load(
                    asset_id,
                    "HEAD",
                )
            except Exception:
                continue

            self.canonical_combo.addItem(
                asset.name,
                (asset.asset_id, asset.asset_type),
            )

    def _canonical_changed(self, index: int) -> None:
        data = self.canonical_combo.itemData(index)

        if not data:
            self._selected_canonical_asset = None
            self.asset_info.setText("No valid Canonical Asset selected.")
            return

        asset_id, asset_type = data

        try:
            asset = CanonicalAssetLoader.load(
                asset_id,
                asset_type,
            )
        except Exception as exc:
            self._selected_canonical_asset = None
            self.asset_info.setText(str(exc))
            return

        self._selected_canonical_asset = asset

        mesh = asset.canonical_mesh
        mapping = asset.canonical_mapping

        self.asset_info.setText(
            f"ID: {asset.asset_id}\n"
            f"Type: {asset.asset_type}\n"
            f"Version: {asset.version}\n"
            f"Vertices: {len(mesh.vertices) if mesh else 0}\n"
            f"Triangles: {len(mesh.triangles) if mesh else 0}\n"
            f"Mapping: {mapping.count() if mapping else 0}"
        )

    def _accept(self) -> None:
        if not self.name_edit.text().strip():
            QMessageBox.warning(
                self,
                "New Reconstruction",
                "Enter a subject name.",
            )
            return

        if self.image_combo.currentData() is None:
            QMessageBox.warning(
                self,
                "New Reconstruction",
                "Select a source photo.",
            )
            return

        if self._selected_canonical_asset is None:
            QMessageBox.warning(
                self,
                "New Reconstruction",
                "Select a valid Canonical Asset.",
            )
            return

        self.accept()

    def subject_name(self) -> str:
        return self.name_edit.text().strip()

    def source_asset_id(self) -> str:
        return str(self.image_combo.currentData())

    def canonical_asset_id(self) -> str:
        return self._selected_canonical_asset.asset_id

    def canonical_asset_type(self) -> str:
        return self._selected_canonical_asset.asset_type

    def canonical_asset_version(self) -> str:
        return self._selected_canonical_asset.version
