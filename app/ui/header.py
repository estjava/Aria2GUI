"""
ui/header.py
Komponen header — judul, status koneksi, tombol folder download.
"""

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QFont

from ui.icons import get_icon, ICON_SIZE


def build_header(window) -> QHBoxLayout:
    """
    Buat layout header dan simpan widget penting ke `window`:
        window.lbl_dot  — indikator status koneksi (●)
        window.lbl_ver  — teks versi aria2

    Parameter:
        window — instance MainWindow, dipakai untuk connect signal
    """
    h = QHBoxLayout()

    title = QLabel("⬇  Aria2 GUI")
    title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
    title.setStyleSheet("color:#e2e8f0; letter-spacing:-0.5px;")

    window.lbl_dot = QLabel("●")
    window.lbl_dot.setStyleSheet("color:#ef4444; font-size:12px;")
    window.lbl_dot.setToolTip("Status koneksi aria2")

    window.lbl_ver = QLabel("Tidak terhubung")
    window.lbl_ver.setStyleSheet("color:#475569; font-size:11px;")

    btn_dir = QPushButton("  Folder Download")
    btn_dir.setObjectName("btn_clear")
    btn_dir.setIcon(get_icon("folder"))
    btn_dir.setIconSize(ICON_SIZE)
    btn_dir.clicked.connect(window._change_dir)

    h.addWidget(title)
    h.addSpacing(10)
    h.addWidget(window.lbl_dot)
    h.addWidget(window.lbl_ver)
    h.addStretch()
    h.addWidget(btn_dir)
    return h
