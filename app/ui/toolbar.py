"""
ui/toolbar.py
Komponen toolbar — tombol Pause/Resume (toggle), Hapus, Bersihkan,
dan label kecepatan download/upload global.
"""

from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QLabel

from ui.icons import get_icon, ICON_SIZE


def build_toolbar(window) -> QHBoxLayout:
    """
    Buat layout toolbar dan simpan widget penting ke `window`:
        window.btn_pause_resume — toggle button Pause/Resume
        window.btn_remove       — tombol hapus
        window.btn_clear        — tombol bersihkan selesai
        window.lbl_dl           — label kecepatan download
        window.lbl_ul           — label kecepatan upload

    State toggle disimpan di window._is_paused (bool).

    Parameter:
        window — instance MainWindow, dipakai untuk connect signal
    """
    h = QHBoxLayout()

    # ── Toggle Pause/Resume ──────────────────────────────────────────
    window._is_paused = False   # state awal: sedang download (belum di-pause)

    window.btn_pause_resume = QPushButton("  Pause")
    window.btn_pause_resume.setObjectName("btn_pause")
    window.btn_pause_resume.setIcon(get_icon("pause"))
    window.btn_pause_resume.setIconSize(ICON_SIZE)
    window.btn_pause_resume.clicked.connect(window._toggle_pause_resume)

    # ── Hapus ────────────────────────────────────────────────────────
    window.btn_remove = QPushButton("  Hapus")
    window.btn_remove.setObjectName("btn_remove")
    window.btn_remove.setIcon(get_icon("remove"))
    window.btn_remove.setIconSize(ICON_SIZE)
    window.btn_remove.clicked.connect(window._remove_selected)

    # ── Bersihkan ────────────────────────────────────────────────────
    window.btn_clear = QPushButton("  Bersihkan Selesai")
    window.btn_clear.setObjectName("btn_clear")
    window.btn_clear.setIcon(get_icon("clear"))
    window.btn_clear.setIconSize(ICON_SIZE)
    window.btn_clear.clicked.connect(window._clear_completed)

    for btn in [window.btn_pause_resume, window.btn_remove, window.btn_clear]:
        h.addWidget(btn)

    h.addStretch()

    window.lbl_dl = QLabel("⬇ —")
    window.lbl_ul = QLabel("⬆ —")
    for lbl in [window.lbl_dl, window.lbl_ul]:
        lbl.setStyleSheet("color:#64748b; font-size:12px;")
        h.addWidget(lbl)

    return h
