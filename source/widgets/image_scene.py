"""
==========================================================
Face3D Studio AI

Image Scene

Autore:
Marco Cantù

Versione:
0.3.0
==========================================================
"""

from PySide6.QtCore import QRectF, Signal
from PySide6.QtGui import QColor, QPen, QPixmap, QBrush
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
)

from source.ai.models.face_detection import FaceDetection
from source.ai.models.face_landmark import FaceLandmark
from source.models.face_mesh import FaceMesh
from source.models.face import Face


class ImageScene(QGraphicsScene):
    """
    Scena grafica contenente tutti gli elementi
    visualizzati nel Viewer.
    """

    face_selected = Signal(object)

    def __init__(self, parent=None):

        super().__init__(parent)

        self._pixmap_item = QGraphicsPixmapItem()

        self.addItem(self._pixmap_item)

        self._face_items: list[QGraphicsRectItem] = []

        self._face_map = {}

        self._landmark_items: list[QGraphicsEllipseItem] = []

        self._mesh_items: list[QGraphicsLineItem] = []

    # ---------------------------------------------------------

    def clear_image(self):

        self._pixmap_item.setPixmap(QPixmap())

        self.clear_faces()

        self.clear_landmarks()

        self.clear_face_mesh()

        self.setSceneRect(QRectF())

    # ---------------------------------------------------------

    def set_image(self, filename: str) -> bool:

        pixmap = QPixmap(filename)

        if pixmap.isNull():

            self.clear_image()

            return False

        self._pixmap_item.setPixmap(pixmap)

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

    def clear_faces(self):

        for item in self._face_items:

            self.removeItem(item)

        self._face_items.clear()

        self._face_map.clear()

    # ---------------------------------------------------------

    def clear_landmarks(self):

        for item in self._landmark_items:

            self.removeItem(item)

        self._landmark_items.clear()

    # ---------------------------------------------------------

    def clear_face_mesh(self):

        for item in self._mesh_items:

            self.removeItem(item)

        self._mesh_items.clear()

    # ---------------------------------------------------------

    def show_landmarks(
        self,
        landmarks: list[FaceLandmark],
    ):

        self.clear_landmarks()

        pen = QPen(QColor(255, 255, 0))
        pen.setWidth(1)

        brush = QBrush(QColor(255, 255, 0))

        radius = 3

        width = self._pixmap_item.pixmap().width()
        height = self._pixmap_item.pixmap().height()

        for point in landmarks:

            x = point.x * width
            y = point.y * height

            item = self.addEllipse(
                x - radius,
                y - radius,
                radius * 2,
                radius * 2,
                pen,
                brush,
            )

            item.setZValue(100)

            self._landmark_items.append(item)


    # ---------------------------------------------------------

    # ---------------------------------------------------------

    def show_face_mesh(
        self,
        landmarks: list[FaceLandmark],
        edges: list[tuple[int, int]],
    ):

        self.clear_face_mesh()

        if not landmarks:
            return

        width = self._pixmap_item.pixmap().width()
        height = self._pixmap_item.pixmap().height()

        pen = QPen(QColor(0, 180, 255))
        pen.setWidth(1)

        for start, end in edges:

            p1 = landmarks[start]
            p2 = landmarks[end]

            line = self.addLine(
                p1.x * width,
                p1.y * height,
                p2.x * width,
                p2.y * height,
                pen,
            )

            line.setZValue(75)

            self._mesh_items.append(line)

            line.setZValue(75)

            self._mesh_items.append(line)

    # ---------------------------------------------------------

    def show_faces(
        self,
        faces: list[Face],
    ):

        self.clear_faces()

        pen = QPen(QColor(0, 255, 0))
        pen.setWidth(3)

        for face in faces:

            detection = face.detection

            rect = self.addRect(
                detection.x,
                detection.y,
                detection.width,
                detection.height,
                pen,
            )

            rect.setZValue(50)

            self._face_items.append(rect)

            self._face_map[rect] = face

    # ---------------------------------------------------------

    def mousePressEvent(self, event):

        item = self.itemAt(
            event.scenePos(),
            self.views()[0].transform(),
        )

        if item in self._face_map:

            self.face_selected.emit(
                self._face_map[item]
            )

            event.accept()

            return

        super().mousePressEvent(event)
    # ---------------------------------------------------------

    def image_rect(self):

        return self._pixmap_item.boundingRect()