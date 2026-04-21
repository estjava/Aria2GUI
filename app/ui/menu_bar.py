"""
ui/menu_bar.py
Komponen menu bar — File, Settings, Help.
"""

import os
import sys
import subprocess

from PyQt6.QtWidgets import QMenuBar, QMenu, QMessageBox, QFileDialog
from PyQt6.QtGui import QAction

from localization import tr, Translator
from ui.icons import get_icon


def build_menu_bar(window) -> QMenuBar:
    """
    Buat menu bar dan pasang ke window.
    Menyimpan referensi action ke window agar bisa di-retranslate:
        window._menu_actions — dict {key: QAction}
        window._menus        — dict {key: QMenu}

    Parameter:
        window — instance MainWindow
    """
    window._menu_actions = {}
    window._menus        = {}

    bar = window.menuBar()

    # ── FILE ──────────────────────────────────────────────────────────────────
    menu_file = bar.addMenu(tr("menu_file"))
    window._menus["file"] = menu_file

    act_add_torrent = QAction(get_icon("torrent"), tr("menu_file_add_torrent"), window)
    act_add_torrent.setShortcut("Ctrl+T")
    act_add_torrent.triggered.connect(window._add_torrent)
    menu_file.addAction(act_add_torrent)
    window._menu_actions["file_add_torrent"] = act_add_torrent

    menu_file.addSeparator()

    act_exit = QAction(tr("menu_file_exit"), window)
    act_exit.setShortcut("Ctrl+Q")
    act_exit.triggered.connect(window.close)
    menu_file.addAction(act_exit)
    window._menu_actions["file_exit"] = act_exit

    # ── SETTINGS ─────────────────────────────────────────────────────────────
    menu_settings = bar.addMenu(tr("menu_settings"))
    window._menus["settings"] = menu_settings

    act_dl_folder = QAction(get_icon("folder"), tr("menu_settings_dl_folder"), window)
    act_dl_folder.setShortcut("Ctrl+Shift+F")
    act_dl_folder.triggered.connect(window._change_dir)
    menu_settings.addAction(act_dl_folder)
    window._menu_actions["settings_dl_folder"] = act_dl_folder

    menu_settings.addSeparator()

    menu_lang = QMenu(tr("menu_settings_language"), window)
    menu_lang.setIcon(get_icon("language") if "language" in __import__("ui.icons", fromlist=["ICONS"]).ICONS else menu_lang.icon())
    window._menus["language"] = menu_lang

    act_lang_id = QAction(tr("menu_settings_lang_id"), window)
    act_lang_id.setCheckable(True)
    act_lang_id.setChecked(Translator.language == "id")
    act_lang_id.triggered.connect(lambda: _switch_language(window, "id"))
    menu_lang.addAction(act_lang_id)
    window._menu_actions["lang_id"] = act_lang_id

    act_lang_en = QAction(tr("menu_settings_lang_en"), window)
    act_lang_en.setCheckable(True)
    act_lang_en.setChecked(Translator.language == "en")
    act_lang_en.triggered.connect(lambda: _switch_language(window, "en"))
    menu_lang.addAction(act_lang_en)
    window._menu_actions["lang_en"] = act_lang_en

    menu_settings.addMenu(menu_lang)

    # ── HELP ─────────────────────────────────────────────────────────────────
    menu_help = bar.addMenu(tr("menu_help"))
    window._menus["help"] = menu_help

    act_about = QAction(get_icon("detail"), tr("menu_help_about"), window)
    act_about.triggered.connect(lambda: _show_about(window))
    menu_help.addAction(act_about)
    window._menu_actions["help_about"] = act_about

    # Daftarkan retranslate saat bahasa diganti
    Translator.on_change(lambda: _retranslate(window))

    return bar


def _switch_language(window, lang: str):
    """Ganti bahasa dan update checkmark."""
    from localization import set_language
    set_language(lang)
    window._menu_actions["lang_id"].setChecked(lang == "id")
    window._menu_actions["lang_en"].setChecked(lang == "en")


def _retranslate(window):
    """Update semua teks UI setelah bahasa diganti."""
    # Menu titles
    window._menus["file"].setTitle(tr("menu_file"))
    window._menus["settings"].setTitle(tr("menu_settings"))
    window._menus["language"].setTitle(tr("menu_settings_language"))
    window._menus["help"].setTitle(tr("menu_help"))

    # Menu actions
    window._menu_actions["file_add_torrent"].setText(tr("menu_file_add_torrent"))
    window._menu_actions["file_exit"].setText(tr("menu_file_exit"))
    window._menu_actions["settings_dl_folder"].setText(tr("menu_settings_dl_folder"))
    window._menu_actions["lang_id"].setText(tr("menu_settings_lang_id"))
    window._menu_actions["lang_en"].setText(tr("menu_settings_lang_en"))
    window._menu_actions["help_about"].setText(tr("menu_help_about"))

    # Header
    window.btn_folder_download.setText(tr("btn_folder"))

    # URL bar
    window.url_input.setPlaceholderText(tr("url_placeholder"))
    window.btn_add_url.setText(tr("btn_add"))
    window.btn_add_torrent.setText(tr("btn_torrent"))

    # Toolbar
    window.btn_pause_resume.setText(
        tr("btn_resume") if window.btn_pause_resume.objectName() == "btn_resume"
        else tr("btn_pause")
    )
    window.btn_remove.setText(tr("btn_remove"))
    window.btn_clear.setText(tr("btn_clear"))

    # Table headers
    window.table.setHorizontalHeaderLabels([
        tr("col_name"), tr("col_size"), tr("col_progress"),
        tr("col_speed"), tr("col_status"), tr("col_gid"),
    ])

    # Status bar — label koneksi
    if "terhubung" in window.lbl_ver.text() or "connected" in window.lbl_ver.text():
        pass  # akan diupdate oleh refresh worker
    else:
        window.lbl_ver.setText(tr("sb_disconnected"))


def _show_about(window):
    """Tampilkan dialog About."""
    msg = QMessageBox(window)
    msg.setWindowTitle(tr("about_title"))
    msg.setIconPixmap(get_icon("app").pixmap(48, 48))
    msg.setText(
        f"<b>{tr('about_title')}</b><br><br>"
        f"{tr('about_desc').replace(chr(10), '<br>')}<br><br>"
        f"{tr('about_version')}<br>"
        f"{tr('about_license')}"
    )
    msg.exec()
