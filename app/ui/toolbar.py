"""
ui/toolbar.py
Komponen toolbar — tombol Pause/Resume (toggle), Hapus, Bersihkan.
Label kecepatan download/upload dipindah ke status bar.
"""

from PyQt6.QtWidgets import QHBoxLayout, QPushButton

from ui.icons import get_icon, ICON_SIZE


def build_toolbar(window) -> QHBoxLayout:
    """
    Buat layout toolbar dan simpan widget penting ke `window`:
        window.btn_pause_resume — toggle button Pause/Resume
        window.btn_remove       — tombol hapus
        window.btn_clear        — tombol bersihkan selesai

    Parameter:
        window — instance MainWindow, dipakai untuk connect signal
    """
    h = QHBoxLayout()

    window._is_paused = False

    window.btn_pause_resume = QPushButton("  Pause")
    window.btn_pause_resume.setObjectName("btn_pause")
    window.btn_pause_resume.setIcon(get_icon("pause"))
    window.btn_pause_resume.setIconSize(ICON_SIZE)
    window.btn_pause_resume.clicked.connect(window._toggle_pause_resume)

    window.btn_remove = QPushButton("  Hapus")
    window.btn_remove.setObjectName("btn_remove")
    window.btn_remove.setIcon(get_icon("remove"))
    window.btn_remove.setIconSize(ICON_SIZE)
    window.btn_remove.clicked.connect(window._remove_selected)

    window.btn_clear = QPushButton("  Bersihkan Selesai")
    window.btn_clear.setObjectName("btn_clear")
    window.btn_clear.setIcon(get_icon("clear"))
    window.btn_clear.setIconSize(ICON_SIZE)
    window.btn_clear.clicked.connect(window._clear_completed)

    for btn in [window.btn_pause_resume, window.btn_remove, window.btn_clear]:
        h.addWidget(btn)

    h.addStretch()
    return h