"""
==========================================================
Face3D Studio AI

Image Scene

Autore:
Marco Cantù

Versione:
0.2.0
==========================================================
"""

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QGraphicsPixmapItem,
    QGraphicsScene,
)


class ImageScene(QGraphicsScene):
    """
    Scena grafica contenente tutti gli elementi
    visualizzati nel Viewer.
    """

    def __init__(self, parent=None):

        super().__init__(parent)

        self._pixmap_item = QGraphicsPixmapItem()

        self.addItem(self._pixmap_item)

    # ---------------------------------------------------------

    def clear_image(self):

        self._pixmap_item.setPixmap(QPixmap())

        self.setSceneRect(QRectF())

    # ---------------------------------------------------------

    def set_image(self, filename: str) -> bool:

        pixmap = QPixmap(filename)

        if pixmap.isNull():

            self.clear_image()

            return False

        self._pixmap_item.setPixmap(pixmap)

        #
        # Aggiorna SEMPRE il rettangolo della scena.
        #

        self.setSceneRect(
            self._pixmap_item.boundingRect()
        )

        return True

    # ---------------------------------------------------------

    def has_image(self) -> bool:

        return not self._pixmap_item.pixmap().isNull()

    # ---------------------------------------------------------

    def pixmap_item(self) -> QGraphicsPixmapItem:

        return self._pixmap_item

    # ---------------------------------------------------------

    def image_rect(self):

        return self._pixmap_item.boundingRect()