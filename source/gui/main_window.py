from PySide6.QtWidgets import (
    QMainWindow,
    QLabel
)

from PySide6.QtCore import Qt


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Face3D Studio AI")

        self.resize(1400, 900)

        label = QLabel("Benvenuto in Face3D Studio AI")

        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setCentralWidget(label)