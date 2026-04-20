"""
ui/context_menu.py
Context menu klik kanan pada baris tabel download.
"""

import os
import sys
import subprocess

from PyQt6.QtWidgets import QMenu, QMessageBox
from PyQt6.QtCore import QPoint

from ui.icons import get_icon
from helpers import STATUS_LABELS


MENU_STYLE = """
    QMenu {
        background-color: #1a1f2e;
        border: 1px solid #2d3748;
        border-radius: 8px;
        padding: 4px;
        color: #e2e8f0;
        font-size: 13px;
    }
    QMenu::item {
        padding: 8px 20px 8px 12px;
        border-radius: 4px;
    }
    QMenu::item:selected {
        background-color: #2d3748;
    }
    QMenu::separator {
        height: 1px;
        background: #2d3748;
        margin: 4px 8px;
    }
    QMenu::item:disabled {
        color: #475569;
    }
"""


def show_context_menu(window, pos: QPoint):
    """
    Tampilkan context menu pada posisi klik kanan di tabel.

    Item menu:
        - Pause / Resume  (adaptif sesuai status)
        - Buka Folder File
        - Lihat Detail
        - Hapus

    Parameter:
        window — instance MainWindow
        pos    — posisi klik dalam koordinat viewport tabel
    """
    row = window.table.rowAt(pos.y())
    if row < 0:
        return

    window.table.selectRow(row)

    d      = window._downloads[row] if row < len(window._downloads) else {}
    status = d.get("status", "")

    menu = QMenu(window)
    menu.setStyleSheet(MENU_STYLE)

    # ── Pause / Resume ──────────────────────────────
    if status == "active":
        act = menu.addAction(get_icon("pause"), "  Pause")
        act.triggered.connect(window._pause_selected)
    elif status in ("paused", "waiting"):
        act = menu.addAction(get_icon("resume"), "  Resume")
        act.triggered.connect(window._resume_selected)
    else:
        act = menu.addAction("  Pause / Resume")
        act.setEnabled(False)

    menu.addSeparator()

    # ── Buka Folder ─────────────────────────────────
    act_folder = menu.addAction(get_icon("open"), "  Buka Folder File")
    act_folder.triggered.connect(lambda: open_folder(window, d))

    menu.addSeparator()

    # ── Detail ──────────────────────────────────────
    act_detail = menu.addAction(get_icon("detail"), "  Lihat Detail")
    act_detail.triggered.connect(lambda: _trigger_detail(window, d))

    menu.addSeparator()

    # ── Hapus ────────────────────────────────────────
    act_remove = menu.addAction(get_icon("remove"), "  Hapus")
    act_remove.triggered.connect(window._remove_selected)

    menu.exec(window.table.viewport().mapToGlobal(pos))


def open_folder(window, d: dict):
    """Buka folder tempat file disimpan di file manager OS."""
    try:
        files  = d.get("files", [])
        path   = files[0].get("path", "") if files else ""
        folder = os.path.dirname(path) if path else window.download_dir

        if not os.path.isdir(folder):
            folder = window.download_dir

        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    except Exception as e:
        QMessageBox.warning(window, "Gagal", f"Tidak bisa membuka folder:\n{e}")


def _trigger_detail(window, d: dict):
    """Delegate ke detail_dialog melalui window agar tidak circular import."""
    from ui.detail_dialog import show_detail
    show_detail(window, d)
