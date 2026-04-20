"""
ui/url_bar.py
Komponen input URL — field teks, tombol Tambah, tombol Torrent.
"""

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLineEdit, QPushButton

from localization import tr
from ui.icons import get_icon, ICON_SIZE


def build_url_bar(window) -> QFrame:
    frame = QFrame()
    frame.setStyleSheet("QFrame{background:#1a1f2e;border-radius:8px;}")

    h = QHBoxLayout(frame)
    h.setContentsMargins(12, 8, 8, 8)

    window.url_input = QLineEdit()
    window.url_input.setPlaceholderText(tr("url_placeholder"))
    window.url_input.setStyleSheet("background:transparent;border:none;font-size:13px;")
    window.url_input.returnPressed.connect(window._add_download)

    window.btn_add_url = QPushButton(tr("btn_add"))
    window.btn_add_url.setObjectName("btn_add")
    window.btn_add_url.setIcon(get_icon("add"))
    window.btn_add_url.setIconSize(ICON_SIZE)
    window.btn_add_url.setFixedHeight(36)
    window.btn_add_url.clicked.connect(window._add_download)

    window.btn_add_torrent = QPushButton(tr("btn_torrent"))
    window.btn_add_torrent.setObjectName("btn_torrent")
    window.btn_add_torrent.setIcon(get_icon("torrent"))
    window.btn_add_torrent.setIconSize(ICON_SIZE)
    window.btn_add_torrent.setFixedHeight(36)
    window.btn_add_torrent.clicked.connect(window._add_torrent)

    h.addWidget(window.url_input)
    h.addWidget(window.btn_add_torrent)
    h.addWidget(window.btn_add_url)
    return frame