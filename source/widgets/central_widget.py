"""
==========================================================
Face3D Studio AI

File:
central_widget.py

Descrizione:
Widget centrale dell'applicazione.

Autore:
Marco Cantù

Versione:
0.3.2
==========================================================
"""

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
)

from source.controllers.application_controller import ApplicationController

from source.widgets.project_panel import ProjectPanel
from source.widgets.viewer_panel import ViewerPanel
from source.widgets.properties_panel import PropertiesPanel
from source.widgets.log_panel import LogPanel


class CentralWidget(QWidget):
    """
    Widget centrale dell'applicazione.
    """

    def __init__(self, app_controller: ApplicationController) -> None:

        super().__init__()

        self.app_controller = app_controller

        self._create_widgets()

        self._create_layout()

    # ---------------------------------------------------------

    def _create_widgets(self) -> None:
        """
        Crea tutti i pannelli dell'interfaccia.
        """

        project_controller = (
            self.app_controller.get_project_controller()
        )

        self.project_panel = ProjectPanel(
            project_controller
        )

        self.viewer_panel = ViewerPanel(
            project_controller
        )

        self.properties_panel = PropertiesPanel()

        self.log_panel = LogPanel()

        #
        # Il Viewer viene aggiornato SOLO dopo che
        # il ProjectPanel ha aggiornato il current_asset.
        #

        self.project_panel.asset_selected.connect(
            self.viewer_panel.show_current_asset
        )

    # ---------------------------------------------------------

    def _create_layout(self) -> None:
        """
        Costruisce il layout principale.
        """

        right_layout = QVBoxLayout()

        right_layout.addWidget(
            self.viewer_panel,
            8,
        )

        right_layout.addWidget(
            self.log_panel,
            2,
        )

        main_layout = QHBoxLayout()

        main_layout.addWidget(
            self.project_panel,
            2,
        )

        main_layout.addLayout(
            right_layout,
            6,
        )

        main_layout.addWidget(
            self.properties_panel,
            2,
        )

        self.setLayout(main_layout)