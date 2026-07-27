import sys

print("1 - Avvio")

from PySide6.QtWidgets import QApplication

print("2 - PySide6 OK")

from source.gui.main_window import MainWindow

print("3 - MainWindow importata")

def main():
    print("4 - Creo QApplication")
    app = QApplication(sys.argv)

    print("5 - Creo MainWindow")
    window = MainWindow()

    print("6 - Mostro finestra")
    window.show()

    print("7 - Entro nel loop")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()