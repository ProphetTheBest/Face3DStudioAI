"""
==========================================================
Face3D Studio AI

New Project Dialog

Autore:
Marco Cantù

Versione:
0.1.0
==========================================================
"""

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class NewProjectDialog(QDialog):
    """
    Dialog per la creazione di un nuovo progetto.
    """

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle("New Project")
        self.resize(550, 180)

        #
        # Widgets
        #

        self.project_name_edit = QLineEdit()

        self.location_edit = QLineEdit()

        self.location_edit.setReadOnly(True)

        self.browse_button = QPushButton("Browse...")

        #
        # Layout posizione
        #

        location_layout = QHBoxLayout()

        location_layout.addWidget(self.location_edit)

        location_layout.addWidget(self.browse_button)

        #
        # Form
        #

        form = QFormLayout()

        form.addRow("Project name:", self.project_name_edit)

        form.addRow("Location:", location_layout)

        #
        # Bottoni
        #

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok |
            QDialogButtonBox.Cancel
        )

        buttons.accepted.connect(self.accept)

        buttons.rejected.connect(self.reject)

        #
        # Layout principale
        #

        layout = QVBoxLayout(self)

        layout.addLayout(form)

        layout.addStretch()

        layout.addWidget(buttons)