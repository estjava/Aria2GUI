"""
main_window.py
Modul utama tampilan GUI — QMainWindow dengan semua widget dan logika UI.
"""

import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QTableWidget, QTableWidgetItem,
    QProgressBar, QHeaderView, QMessageBox, QFileDialog, QFrame,
    QStatusBar, QMenu, QDialog, QGridLayout, QDialogButtonBox,
)
from PyQt6.QtCore import Qt, QTimer, QSize, QPoint
from PyQt6.QtGui import QColor, QFont, QIcon
import qtawesome as qta

# ── Pemetaan nama logis → nama icon Font Awesome ─────────────────────────────
#    Ganti value-nya jika ingin pakai icon lain dari qtawesome.
#    Daftar icon: https://fontawesome.com/icons  (prefix fa5s, fa5r, fa5b, mdi, dll)
ICONS = {
    "app":     ("fa5s.download",        "#3b82f6"),
    "add":     ("fa5s.plus-circle",     "#ffffff"),
    "torrent": ("fa5s.magnet",          "#a78bfa"),
    "folder":  ("fa5s.folder-open",     "#94a3b8"),
    "pause":   ("fa5s.pause-circle",    "#facc15"),
    "resume":  ("fa5s.play-circle",     "#4ade80"),
    "remove":  ("fa5s.trash-alt",       "#f87171"),
    "clear":   ("fa5s.broom",           "#94a3b8"),
    "detail":  ("fa5s.info-circle",     "#60a5fa"),
    "open":    ("fa5s.external-link-alt","#94a3b8"),
}

def get_icon(name, color=None):
    """
    Ambil QIcon dari qtawesome berdasarkan nama logis (key di dict ICONS).
    Contoh: get_icon("add")  atau  get_icon("pause", color="#ff0000")
    """
    if name not in ICONS:
        return QIcon()
    fa_name, default_color = ICONS[name]
    return qta.icon(fa_name, color=color or default_color)

ICON_SIZE = QSize(18, 18)   # ukuran icon di semua tombol

from aria2_client  import Aria2Client
from aria2_manager import Aria2Manager
from aria2_worker  import RefreshWorker
from helpers       import fmt_size, fmt_speed, get_filename, STATUS_LABELS
from styles        import DARK_STYLE


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aria2 GUI")
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)

        self.client       = Aria2Client()
        self.manager      = Aria2Manager()
        self.worker       = None
        self.download_dir = str(Path.home() / "Downloads")
        self._retry_count = 0
        self._downloads   = []   # cache data download untuk context menu & detail

        self.setWindowIcon(get_icon("app"))        # icon taskbar/titlebar
        self.setStyleSheet(DARK_STYLE)
        self._build_ui()
        self._auto_connect()

    # ── BUILD UI ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 10)
        root.setSpacing(12)

        root.addLayout(self._build_header())
        root.addWidget(self._build_url_bar())
        root.addLayout(self._build_toolbar())
        root.addWidget(self._build_table(), stretch=1)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self._lbl_stat = QLabel("—")
        self._lbl_stat.setStyleSheet("color:#475569; font-size:11px;")
        self.status_bar.addPermanentWidget(self._lbl_stat)

    def _build_header(self):
        h = QHBoxLayout()

        title = QLabel("⬇  Aria2 GUI")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color:#e2e8f0; letter-spacing:-0.5px;")

        self.lbl_dot = QLabel("●")
        self.lbl_dot.setStyleSheet("color:#ef4444; font-size:12px;")
        self.lbl_dot.setToolTip("Status koneksi aria2")

        self.lbl_ver = QLabel("Tidak terhubung")
        self.lbl_ver.setStyleSheet("color:#475569; font-size:11px;")

        btn_dir = QPushButton("  Folder Download")
        btn_dir.setObjectName("btn_clear")
        btn_dir.setIcon(get_icon("folder"))
        btn_dir.setIconSize(ICON_SIZE)
        btn_dir.clicked.connect(self._change_dir)

        h.addWidget(title)
        h.addSpacing(10)
        h.addWidget(self.lbl_dot)
        h.addWidget(self.lbl_ver)
        h.addStretch()
        h.addWidget(btn_dir)
        return h

    def _build_url_bar(self):
        frame = QFrame()
        frame.setStyleSheet("QFrame{background:#1a1f2e;border-radius:8px;}")
        h = QHBoxLayout(frame)
        h.setContentsMargins(12, 8, 8, 8)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Masukkan URL download (HTTP, FTP, Magnet)...")
        self.url_input.setStyleSheet("background:transparent;border:none;font-size:13px;")
        self.url_input.returnPressed.connect(self._add_download)

        btn_add = QPushButton("  Tambah")
        btn_add.setObjectName("btn_add")
        btn_add.setIcon(get_icon("add"))
        btn_add.setIconSize(ICON_SIZE)
        btn_add.setFixedHeight(36)
        btn_add.clicked.connect(self._add_download)

        btn_torrent = QPushButton("  Torrent")
        btn_torrent.setObjectName("btn_torrent")
        btn_torrent.setIcon(get_icon("torrent"))
        btn_torrent.setIconSize(ICON_SIZE)
        btn_torrent.setFixedHeight(36)
        btn_torrent.clicked.connect(self._add_torrent)

        h.addWidget(self.url_input)
        h.addWidget(btn_torrent)
        h.addWidget(btn_add)
        return frame

    def _build_toolbar(self):
        h = QHBoxLayout()

        self.btn_pause  = QPushButton("  Pause")
        self.btn_pause.setObjectName("btn_pause")
        self.btn_pause.setIcon(get_icon("pause"))
        self.btn_pause.setIconSize(ICON_SIZE)
        self.btn_pause.clicked.connect(self._pause_selected)

        self.btn_resume = QPushButton("  Resume")
        self.btn_resume.setObjectName("btn_resume")
        self.btn_resume.setIcon(get_icon("resume"))
        self.btn_resume.setIconSize(ICON_SIZE)
        self.btn_resume.clicked.connect(self._resume_selected)

        self.btn_remove = QPushButton("  Hapus")
        self.btn_remove.setObjectName("btn_remove")
        self.btn_remove.setIcon(get_icon("remove"))
        self.btn_remove.setIconSize(ICON_SIZE)
        self.btn_remove.clicked.connect(self._remove_selected)

        self.btn_clear  = QPushButton("  Bersihkan Selesai")
        self.btn_clear.setObjectName("btn_clear")
        self.btn_clear.setIcon(get_icon("clear"))
        self.btn_clear.setIconSize(ICON_SIZE)
        self.btn_clear.clicked.connect(self._clear_completed)

        for btn in [self.btn_pause, self.btn_resume, self.btn_remove, self.btn_clear]:
            h.addWidget(btn)

        h.addStretch()

        self.lbl_dl = QLabel("⬇ —")
        self.lbl_ul = QLabel("⬆ —")
        for lbl in [self.lbl_dl, self.lbl_ul]:
            lbl.setStyleSheet("color:#64748b; font-size:12px;")
            h.addWidget(lbl)

        return h

    def _build_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Nama File", "Ukuran", "Progress", "Kecepatan", "Status", "GID"
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 160)
        self.table.setColumnWidth(1, 90)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 110)
        self.table.setColumnWidth(5, 80)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)

        # Aktifkan context menu klik kanan
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        return self.table

    # ── AUTO CONNECT ──────────────────────────────────────────────────────────

    def _auto_connect(self):
        """Coba connect dulu; kalau gagal, otomatis start aria2."""
        self.status_bar.showMessage("Mencoba koneksi ke aria2...")
        QTimer.singleShot(200, self._try_connect)

    def _try_connect(self):
        if self.client.is_connected():
            self._on_connected()
            return

        self.status_bar.showMessage("aria2 tidak berjalan, mencoba menjalankan otomatis...")
        ok, msg = self.manager.start(
            port=6800,
            download_dir=self.download_dir
        )
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
        self.worker.data_ready.connect(self._update_table)
        self.worker.start()

    def _on_connect_failed(self, msg):
        self.lbl_dot.setStyleSheet("color:#ef4444; font-size:12px;")
        self.lbl_ver.setText("Tidak terhubung")
        self.status_bar.showMessage(f"✖ Gagal terhubung")
        QMessageBox.critical(
            self, "Gagal Terhubung",
            f"Tidak bisa terhubung ke aria2.\n\n{msg}"
        )

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
        d = QFileDialog.getExistingDirectory(self, "Pilih Folder Download", self.download_dir)
        if d:
            self.download_dir = d
            self.status_bar.showMessage(f"Folder download: {d}", 3000)

    # ── CONTEXT MENU ──────────────────────────────────────────────────────────

    def _show_context_menu(self, pos: QPoint):
        row = self.table.rowAt(pos.y())
        if row < 0:
            return

        # Pilih baris yang diklik kanan
        self.table.selectRow(row)

        # Ambil data download dari cache
        d = self._downloads[row] if row < len(self._downloads) else {}
        status = d.get("status", "")

        menu = QMenu(self)
        menu.setStyleSheet("""
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
        """)

        # ── Pause / Resume (tergantung status saat ini) ──
        if status == "active":
            act_pause = menu.addAction(get_icon("pause"), "  Pause")
            act_pause.triggered.connect(self._pause_selected)
        elif status in ("paused", "waiting"):
            act_resume = menu.addAction(get_icon("resume"), "  Resume")
            act_resume.triggered.connect(self._resume_selected)
        else:
            # status complete/error — tampilkan keduanya tapi disabled
            act_pr = menu.addAction("  Pause / Resume")
            act_pr.setEnabled(False)

        menu.addSeparator()

        # ── Buka folder ──
        act_folder = menu.addAction(get_icon("open"), "  Buka Folder File")
        act_folder.triggered.connect(lambda: self._open_folder(d))

        menu.addSeparator()

        # ── Detail ──
        act_detail = menu.addAction(get_icon("detail"), "  Lihat Detail")
        act_detail.triggered.connect(lambda: self._show_detail(d))

        menu.addSeparator()

        # ── Hapus ──
        act_remove = menu.addAction(get_icon("remove"), "  Hapus")
        act_remove.triggered.connect(self._remove_selected)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _open_folder(self, d):
        """Buka folder tempat file disimpan di file manager."""
        try:
            files = d.get("files", [])
            if files:
                path = files[0].get("path", "")
                folder = os.path.dirname(path) if path else self.download_dir
            else:
                folder = self.download_dir

            if not os.path.isdir(folder):
                folder = self.download_dir

            import subprocess, sys
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception as e:
            QMessageBox.warning(self, "Gagal", f"Tidak bisa membuka folder:\n{e}")

    def _show_detail(self, d):
        """Tampilkan dialog detail informasi download."""
        from helpers import fmt_size, fmt_speed, get_filename

        dlg = QDialog(self)
        dlg.setWindowTitle("Detail Download")
        dlg.setMinimumWidth(480)
        dlg.setStyleSheet("""
            QDialog {
                background-color: #0f1117;
                color: #e2e8f0;
            }
            QLabel#lbl_key {
                color: #64748b;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }
            QLabel#lbl_val {
                color: #e2e8f0;
                font-size: 13px;
            }
            QDialogButtonBox QPushButton {
                background-color: #1e2435;
                color: #94a3b8;
                border: 1px solid #2d3748;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 12px;
            }
            QDialogButtonBox QPushButton:hover {
                background-color: #2d3748;
            }
        """)

        total    = int(d.get("totalLength", 0))
        done     = int(d.get("completedLength", 0))
        speed_dl = int(d.get("downloadSpeed", 0))
        speed_ul = int(d.get("uploadSpeed", 0))
        status   = d.get("status", "—")
        gid      = d.get("gid", "—")
        files    = d.get("files", [])
        path     = files[0].get("path", "—") if files else "—"
        uris     = files[0].get("uris", []) if files else []
        url      = uris[0].get("uri", "—") if uris else "—"
        pct      = int(done / total * 100) if total > 0 else 0
        conns    = d.get("connections", "—")
        peers    = d.get("numSeeders", "—")

        label_status, _ = STATUS_LABELS.get(status, (status, "#94a3b8"))

        rows = [
            ("Nama File",   get_filename(d)),
            ("Path",        path),
            ("URL",         url if len(url) < 80 else url[:77] + "..."),
            ("GID",         gid),
            ("Status",      label_status),
            ("Ukuran Total",fmt_size(total) if total else "—"),
            ("Terunduh",    fmt_size(done)),
            ("Progress",    f"{pct}%"),
            ("Kecepatan ⬇", fmt_speed(speed_dl)),
            ("Kecepatan ⬆", fmt_speed(speed_ul)),
            ("Koneksi",     str(conns)),
            ("Seeders",     str(peers)),
        ]

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setContentsMargins(20, 20, 20, 10)
        grid.setColumnMinimumWidth(0, 120)

        for i, (key, val) in enumerate(rows):
            lbl_k = QLabel(key.upper())
            lbl_k.setObjectName("lbl_key")
            lbl_v = QLabel(str(val))
            lbl_v.setObjectName("lbl_val")
            lbl_v.setWordWrap(True)
            lbl_v.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            grid.addWidget(lbl_k, i, 0, Qt.AlignmentFlag.AlignTop)
            grid.addWidget(lbl_v, i, 1)

        # Progress bar di dialog
        bar = QProgressBar()
        bar.setValue(pct)
        bar.setFormat(f"{pct}%")
        bar.setFixedHeight(8)
        bar.setStyleSheet(
            "QProgressBar{background:#1a1f2e;border:none;border-radius:4px;}"
            "QProgressBar::chunk{background:#3b82f6;border-radius:4px;}"
        )

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn_box.rejected.connect(dlg.reject)

        layout = QVBoxLayout(dlg)
        layout.setSpacing(12)
        layout.addLayout(grid)
        layout.addWidget(bar)
        layout.addWidget(btn_box)

        dlg.exec()

    # ── TABLE UPDATE ──────────────────────────────────────────────────────────

    def _update_table(self, downloads, stat):
        self._downloads = downloads   # simpan cache untuk context menu & detail
        self.table.setRowCount(len(downloads))

        for row, d in enumerate(downloads):
            total  = int(d.get("totalLength", 0))
            done   = int(d.get("completedLength", 0))
            speed  = int(d.get("downloadSpeed", 0))
            status = d.get("status", "unknown")
            pct    = int(done / total * 100) if total > 0 else 0

            # Nama file
            self.table.setItem(row, 0, QTableWidgetItem(get_filename(d)))

            # Ukuran
            self.table.setItem(row, 1, QTableWidgetItem(fmt_size(total) if total else "—"))

            # Progress bar
            bar = QProgressBar()
            bar.setValue(pct)
            bar.setFormat(f"{pct}%")
            bar.setTextVisible(True)
            bar.setStyleSheet(
                "QProgressBar{background:#1a1f2e;border:none;border-radius:3px;"
                "color:#94a3b8;font-size:11px;}"
                "QProgressBar::chunk{background:#3b82f6;border-radius:3px;}"
            )
            self.table.setCellWidget(row, 2, bar)

            # Kecepatan
            self.table.setItem(row, 3, QTableWidgetItem(
                fmt_speed(speed) if status == "active" else "—"
            ))

            # Status
            label, color = STATUS_LABELS.get(status, (status, "#94a3b8"))
            st_item = QTableWidgetItem(label)
            st_item.setForeground(QColor(color))
            self.table.setItem(row, 4, st_item)

            # GID
            gid_item = QTableWidgetItem(d.get("gid", ""))
            gid_item.setForeground(QColor("#334155"))
            self.table.setItem(row, 5, gid_item)

            self.table.setRowHeight(row, 42)

        # Update speed labels & stat bar
        self.lbl_dl.setText(f"⬇ {fmt_speed(stat.get('downloadSpeed', 0))}")
        self.lbl_ul.setText(f"⬆ {fmt_speed(stat.get('uploadSpeed', 0))}")
        self._lbl_stat.setText(
            f"Aktif: {stat.get('numActive', 0)}  |  "
            f"Antrian: {stat.get('numWaiting', 0)}  |  "
            f"Total: {len(downloads)}"
        )

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
