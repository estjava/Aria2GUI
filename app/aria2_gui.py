"""
Aria2 GUI - PyQt6
Auto-connect & auto-start aria2 RPC
"""

import sys
import os
import subprocess
import time
import requests
import json
import threading
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QTableWidget, QTableWidgetItem,
    QProgressBar, QHeaderView, QMessageBox, QFileDialog, QFrame,
    QSystemTrayIcon, QMenu, QStatusBar, QSplitter, QGroupBox,
    QSpinBox, QCheckBox, QTabWidget, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QColor, QFont, QAction, QPalette


# ─────────────────────────────────────────────
#  ARIA2 RPC CLIENT
# ─────────────────────────────────────────────

class Aria2Client:
    def __init__(self, host="localhost", port=6800, secret=""):
        self.url = f"http://{host}:{port}/jsonrpc"
        self.secret = secret
        self._id = 0

    def _next_id(self):
        self._id += 1
        return str(self._id)

    def _call(self, method, params=None):
        if params is None:
            params = []
        if self.secret:
            params = [f"token:{self.secret}"] + params

        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params
        }
        try:
            res = requests.post(self.url, json=payload, timeout=5)
            data = res.json()
            if "error" in data:
                return None
            return data.get("result")
        except Exception:
            return None

    def is_connected(self):
        result = self._call("aria2.getVersion")
        return result is not None

    def get_version(self):
        result = self._call("aria2.getVersion")
        return result.get("version", "unknown") if result else None

    def add_uri(self, url, options=None):
        params = [[url]]
        if options:
            params.append(options)
        return self._call("aria2.addUri", params)

    def add_torrent(self, torrent_path, options=None):
        import base64
        with open(torrent_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        params = [data, [], options or {}]
        return self._call("aria2.addTorrent", params)

    def tell_active(self):
        return self._call("aria2.tellActive") or []

    def tell_waiting(self, offset=0, num=100):
        return self._call("aria2.tellWaiting", [offset, num]) or []

    def tell_stopped(self, offset=-1, num=100):
        return self._call("aria2.tellStopped", [offset, num]) or []

    def pause(self, gid):
        return self._call("aria2.pause", [gid])

    def unpause(self, gid):
        return self._call("aria2.unpause", [gid])

    def remove(self, gid):
        result = self._call("aria2.remove", [gid])
        if not result:
            result = self._call("aria2.removeDownloadResult", [gid])
        return result

    def get_global_stat(self):
        return self._call("aria2.getGlobalStat") or {}

    def get_global_option(self):
        return self._call("aria2.getGlobalOption") or {}

    def change_global_option(self, options):
        return self._call("aria2.changeGlobalOption", [options])

    def purge_download_result(self):
        return self._call("aria2.purgeDownloadResult")


# ─────────────────────────────────────────────
#  ARIA2 PROCESS MANAGER (Auto-start)
# ─────────────────────────────────────────────

class Aria2Manager:
    def __init__(self):
        self.process = None
        self.port = 6800
        self.secret = ""

    def find_aria2(self):
        """Cari aria2c di PATH atau folder yang umum."""
        import shutil
        path = shutil.which("aria2c")
        if path:
            return path

        # Windows common paths
        candidates = [
            r"C:\Program Files\aria2\aria2c.exe",
            r"C:\aria2\aria2c.exe",
            os.path.join(os.path.dirname(__file__), "aria2c.exe"),
            os.path.join(os.path.dirname(__file__), "aria2c"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
        return None

    def start(self, port=6800, secret="", download_dir=None):
        """Start aria2c dengan RPC enabled."""
        aria2_path = self.find_aria2()
        if not aria2_path:
            return False, "aria2c tidak ditemukan. Pastikan aria2 sudah terinstall dan ada di PATH."

        self.port = port
        self.secret = secret

        cmd = [
            aria2_path,
            f"--enable-rpc=true",
            f"--rpc-listen-port={port}",
            "--rpc-allow-origin-all=true",
            "--rpc-listen-all=true",
            "--continue=true",
            "--max-concurrent-downloads=5",
            "--max-connection-per-server=16",
            "--split=16",
            "--min-split-size=1M",
            "--console-log-level=error",
            "--quiet=true",
        ]

        if secret:
            cmd.append(f"--rpc-secret={secret}")

        if download_dir:
            cmd.append(f"--dir={download_dir}")

        try:
            if sys.platform == "win32":
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            return True, "OK"
        except Exception as e:
            return False, str(e)

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process = None

    def is_running(self):
        if self.process is None:
            return False
        return self.process.poll() is None


# ─────────────────────────────────────────────
#  REFRESH THREAD
# ─────────────────────────────────────────────

class RefreshWorker(QThread):
    data_ready = pyqtSignal(list, dict)

    def __init__(self, client):
        super().__init__()
        self.client = client
        self._running = True

    def run(self):
        while self._running:
            try:
                active = self.client.tell_active()
                waiting = self.client.tell_waiting()
                stopped = self.client.tell_stopped()
                all_downloads = active + waiting + stopped
                stat = self.client.get_global_stat()
                self.data_ready.emit(all_downloads, stat)
            except Exception:
                pass
            time.sleep(1)

    def stop(self):
        self._running = False


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def fmt_size(b):
    try:
        b = int(b)
        if b < 1024:
            return f"{b} B"
        elif b < 1024**2:
            return f"{b/1024:.1f} KB"
        elif b < 1024**3:
            return f"{b/1024**2:.1f} MB"
        else:
            return f"{b/1024**3:.2f} GB"
    except:
        return "—"

def fmt_speed(b):
    try:
        b = int(b)
        if b == 0:
            return "—"
        return fmt_size(b) + "/s"
    except:
        return "—"

def get_filename(d):
    try:
        files = d.get("files", [])
        if files:
            path = files[0].get("path", "")
            if path:
                return os.path.basename(path)
        uris = d.get("files", [{}])[0].get("uris", [{}])
        if uris:
            uri = uris[0].get("uri", "")
            return uri.split("/")[-1] or uri
    except:
        pass
    return d.get("gid", "Unknown")

STATUS_LABELS = {
    "active":   ("⬇ Downloading", "#4ade80"),
    "waiting":  ("⏸ Waiting",     "#facc15"),
    "paused":   ("⏸ Paused",      "#94a3b8"),
    "complete": ("✔ Complete",    "#60a5fa"),
    "error":    ("✖ Error",       "#f87171"),
    "removed":  ("✖ Removed",     "#f87171"),
}


# ─────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────

DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #0f1117;
    color: #e2e8f0;
    font-family: 'Segoe UI', 'SF Pro Display', sans-serif;
    font-size: 13px;
}

QGroupBox {
    border: 1px solid #1e2435;
    border-radius: 8px;
    margin-top: 12px;
    padding: 10px;
    color: #94a3b8;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
    text-transform: uppercase;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}

QLineEdit {
    background-color: #1a1f2e;
    border: 1px solid #2d3748;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e2e8f0;
    selection-background-color: #3b82f6;
}
QLineEdit:focus {
    border-color: #3b82f6;
}

QPushButton {
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 12px;
}
QPushButton#btn_add {
    background-color: #3b82f6;
    color: white;
    border: none;
}
QPushButton#btn_add:hover { background-color: #2563eb; }
QPushButton#btn_add:pressed { background-color: #1d4ed8; }

QPushButton#btn_pause {
    background-color: #1e2435;
    color: #facc15;
    border: 1px solid #2d3748;
}
QPushButton#btn_pause:hover { background-color: #2d3748; }

QPushButton#btn_resume {
    background-color: #1e2435;
    color: #4ade80;
    border: 1px solid #2d3748;
}
QPushButton#btn_resume:hover { background-color: #2d3748; }

QPushButton#btn_remove {
    background-color: #1e2435;
    color: #f87171;
    border: 1px solid #2d3748;
}
QPushButton#btn_remove:hover { background-color: #2d3748; }

QPushButton#btn_clear {
    background-color: #1e2435;
    color: #94a3b8;
    border: 1px solid #2d3748;
}
QPushButton#btn_clear:hover { background-color: #2d3748; }

QPushButton#btn_torrent {
    background-color: #1e2435;
    color: #a78bfa;
    border: 1px solid #2d3748;
}
QPushButton#btn_torrent:hover { background-color: #2d3748; }

QTableWidget {
    background-color: #0f1117;
    border: none;
    gridline-color: #1a1f2e;
    border-radius: 8px;
    outline: none;
}
QTableWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #1a1f2e;
}
QTableWidget::item:selected {
    background-color: #1e2a3a;
    color: #e2e8f0;
}
QHeaderView::section {
    background-color: #1a1f2e;
    color: #64748b;
    padding: 8px 10px;
    border: none;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

QProgressBar {
    background-color: #1a1f2e;
    border: none;
    border-radius: 3px;
    height: 6px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #3b82f6;
    border-radius: 3px;
}

QStatusBar {
    background-color: #0a0d14;
    color: #475569;
    border-top: 1px solid #1a1f2e;
    font-size: 11px;
    padding: 2px 10px;
}

QTabWidget::pane {
    border: 1px solid #1e2435;
    border-radius: 8px;
    background: #0f1117;
}
QTabBar::tab {
    background: #1a1f2e;
    color: #64748b;
    padding: 8px 20px;
    border: none;
    border-radius: 6px 6px 0 0;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #0f1117;
    color: #e2e8f0;
    border-bottom: 2px solid #3b82f6;
}

QScrollBar:vertical {
    background: #0f1117;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #2d3748;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QLabel#lbl_status_dot {
    font-size: 10px;
}
QLabel#lbl_version {
    color: #475569;
    font-size: 11px;
}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aria2 GUI")
        self.setMinimumSize(900, 600)
        self.resize(1100, 700)

        self.client = Aria2Client()
        self.manager = Aria2Manager()
        self.worker = None
        self.download_dir = str(Path.home() / "Downloads")

        self.setStyleSheet(DARK_STYLE)
        self._build_ui()
        self._auto_connect()

    # ── BUILD UI ──────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 10)
        root.setSpacing(12)

        # Header
        root.addLayout(self._header())

        # Add URL bar
        root.addWidget(self._url_bar())

        # Toolbar
        root.addLayout(self._toolbar())

        # Download table
        root.addWidget(self._table(), stretch=1)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self._lbl_stat = QLabel("—")
        self._lbl_stat.setObjectName("lbl_version")
        self.status.addPermanentWidget(self._lbl_stat)

    def _header(self):
        h = QHBoxLayout()

        title = QLabel("⬇  Aria2 GUI")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #e2e8f0; letter-spacing: -0.5px;")

        self.lbl_dot = QLabel("●")
        self.lbl_dot.setObjectName("lbl_status_dot")
        self.lbl_dot.setStyleSheet("color: #ef4444; font-size:12px;")
        self.lbl_dot.setToolTip("Status koneksi aria2")

        self.lbl_ver = QLabel("Tidak terhubung")
        self.lbl_ver.setObjectName("lbl_version")

        h.addWidget(title)
        h.addSpacing(10)
        h.addWidget(self.lbl_dot)
        h.addWidget(self.lbl_ver)
        h.addStretch()

        btn_dir = QPushButton("📁 Folder Download")
        btn_dir.setObjectName("btn_clear")
        btn_dir.clicked.connect(self._change_dir)
        h.addWidget(btn_dir)
        return h

    def _url_bar(self):
        frame = QFrame()
        frame.setStyleSheet("QFrame { background:#1a1f2e; border-radius:8px; }")
        h = QHBoxLayout(frame)
        h.setContentsMargins(12, 8, 8, 8)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Masukkan URL download (HTTP, FTP, Magnet)...")
        self.url_input.setStyleSheet("background:transparent; border:none; font-size:13px;")
        self.url_input.returnPressed.connect(self._add_download)

        btn = QPushButton("+ Tambah")
        btn.setObjectName("btn_add")
        btn.setFixedHeight(36)
        btn.clicked.connect(self._add_download)

        btn_torrent = QPushButton("🌱 Torrent")
        btn_torrent.setObjectName("btn_torrent")
        btn_torrent.setFixedHeight(36)
        btn_torrent.clicked.connect(self._add_torrent)

        h.addWidget(self.url_input)
        h.addWidget(btn_torrent)
        h.addWidget(btn)
        return frame

    def _toolbar(self):
        h = QHBoxLayout()

        self.btn_pause = QPushButton("⏸ Pause")
        self.btn_pause.setObjectName("btn_pause")
        self.btn_pause.clicked.connect(self._pause_selected)

        self.btn_resume = QPushButton("▶ Resume")
        self.btn_resume.setObjectName("btn_resume")
        self.btn_resume.clicked.connect(self._resume_selected)

        self.btn_remove = QPushButton("✖ Hapus")
        self.btn_remove.setObjectName("btn_remove")
        self.btn_remove.clicked.connect(self._remove_selected)

        self.btn_clear = QPushButton("🧹 Bersihkan Selesai")
        self.btn_clear.setObjectName("btn_clear")
        self.btn_clear.clicked.connect(self._clear_completed)

        for b in [self.btn_pause, self.btn_resume, self.btn_remove, self.btn_clear]:
            h.addWidget(b)

        h.addStretch()

        # Speed stat labels
        self.lbl_dl = QLabel("⬇ —")
        self.lbl_ul = QLabel("⬆ —")
        for lbl in [self.lbl_dl, self.lbl_ul]:
            lbl.setStyleSheet("color:#64748b; font-size:12px;")
            h.addWidget(lbl)

        return h

    def _table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Nama File", "Ukuran", "Progress", "Kecepatan", "Status", "GID"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 160)
        self.table.setColumnWidth(1, 90)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 110)
        self.table.setColumnWidth(5, 80)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        return self.table

    # ── AUTO CONNECT ──────────────────────────

    def _auto_connect(self):
        """Coba connect dulu, kalau gagal auto-start aria2."""
        self.status.showMessage("Mencoba koneksi ke aria2...")
        QTimer.singleShot(200, self._try_connect)

    def _try_connect(self):
        if self.client.is_connected():
            self._on_connected()
        else:
            self.status.showMessage("aria2 tidak berjalan, mencoba menjalankan otomatis...")
            ok, msg = self.manager.start(
                port=6800,
                secret=self.manager.secret,
                download_dir=self.download_dir
            )
            if not ok:
                self._on_connect_failed(msg)
                return
            # Tunggu aria2 siap (max 5 detik)
            QTimer.singleShot(500, self._wait_ready)
            self._retry_count = 0

    def _wait_ready(self):
        if self.client.is_connected():
            self._on_connected()
        else:
            self._retry_count += 1
            if self._retry_count >= 10:
                self._on_connect_failed("aria2 tidak merespons setelah dijalankan.")
            else:
                QTimer.singleShot(500, self._wait_ready)

    def _on_connected(self):
        ver = self.client.get_version()
        self.lbl_dot.setStyleSheet("color: #4ade80; font-size:12px;")
        self.lbl_ver.setText(f"aria2 v{ver} — terhubung")
        self.status.showMessage(f"✔ Terhubung ke aria2 v{ver}", 4000)

        # Start refresh worker
        self.worker = RefreshWorker(self.client)
        self.worker.data_ready.connect(self._update_table)
        self.worker.start()

    def _on_connect_failed(self, msg):
        self.lbl_dot.setStyleSheet("color: #ef4444; font-size:12px;")
        self.lbl_ver.setText("Tidak terhubung")
        self.status.showMessage(f"✖ Gagal: {msg}")
        QMessageBox.critical(
            self, "Gagal Terhubung",
            f"Tidak bisa terhubung ke aria2.\n\n{msg}\n\n"
            "Pastikan aria2 sudah terinstall:\n"
            "• Linux: sudo apt install aria2\n"
            "• Windows: download dari github.com/aria2/aria2/releases"
        )

    # ── DOWNLOAD ACTIONS ──────────────────────

    def _add_download(self):
        url = self.url_input.text().strip()
        if not url:
            return
        if not self.client.is_connected():
            QMessageBox.warning(self, "Tidak terhubung", "aria2 belum terhubung.")
            return

        options = {"dir": self.download_dir}
        result = self.client.add_uri(url, options)
        if result:
            self.url_input.clear()
            self.status.showMessage(f"✔ Download ditambahkan: {url[:60]}...", 3000)
        else:
            QMessageBox.warning(self, "Gagal", "Gagal menambahkan URL.")

    def _add_torrent(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Pilih file .torrent", self.download_dir, "Torrent Files (*.torrent)"
        )
        if not path:
            return
        options = {"dir": self.download_dir}
        result = self.client.add_torrent(path, options)
        if result:
            self.status.showMessage(f"✔ Torrent ditambahkan: {os.path.basename(path)}", 3000)
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
            self, "Hapus Download",
            "Yakin ingin menghapus download ini?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.client.remove(gid)

    def _clear_completed(self):
        self.client.purge_download_result()
        self.status.showMessage("✔ Download selesai dibersihkan", 2000)

    def _change_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Pilih Folder Download", self.download_dir)
        if d:
            self.download_dir = d
            self.status.showMessage(f"Folder download: {d}", 3000)

    # ── TABLE UPDATE ──────────────────────────

    def _update_table(self, downloads, stat):
        self.table.setRowCount(len(downloads))
        for row, d in enumerate(downloads):
            name = get_filename(d)
            total = int(d.get("totalLength", 0))
            done = int(d.get("completedLength", 0))
            speed_dl = int(d.get("downloadSpeed", 0))
            status = d.get("status", "unknown")
            gid = d.get("gid", "")

            pct = int(done / total * 100) if total > 0 else 0

            # Name
            self.table.setItem(row, 0, QTableWidgetItem(name))

            # Size
            size_str = fmt_size(total) if total else "—"
            self.table.setItem(row, 1, QTableWidgetItem(size_str))

            # Progress bar
            bar = QProgressBar()
            bar.setValue(pct)
            bar.setFormat(f"{pct}%")
            bar.setTextVisible(True)
            bar.setStyleSheet("""
                QProgressBar { background:#1a1f2e; border:none; border-radius:3px; color:#94a3b8; font-size:11px; }
                QProgressBar::chunk { background:#3b82f6; border-radius:3px; }
            """)
            self.table.setCellWidget(row, 2, bar)

            # Speed
            spd = fmt_speed(speed_dl) if status == "active" else "—"
            self.table.setItem(row, 3, QTableWidgetItem(spd))

            # Status
            label, color = STATUS_LABELS.get(status, (status, "#94a3b8"))
            st_item = QTableWidgetItem(label)
            st_item.setForeground(QColor(color))
            self.table.setItem(row, 4, st_item)

            # GID (hidden-ish)
            gid_item = QTableWidgetItem(gid)
            gid_item.setForeground(QColor("#334155"))
            self.table.setItem(row, 5, gid_item)

            self.table.setRowHeight(row, 42)

        # Global stat
        dl_speed = fmt_speed(stat.get("downloadSpeed", 0))
        ul_speed = fmt_speed(stat.get("uploadSpeed", 0))
        self.lbl_dl.setText(f"⬇ {dl_speed}")
        self.lbl_ul.setText(f"⬆ {ul_speed}")

        active = stat.get("numActive", 0)
        waiting = stat.get("numWaiting", 0)
        self._lbl_stat.setText(f"Aktif: {active}  |  Antrian: {waiting}  |  Total: {len(downloads)}")

    # ── CLOSE ─────────────────────────────────

    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
            self.worker.wait(2000)

        # Tanya apakah ingin matikan aria2
        if self.manager.is_running():
            reply = QMessageBox.question(
                self, "Tutup Aplikasi",
                "Apakah ingin menghentikan aria2 juga?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.manager.stop()

        event.accept()


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Aria2 GUI")
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
