"""
==========================================================
Face3D Studio AI

File:
face_diagnostics_dialog.py

Descrizione:
Finestra di diagnostica del volto corrente.

Autore:
Marco Cantù

==========================================================
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

# from source.analysis.geometry.geometry_analyzer import GeometryAnalyzer
# from source.analysis.landmarks.landmark_analyzer import LandmarkAnalyzer


class FaceDiagnosticsDialog(QDialog):
    """
    Visualizza tutte le informazioni diagnostiche
    del Current Face.
    """

    # ---------------------------------------------------------

    def __init__(
        self,
        diagnostics_report,
        parent=None,
    ):

        super().__init__(parent)

        self._report = diagnostics_report

        self.setWindowTitle("Face Diagnostics")

        self.resize(700, 550)

        self._create_ui()

        self._populate()

    # ---------------------------------------------------------

    def _create_ui(self):

        layout = QVBoxLayout(self)

        self._tree = QTreeWidget()

        self._tree.setColumnCount(2)

        self._tree.setHeaderLabels(
            [
                "Property",
                "Value",
            ]
        )

        self._tree.header().setSectionResizeMode(
            0,
            QHeaderView.Stretch,
        )

        self._tree.header().setSectionResizeMode(
            1,
            QHeaderView.ResizeToContents,
        )

        layout.addWidget(
            self._tree
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.Close
        )

        buttons.rejected.connect(
            self.reject
        )

        layout.addWidget(
            buttons
        )

    # ---------------------------------------------------------

    def _populate(self):

        geometry = self._report.geometry

        landmarks = self._report.landmarks

        geometry_item = QTreeWidgetItem(
            self._tree,
            ["Geometry"]
        )

        self._add_property(
            geometry_item,
            "Vertices",
            geometry.vertex_count,
        )

        self._add_property(
            geometry_item,
            "Triangles",
            geometry.triangle_count,
        )

        self._add_property(
            geometry_item,
            "Width",
            f"{geometry.width:.6f}",
        )

        self._add_property(
            geometry_item,
            "Height",
            f"{geometry.height:.6f}",
        )

        self._add_property(
            geometry_item,
            "Depth",
            f"{geometry.depth:.6f}",
        )

        self._add_property(
            geometry_item,
            "Aspect XY",
            f"{geometry.aspect_xy:.6f}",
        )

        landmark_item = QTreeWidgetItem(
            self._tree,
            ["Landmarks"]
        )

        self._add_property(
            landmark_item,
            "Count",
            landmarks.landmark_count,
        )

        self._add_property(
            landmark_item,
            "Width",
            f"{landmarks.width:.6f}",
        )

        self._add_property(
            landmark_item,
            "Height",
            f"{landmarks.height:.6f}",
        )

        self._add_property(
            landmark_item,
            "Aspect XY",
            f"{landmarks.aspect_xy:.6f}",
        )

        status_item = QTreeWidgetItem(
            self._tree,
            ["Status"]
        )

        self._add_property(
            status_item,
            "Geometry",
            "OK",
        )

        if abs(
            geometry.aspect_xy -
            landmarks.aspect_xy
        ) < 0.000001:

            result = "MATCH"

        else:

            result = "DIFFERENT"

        self._add_property(
            status_item,
            "Aspect Ratio",
            result,
        )

        self._tree.expandAll()

    # ---------------------------------------------------------

    @staticmethod
    def _add_property(
        parent,
        name,
        value,
    ):

        QTreeWidgetItem(
            parent,
            [
                str(name),
                str(value),
            ]
        )