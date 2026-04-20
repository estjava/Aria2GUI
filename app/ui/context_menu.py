"""
ui/context_menu.py
Context menu klik kanan pada baris tabel download.
"""

import os
import sys
import subprocess

from PyQt6.QtWidgets import QMenu, QMessageBox
from PyQt6.QtCore import QPoint

from localization import tr
from ui.icons import get_icon

MENU_STYLE = """
    QMenu {
        background-color: #1a1f2e;
        border: 1px solid #2d3748;
        border-radius: 8px;
        padding: 4px;
        color: #e2e8f0;
        font-size: 13px;
    }
    QMenu::item { padding: 8px 20px 8px 12px; border-radius: 4px; }
    QMenu::item:selected { background-color: #2d3748; }
    QMenu::separator { height: 1px; background: #2d3748; margin: 4px 8px; }
    QMenu::item:disabled { color: #475569; }
"""


def show_context_menu(window, pos: QPoint):
    row = window.table.rowAt(pos.y())
    if row < 0:
        return

    window.table.selectRow(row)
    d      = window._downloads[row] if row < len(window._downloads) else {}
    status = d.get("status", "")

    menu = QMenu(window)
    menu.setStyleSheet(MENU_STYLE)

    if status == "active":
        act = menu.addAction(get_icon("pause"), tr("ctx_pause"))
        act.triggered.connect(window._toggle_pause_resume)
    elif status in ("paused", "waiting"):
        act = menu.addAction(get_icon("resume"), tr("ctx_resume"))
        act.triggered.connect(window._toggle_pause_resume)
    else:
        act = menu.addAction(tr("ctx_pause_resume"))
        act.setEnabled(False)

    menu.addSeparator()

    act_folder = menu.addAction(get_icon("open"), tr("ctx_open_folder"))
    act_folder.triggered.connect(lambda: open_folder(window, d))

    menu.addSeparator()

    act_detail = menu.addAction(get_icon("detail"), tr("ctx_detail"))
    act_detail.triggered.connect(lambda: _trigger_detail(window, d))

    menu.addSeparator()

    act_remove = menu.addAction(get_icon("remove"), tr("ctx_remove"))
    act_remove.triggered.connect(window._remove_selected)

    menu.exec(window.table.viewport().mapToGlobal(pos))


def open_folder(window, d: dict):
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
        QMessageBox.warning(window, tr("dlg_failed_title"),
                            tr("dlg_open_folder_fail", err=str(e)))


def _trigger_detail(window, d: dict):
    from ui.detail_dialog import show_detail
    show_detail(window, d)