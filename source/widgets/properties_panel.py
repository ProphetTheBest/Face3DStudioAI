"""
==========================================================
Face3D Studio AI

Properties Panel

Autore:
Marco Cantù

Versione:
0.2.1
==========================================================
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QWidget,
)

from source.models.assets.asset import Asset
from source.widgets.base_panel import BasePanel


class PropertiesPanel(BasePanel):

    def __init__(self):

        super().__init__("PROPERTIES")

        self._create_properties_ui()

    # ---------------------------------------------------------

    def _create_properties_ui(self):

        container = QWidget()

        layout = QFormLayout(container)

        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.lbl_name = QLabel("-")
        self.lbl_type = QLabel("-")
        self.lbl_format = QLabel("-")
        self.lbl_resolution = QLabel("-")
        self.lbl_size = QLabel("-")
        self.lbl_path = QLabel("-")

        self.lbl_path.setWordWrap(True)

        layout.addRow("Name", self.lbl_name)
        layout.addRow("Type", self.lbl_type)
        layout.addRow("Format", self.lbl_format)
        layout.addRow("Resolution", self.lbl_resolution)
        layout.addRow("File size", self.lbl_size)
        layout.addRow("Relative path", self.lbl_path)

        self.add_content_widget(container)

    # ---------------------------------------------------------

    def clear(self):

        self.lbl_name.setText("-")
        self.lbl_type.setText("-")
        self.lbl_format.setText("-")
        self.lbl_resolution.setText("-")
        self.lbl_size.setText("-")
        self.lbl_path.setText("-")

    # ---------------------------------------------------------

    def show_asset(self, asset: Asset | None):

        self.clear()

        if asset is None:
            return

        #
        # Nome
        #

        self.lbl_name.setText(asset.filename)

        #
        # Tipo
        #

        self.lbl_type.setText(
            asset.asset_type.value.capitalize()
        )

        #
        # Formato
        #

        self.lbl_format.setText(
            asset.extension.replace(".", "").upper()
        )

        #
        # Percorso relativo
        #

        self.lbl_path.setText(
            str(asset.relative_path)
        )

        #
        # Saranno compilati nella prossima milestone
        #

        self.lbl_resolution.setText("-")

        self.lbl_size.setText("-")