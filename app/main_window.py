"""
main_window.py
Assembly utama — hanya menyatukan komponen UI dan menangani logika bisnis.
Untuk ubah tampilan, edit file di folder ui/.
Untuk ubah koneksi aria2, edit file di folder aria2/.
Untuk ubah teks/bahasa, edit file di folder localization/.
"""

import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QLabel, QStatusBar, QMessageBox, QFileDialog,
)
from PyQt6.QtCore import QTimer, QPoint

from aria2          import Aria2Client, Aria2Manager, RefreshWorker
from helpers        import fmt_size, fmt_speed
from ui.css         import DARK_STYLE
from localization   import tr, Translator
from ui             import (
    get_icon,
    build_menu_bar,
    build_header,
    build_url_bar,
    build_toolbar,
    build_table,
    update_table,
    show_context_menu,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("app_title"))
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)

        self.client       = Aria2Client()
        self.manager      = Aria2Manager()
        self.worker       = None
        self.download_dir = str(Path.home() / "Downloads")
        self._retry_count = 0
        self._downloads   = []

        self.setWindowIcon(get_icon("app"))
        self.setStyleSheet(DARK_STYLE)
        self._build_ui()
        self._auto_connect()

    # ── ASSEMBLY UI ───────────────────────────────────────────────────────────

    def _build_ui(self):
        build_menu_bar(self)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 10)
        root.setSpacing(12)

        root.addLayout(build_header(self))
        root.addWidget(build_url_bar(self))
        root.addLayout(build_toolbar(self))
        root.addWidget(build_table(self), stretch=1)

        self._build_status_bar()

    def _build_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # KIRI (permanent) — indikator koneksi aria2
        self.lbl_dot = QLabel("●")
        self.lbl_dot.setToolTip("Status koneksi aria2")

        self.lbl_ver = QLabel(tr("sb_disconnected"))

        self.status_bar.insertPermanentWidget(0, self.lbl_dot)
        self.status_bar.insertPermanentWidget(1, self.lbl_ver)

        # KANAN (permanent) — kecepatan & statistik download
        self.lbl_dl = QLabel("⬇ —")

        self.lbl_ul = QLabel("⬆ —")

        self._lbl_stat = QLabel(
            f"{tr('sb_active')}: 0  |  {tr('sb_waiting')}: 0  |  {tr('sb_total')}: 0"
        )

        self.status_bar.addPermanentWidget(self.lbl_dl)
        self.status_bar.addPermanentWidget(self.lbl_ul)
        self.status_bar.addPermanentWidget(self._lbl_stat)

    def _set_status(self, msg: str, timeout: int = 3000):
        """Tampilkan pesan sementara di tengah status bar."""
        self.status_bar.showMessage(msg, timeout)

    # ── AUTO CONNECT ──────────────────────────────────────────────────────────

    def _auto_connect(self):
        self.lbl_ver.setText(tr("sb_connecting"))
        self._set_status(tr("sb_trying"))
        QTimer.singleShot(200, self._try_connect)

    def _try_connect(self):
        if self.client.is_connected():
            self._on_connected()
            return

        self.lbl_ver.setText(tr("sb_starting"))
        self._set_status(tr("sb_starting_auto"))
        ok, msg = self.manager.start(port=6800, download_dir=self.download_dir)
        if not ok:
            self._on_connect_failed(msg)
            return

        self._retry_count = 0
        QTimer.singleShot(500, self._wait_ready)

    def _wait_ready(self):
        if self.client.is_connected():
            self._on_connected()
            return
        self._retry_count += 1
        if self._retry_count >= 10:
            self._on_connect_failed("aria2 tidak merespons setelah dijalankan.")
        else:
            QTimer.singleShot(500, self._wait_ready)

    def _on_connected(self):
        ver = self.client.get_version()
        self.lbl_ver.setText(tr("sb_connected_label", ver=ver))
        self._set_status(tr("sb_connected", ver=ver), 4000)

        self.worker = RefreshWorker(self.client)
        self.worker.data_ready.connect(self._on_data_ready)
        self.worker.start()

    def _on_connect_failed(self, msg):
        self.lbl_ver.setText(tr("sb_disconnected"))
        self._set_status(tr("sb_failed", msg=msg), 8000)
        QMessageBox.critical(self, tr("dlg_connect_fail_title"),
                             tr("dlg_connect_fail_msg", msg=msg))

    # ── DATA REFRESH ──────────────────────────────────────────────────────────

    def _on_data_ready(self, downloads: list, stat: dict):
        update_table(self, downloads, stat)

    # ── CONTEXT MENU ──────────────────────────────────────────────────────────

    def _show_context_menu(self, pos: QPoint):
        show_context_menu(self, pos)

    # ── DOWNLOAD ACTIONS ──────────────────────────────────────────────────────

    def _add_download(self):
        url = self.url_input.text().strip()
        if not url:
            return
        if not self.client.is_connected():
            QMessageBox.warning(self, tr("dlg_not_connected_title"),
                                tr("dlg_not_connected_msg"))
            return
        result = self.client.add_uri(url, {"dir": self.download_dir})
        if result:
            self.url_input.clear()
            self._set_status(tr("sb_added", url=url[:60]))
        else:
            QMessageBox.warning(self, tr("dlg_failed_title"), tr("dlg_failed_add"))

    def _add_torrent(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr("dlg_torrent_title"), self.download_dir, tr("dlg_torrent_filter")
        )
        if not path:
            return
        result = self.client.add_torrent(path, {"dir": self.download_dir})
        if result:
            self._set_status(tr("sb_torrent_added", name=os.path.basename(path)))
        else:
            QMessageBox.warning(self, tr("dlg_failed_title"), tr("dlg_failed_torrent"))

    def _get_selected_gid(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 5)
        return item.text() if item else None

    def _toggle_pause_resume(self):
        gid = self._get_selected_gid()
        if not gid:
            return
        d      = next((x for x in self._downloads if x.get("gid") == gid), {})
        status = d.get("status", "")
        if status == "active":
            self.client.pause(gid)
            self._set_status(tr("sb_paused"))
        elif status in ("paused", "waiting"):
            self.client.unpause(gid)
            self._set_status(tr("sb_resumed"))

    def _sync_pause_resume_btn(self):
        """Perbarui icon & label tombol toggle sesuai status baris yang dipilih."""
        from ui.icons import get_icon, ICON_SIZE
        gid    = self._get_selected_gid()
        btn    = self.btn_pause_resume
        d      = next((x for x in self._downloads if x.get("gid") == gid), {}) if gid else {}
        status = d.get("status", "")

        if status == "active":
            btn.setText(tr("btn_pause"))
            btn.setIcon(get_icon("pause"))
            btn.setObjectName("btn_pause")
            btn.setEnabled(True)
        elif status in ("paused", "waiting"):
            btn.setText(tr("btn_resume"))
            btn.setIcon(get_icon("resume"))
            btn.setObjectName("btn_resume")
            btn.setEnabled(True)
        else:
            btn.setText(tr("btn_pause"))
            btn.setIcon(get_icon("pause"))
            btn.setObjectName("btn_pause")
            btn.setEnabled(False)

        btn.setStyle(btn.style())

    def _remove_selected(self):
        gid = self._get_selected_gid()
        if not gid:
            return
        reply = QMessageBox.question(
            self, tr("dlg_remove_title"), tr("dlg_remove_msg"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.client.remove(gid)
            self._set_status(tr("sb_removed"))

    def _clear_completed(self):
        self.client.purge_download_result()
        self._set_status(tr("sb_cleared"))

    def _change_dir(self):
        d = QFileDialog.getExistingDirectory(
            self, tr("dlg_folder_title"), self.download_dir
        )
        if d:
            self.download_dir = d
            self._set_status(tr("sb_folder_changed", path=d))

    # ── CLOSE ─────────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
            self.worker.wait(2000)

        if self.manager.is_running():
            reply = QMessageBox.question(
                self, tr("dlg_close_title"), tr("dlg_close_msg"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.manager.stop()

        event.accept()