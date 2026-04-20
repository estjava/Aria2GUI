"""
ui/icons.py
Pemetaan nama logis ke icon qtawesome + helper get_icon().

Untuk mengganti icon, edit dict ICONS di bawah.
Daftar icon tersedia di: https://fontawesome.com/icons
Prefix yang umum dipakai: fa5s (solid), fa5r (regular), fa5b (brands), mdi (Material Design)
"""

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
import qtawesome as qta


ICONS = {
    "app":     ("fa5s.download",         "#3b82f6"),
    "add":     ("fa5s.plus-circle",      "#ffffff"),
    "torrent": ("fa5s.magnet",           "#a78bfa"),
    "folder":  ("fa5s.folder-open",      "#94a3b8"),
    "pause":   ("fa5s.pause-circle",     "#facc15"),
    "resume":  ("fa5s.play-circle",      "#4ade80"),
    "remove":  ("fa5s.trash-alt",        "#f87171"),
    "clear":   ("fa5s.broom",            "#94a3b8"),
    "detail":  ("fa5s.info-circle",      "#60a5fa"),
    "open":    ("fa5s.external-link-alt","#94a3b8"),
}

ICON_SIZE = QSize(18, 18)


def get_icon(name: str, color: str = None) -> QIcon:
    """
    Ambil QIcon dari qtawesome berdasarkan nama logis (key di ICONS).
    Jika nama tidak ditemukan, kembalikan QIcon kosong.

    Contoh:
        get_icon("add")
        get_icon("pause", color="#ff0000")
    """
    if name not in ICONS:
        return QIcon()
    fa_name, default_color = ICONS[name]
    return qta.icon(fa_name, color=color or default_color)
