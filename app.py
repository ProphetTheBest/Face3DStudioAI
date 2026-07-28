"""
==========================================================
Face3D Studio AI

File: app.py

Punto di ingresso dell'applicazione.

Autore:
Marco Cantù

Versione:
0.2.0
==========================================================
"""

import sys

from PySide6.QtWidgets import QApplication

from source.controllers.application_controller import ApplicationController
from source.gui.main_window import MainWindow


def main():
    """
    Punto di ingresso dell'applicazione.
    """

    app = QApplication(sys.argv)

    #
    # Crea il controller principale
    #
    app_controller = ApplicationController()
    
    # # -----------------------------
    # # TEST TEMPORANEO
    # # -----------------------------

    # app_controller.get_project_manager().new_project("Test Project")

    # app_controller.get_project_manager().save_project(
    #     r"C:\Users\Marco\Desktop\TestProject.face3d"
    # )
    #
    # Crea la finestra principale
    #
    window = MainWindow(app_controller)

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()