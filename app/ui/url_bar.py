"""
ui/url_bar.py
Komponen input URL — field teks, tombol Tambah, tombol Torrent.
"""

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLineEdit, QPushButton

from ui.icons import get_icon, ICON_SIZE


def build_url_bar(window) -> QFrame:
    """
    Buat frame URL bar dan simpan widget penting ke `window`:
        window.url_input — QLineEdit untuk memasukkan URL

    Parameter:
        window — instance MainWindow, dipakai untuk connect signal
    """
    frame = QFrame()
    frame.setStyleSheet("QFrame{background:#1a1f2e;border-radius:8px;}")

    h = QHBoxLayout(frame)
    h.setContentsMargins(12, 8, 8, 8)

    window.url_input = QLineEdit()
    window.url_input.setPlaceholderText("Masukkan URL download (HTTP, FTP, Magnet)...")
    window.url_input.setStyleSheet("background:transparent;border:none;font-size:13px;")
    window.url_input.returnPressed.connect(window._add_download)

    btn_add = QPushButton("  Tambah")
    btn_add.setObjectName("btn_add")
    btn_add.setIcon(get_icon("add"))
    btn_add.setIconSize(ICON_SIZE)
    btn_add.setFixedHeight(36)
    btn_add.clicked.connect(window._add_download)

    btn_torrent = QPushButton("  Torrent")
    btn_torrent.setObjectName("btn_torrent")
    btn_torrent.setIcon(get_icon("torrent"))
    btn_torrent.setIconSize(ICON_SIZE)
    btn_torrent.setFixedHeight(36)
    btn_torrent.clicked.connect(window._add_torrent)

    h.addWidget(window.url_input)
    h.addWidget(btn_torrent)
    h.addWidget(btn_add)
    return frame
