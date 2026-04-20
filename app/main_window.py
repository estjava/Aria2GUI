"""
main_window.py
Assembly utama — hanya menyatukan komponen UI dan menangani logika bisnis.
Untuk ubah tampilan, edit file di folder ui/.
Untuk ubah koneksi aria2, edit file di folder aria2/.
"""

import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QLabel, QStatusBar, QMessageBox, QFileDialog,
)
from PyQt6.QtCore import QTimer, QPoint

from aria2 import Aria2Client, Aria2Manager, RefreshWorker
from helpers import fmt_size, fmt_speed
from styles  import DARK_STYLE
from ui      import (
    get_icon,
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
        self.setWindowTitle("Aria2 GUI")
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)

        # State
        self.client       = Aria2Client()
        self.manager      = Aria2Manager()
        self.worker       = None
        self.download_dir = str(Path.home() / "Downloads")
        self._retry_count = 0
        self._downloads   = []   # cache download untuk context menu & detail

        self.setWindowIcon(get_icon("app"))
        self.setStyleSheet(DARK_STYLE)
        self._build_ui()
        self._auto_connect()

    # ── ASSEMBLY UI ───────────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 10)
        root.setSpacing(12)

        root.addLayout(build_header(self))
        root.addWidget(build_url_bar(self))
        root.addLayout(build_toolbar(self))
        root.addWidget(build_table(self), stretch=1)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._lbl_stat = QLabel("—")
        self._lbl_stat.setStyleSheet("color:#475569; font-size:11px;")
        self.status_bar.addPermanentWidget(self._lbl_stat)

    # ── AUTO CONNECT ──────────────────────────────────────────────────────────

    def _auto_connect(self):
        self.status_bar.showMessage("Mencoba koneksi ke aria2...")
        QTimer.singleShot(200, self._try_connect)

    def _try_connect(self):
        if self.client.is_connected():
            self._on_connected()
            return

        self.status_bar.showMessage("aria2 tidak berjalan, mencoba menjalankan otomatis...")
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
        self.lbl_dot.setStyleSheet("color:#4ade80; font-size:12px;")
        self.lbl_ver.setText(f"aria2 v{ver} — terhubung")
        self.status_bar.showMessage(f"✔ Terhubung ke aria2 v{ver}", 4000)

        self.worker = RefreshWorker(self.client)
        self.worker.data_ready.connect(self._on_data_ready)
        self.worker.start()

    def _on_connect_failed(self, msg):
        self.lbl_dot.setStyleSheet("color:#ef4444; font-size:12px;")
        self.lbl_ver.setText("Tidak terhubung")
        self.status_bar.showMessage("✖ Gagal terhubung")
        QMessageBox.critical(self, "Gagal Terhubung",
                             f"Tidak bisa terhubung ke aria2.\n\n{msg}")

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
            QMessageBox.warning(self, "Tidak terhubung", "aria2 belum terhubung.")
            return
        result = self.client.add_uri(url, {"dir": self.download_dir})
        if result:
            self.url_input.clear()
            self.status_bar.showMessage(f"✔ Download ditambahkan: {url[:60]}", 3000)
        else:
            QMessageBox.warning(self, "Gagal", "Gagal menambahkan URL.")

    def _add_torrent(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Pilih file .torrent", self.download_dir, "Torrent Files (*.torrent)"
        )
        if not path:
            return
        result = self.client.add_torrent(path, {"dir": self.download_dir})
        if result:
            self.status_bar.showMessage(f"✔ Torrent: {os.path.basename(path)}", 3000)
        else:
            QMessageBox.warning(self, "Gagal", "Gagal menambahkan torrent.")

    def _get_selected_gid(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 5)
        return item.text() if item else None

    def _pause_selected(self):
        gid = self._get_selected_gid()
        if gid:
            self.client.pause(gid)

    def _resume_selected(self):
        gid = self._get_selected_gid()
        if gid:
            self.client.unpause(gid)

    def _toggle_pause_resume(self):
        """Toggle pause/resume berdasarkan status download yang dipilih."""
        gid = self._get_selected_gid()
        if not gid:
            return

        # Cari status download dari cache
        d      = next((x for x in self._downloads if x.get("gid") == gid), {})
        status = d.get("status", "")

        if status == "active":
            self.client.pause(gid)
        elif status in ("paused", "waiting"):
            self.client.unpause(gid)

    def _sync_pause_resume_btn(self):
        """
        Perbarui icon & label tombol toggle sesuai status baris yang dipilih.
        - active  → tampilkan "Pause"
        - paused/waiting → tampilkan "Resume"
        - lainnya → disable tombol
        """
        from ui.icons import get_icon, ICON_SIZE
        gid    = self._get_selected_gid()
        btn    = self.btn_pause_resume
        d      = next((x for x in self._downloads if x.get("gid") == gid), {}) if gid else {}
        status = d.get("status", "")

        if status == "active":
            btn.setText("  Pause")
            btn.setIcon(get_icon("pause"))
            btn.setObjectName("btn_pause")
            btn.setEnabled(True)
        elif status in ("paused", "waiting"):
            btn.setText("  Resume")
            btn.setIcon(get_icon("resume"))
            btn.setObjectName("btn_resume")
            btn.setEnabled(True)
        else:
            btn.setText("  Pause")
            btn.setIcon(get_icon("pause"))
            btn.setObjectName("btn_pause")
            btn.setEnabled(False)

        # Re-apply stylesheet agar objectName baru terbaca
        btn.setStyle(btn.style())

    def _remove_selected(self):
        gid = self._get_selected_gid()
        if not gid:
            return
        reply = QMessageBox.question(
            self, "Hapus Download", "Yakin ingin menghapus download ini?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.client.remove(gid)

    def _clear_completed(self):
        self.client.purge_download_result()
        self.status_bar.showMessage("✔ Download selesai dibersihkan", 2000)

    def _change_dir(self):
        d = QFileDialog.getExistingDirectory(
            self, "Pilih Folder Download", self.download_dir
        )
        if d:
            self.download_dir = d
            self.status_bar.showMessage(f"Folder download: {d}", 3000)

    # ── CLOSE ─────────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
            self.worker.wait(2000)

        if self.manager.is_running():
            reply = QMessageBox.question(
                self, "Tutup Aplikasi",
                "Apakah ingin menghentikan aria2 juga?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.manager.stop()

        event.accept()
