"""
==========================================================
Face3D Studio AI

Image Viewer

Autore:
Marco Cantù

Versione:
0.4.0
==========================================================
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QGraphicsView

from source.widgets.image_scene import ImageScene

from source.ai.models.face_detection import FaceDetection
from source.ai.models.face_landmark import FaceLandmark

from source.models.face_mesh import FaceMesh


class ImageViewer(QGraphicsView):

    MIN_ZOOM = 0.10
    MAX_ZOOM = 20.0
    ZOOM_FACTOR = 1.15

    def __init__(self):

        super().__init__()

        self._scene = ImageScene(self)

        self.setScene(self._scene)

        self._current_image = None

        self._current_zoom = 1.0

        self._fit_mode = True

        self._panning = False

        self._last_mouse_pos = None

        self.setAlignment(Qt.AlignCenter)

        self.setRenderHint(QPainter.SmoothPixmapTransform)

        self.setTransformationAnchor(
            QGraphicsView.AnchorUnderMouse
        )

        self.setResizeAnchor(
            QGraphicsView.AnchorViewCenter
        )

        self.setDragMode(
            QGraphicsView.NoDrag
        )

    # ---------------------------------------------------------

    def clear(self):

        self._scene.clear_image()

        self._current_image = None

        self.resetTransform()

        self.centerOn(0, 0)

        self.horizontalScrollBar().setValue(0)

        self.verticalScrollBar().setValue(0)

        self._current_zoom = 1.0

        self._fit_mode = True

        self.viewport().update()

    # ---------------------------------------------------------

    def show_image(
        self,
        filename: str,
    ):

        self.clear()

        if not self._scene.set_image(filename):

            return

        self._current_image = filename

        self.fit_image()

    # ---------------------------------------------------------

    def fit_image(self):

        if not self._scene.has_image():

            return

        self.resetTransform()

        self.fitInView(

            self._scene.pixmap_item(),

            Qt.KeepAspectRatio,

        )

        self.centerOn(

            self._scene.pixmap_item()

        )

        self._current_zoom = 1.0

        self._fit_mode = True

    # ---------------------------------------------------------

    def current_image(self):

        return self._current_image

    # ---------------------------------------------------------

    def show_faces(
        self,
        faces: list[FaceDetection],
    ):

        self._scene.show_faces(faces)

    # ---------------------------------------------------------

    def show_landmarks(
        self,
        landmarks: list[FaceLandmark],
    ):

        self._scene.show_landmarks(
            landmarks
        )

    # ---------------------------------------------------------

    def show_face_mesh(
        self,
        mesh: FaceMesh,
    ):

        self._scene.show_face_mesh(
            mesh
        )

    # ---------------------------------------------------------

    def clear_landmarks(self):

        self._scene.clear_landmarks()

    # ---------------------------------------------------------

    def clear_faces(self):

        self._scene.clear_faces()

    # ---------------------------------------------------------

    def clear_face_mesh(self):

        self._scene.clear_face_mesh()

    # ---------------------------------------------------------

    def _is_pan_button(
        self,
        event,
    ):

        return event.button() == Qt.MiddleButton

    # ---------------------------------------------------------

    def wheelEvent(self, event):

        if not self._scene.has_image():

            return

        if event.angleDelta().y() > 0:

            factor = self.ZOOM_FACTOR

        else:

            factor = 1 / self.ZOOM_FACTOR

        new_zoom = self._current_zoom * factor

        if new_zoom < self.MIN_ZOOM:

            return

        if new_zoom > self.MAX_ZOOM:

            return

        self._fit_mode = False

        self.scale(
            factor,
            factor,
        )

        self._current_zoom = new_zoom

    # ---------------------------------------------------------

    def mousePressEvent(self, event):

        if self._is_pan_button(event):

            self._panning = True

            self._last_mouse_pos = event.pos()

            self.setCursor(Qt.ClosedHandCursor)

            event.accept()

            return

        super().mousePressEvent(event)

    # ---------------------------------------------------------

    def mouseMoveEvent(self, event):

        if self._panning:

            delta = event.pos() - self._last_mouse_pos

            self._last_mouse_pos = event.pos()

            self.horizontalScrollBar().setValue(

                self.horizontalScrollBar().value() - delta.x()

            )

            self.verticalScrollBar().setValue(

                self.verticalScrollBar().value() - delta.y()

            )

            event.accept()

            return

        super().mouseMoveEvent(event)

    # ---------------------------------------------------------

    def mouseReleaseEvent(self, event):

        if self._is_pan_button(event):

            self._panning = False

            self.setCursor(Qt.ArrowCursor)

            event.accept()

            return

        super().mouseReleaseEvent(event)

    # ---------------------------------------------------------

    def mouseDoubleClickEvent(self, event):

        self.fit_image()

        super().mouseDoubleClickEvent(event)

    # ---------------------------------------------------------

    def resizeEvent(self, event):

        super().resizeEvent(event)

        if self._fit_mode:

            self.fit_image()