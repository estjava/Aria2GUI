"""
ui/header.py
Komponen header — judul dan tombol folder download.
"""

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QFont

from localization import tr
from ui.icons import get_icon, ICON_SIZE


def build_header(window) -> QHBoxLayout:
    h = QHBoxLayout()

    title = QLabel(tr("header_title"))
    title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
    title.setStyleSheet("color:#e2e8f0; letter-spacing:-0.5px;")

    window.btn_folder_download = QPushButton(tr("btn_folder"))
    window.btn_folder_download.setObjectName("btn_clear")
    window.btn_folder_download.setIcon(get_icon("folder"))
    window.btn_folder_download.setIconSize(ICON_SIZE)
    window.btn_folder_download.clicked.connect(window._change_dir)

    h.addWidget(title)
    h.addStretch()
    h.addWidget(window.btn_folder_download)
    return h