"""
==========================================================
Face3D Studio AI

File:
new_project_dialog.py

Descrizione:
Dialog per la creazione di un nuovo progetto.

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
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
        self.resize(600, 180)

        self._project_folder = ""

        # -------------------------------------------------
        # Widgets
        # -------------------------------------------------

        self.project_name_edit = QLineEdit()

        self.location_edit = QLineEdit()
        self.location_edit.setReadOnly(True)

        self.browse_button = QPushButton("Browse...")

        # -------------------------------------------------
        # Layout Location
        # -------------------------------------------------

        location_layout = QHBoxLayout()

        location_layout.addWidget(self.location_edit)
        location_layout.addWidget(self.browse_button)

        # -------------------------------------------------
        # Form
        # -------------------------------------------------

        form_layout = QFormLayout()

        form_layout.addRow(
            "Project name:",
            self.project_name_edit
        )

        form_layout.addRow(
            "Location:",
            location_layout
        )

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok |
            QDialogButtonBox.Cancel
        )

        self.ok_button = self.button_box.button(
            QDialogButtonBox.Ok
        )
        
        self.ok_button.setText("Create")
        self.ok_button.setEnabled(False)

        # -------------------------------------------------
        # Main Layout
        # -------------------------------------------------

        layout = QVBoxLayout(self)

        layout.addLayout(form_layout)
        layout.addStretch()
        layout.addWidget(self.button_box)

        # -------------------------------------------------
        # Signals
        # -------------------------------------------------

        self.browse_button.clicked.connect(
            self._on_browse
        )

        self.project_name_edit.textChanged.connect(
            self._update_ok_button
        )

        self.button_box.accepted.connect(
            self.accept
        )

        self.button_box.rejected.connect(
            self.reject
        )

    # =====================================================
    # Slots
    # =====================================================

    def _on_browse(self):
        """
        Seleziona la cartella del progetto.
        """

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Project Folder"
        )

        if not folder:
            return

        self._project_folder = folder

        self.location_edit.setText(folder)

        self._update_ok_button()

    # =====================================================

    def _update_ok_button(self):
        """
        Abilita il pulsante Create solo quando il dialog è valido.
        """
        enabled = (
            self.project_name_edit.text().strip() != ""
            and
            self._project_folder != ""
        )

        self.ok_button.setEnabled(enabled)

    # =====================================================
    # Public API
    # =====================================================

    def project_name(self) -> str:
        """
        Restituisce il nome del progetto.
        """

        return self.project_name_edit.text().strip()

    # -----------------------------------------------------

    def project_folder(self) -> str:
        """
        Restituisce la cartella scelta.
        """

        return self._project_folder