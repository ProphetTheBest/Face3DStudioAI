"""
==========================================================
Face3D Studio AI

File:
diagnostics_controller.py

Descrizione:
Controller della diagnostica del volto corrente.

Autore:
Marco Cantù

==========================================================
"""

from source.gui.dialogs.diagnostics.face_diagnostics_dialog import (
    FaceDiagnosticsDialog,
)

from source.services.diagnostics.face_diagnostics_service import (
    FaceDiagnosticsService,
)


class DiagnosticsController:
    """
    Gestisce l'apertura della finestra
    Face Diagnostics.
    """

    # ---------------------------------------------------------

    @staticmethod
    def show(face, parent=None):
        """
        Visualizza la finestra di diagnostica
        del volto corrente.
        """

        if face is None:
            return

        report = FaceDiagnosticsService.create_report(
            face
        )

        dialog = FaceDiagnosticsDialog(
            report,
            parent,
        )

        dialog.exec()