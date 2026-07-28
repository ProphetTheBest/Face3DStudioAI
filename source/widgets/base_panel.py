"""
==========================================================
Face3D Studio AI

Base Panel

Classe base di tutti i pannelli della GUI.

Autore:
Marco Cantù

Versione:
0.1.1
==========================================================
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QFrame,
    QVBoxLayout,
    QWidget,
)


class BasePanel(QFrame):
    """
    Classe base di tutti i pannelli dell'applicazione.

    Tutti i pannelli della GUI erediteranno
    da questa classe.
    """

    def __init__(self, title: str) -> None:
        """
        Costruttore.

        Parameters
        ----------
        title : str
            Titolo del pannello.
        """

        super().__init__()

        self.title = title

        self._create_ui()

    # ---------------------------------------------------------

    def _create_ui(self) -> None:
        """
        Costruisce l'interfaccia grafica del pannello.
        """

        self.setFrameShape(QFrame.Shape.Box)

        self.main_layout = QVBoxLayout()

        self.lbl_title = QLabel(self.title)
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.main_layout.addWidget(self.lbl_title)

        self.setLayout(self.main_layout)

    # ---------------------------------------------------------

    def add_content_widget(self, widget: QWidget) -> None:
        """
        Aggiunge un widget al contenuto del pannello.

        Parameters
        ----------
        widget : QWidget
            Widget da inserire nel pannello.
        """

        self.main_layout.addWidget(widget)