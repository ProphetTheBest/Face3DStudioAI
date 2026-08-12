"""Face3D Studio AI - Mapping Report Dialog - Versione 1.0.0"""

from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout,
)


class MappingReportDialog(QDialog):
    """Mostra lo stato corrente delle associazioni landmark -> vertice."""

    def __init__(self, landmark_catalog, mapping_collection, parent=None):
        super().__init__(parent)
        self.landmark_catalog = landmark_catalog
        self.mapping_collection = mapping_collection
        self.setWindowTitle("Face3D Studio - Report Mappatura")
        self.resize(850, 650)

        layout=QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Report mappatura landmark → vertice</h2>"))
        self.summary=QLabel()
        layout.addWidget(self.summary)

        self.table=QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Indice","Landmark","Stato","Vertex","X","Y","Z"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table,1)

        buttons=QHBoxLayout()
        buttons.addStretch()
        close_button=QPushButton("Chiudi")
        close_button.clicked.connect(self.close)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)
        self._populate()

    def _populate(self):
        landmarks=self.landmark_catalog.all()
        self.table.setRowCount(len(landmarks))
        mapped_count=self.mapping_collection.count()
        self.summary.setText(f"<b>{mapped_count} / {len(landmarks)} landmark associati</b>")
        for row, landmark in enumerate(landmarks):
            mapping=self.mapping_collection.get_by_landmark(landmark.index)
            values=[
                str(landmark.index), landmark.name,
                "ASSOCIATO" if mapping is not None else "NON ASSOCIATO",
                str(mapping.vertex_index) if mapping is not None else "—",
                f"{mapping.vertex.x:.6f}" if mapping is not None and mapping.vertex is not None else "—",
                f"{mapping.vertex.y:.6f}" if mapping is not None and mapping.vertex is not None else "—",
                f"{mapping.vertex.z:.6f}" if mapping is not None and mapping.vertex is not None else "—",
            ]
            for column,value in enumerate(values):
                self.table.setItem(row,column,QTableWidgetItem(value))
        self.table.resizeColumnsToContents()
