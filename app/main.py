"""
main.py
Entry point — jalankan file ini untuk membuka aplikasi.

    python main.py
"""

import sys
from PyQt6.QtWidgets import QApplication
from main_window_v3 import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Aria2 GUI")
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
