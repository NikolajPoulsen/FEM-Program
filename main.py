import sys
from PySide6.QtWidgets import QApplication
from ui.ui_main import MainWindow


if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
