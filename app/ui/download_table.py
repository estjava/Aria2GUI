"""
ui/download_table.py
Komponen tabel download — setup kolom dan fungsi update data real-time.
"""

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QProgressBar, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from helpers import fmt_size, fmt_speed, get_filename, STATUS_LABELS


def build_table(window) -> QTableWidget:
    """
    Buat dan kembalikan QTableWidget download.
    Menyimpan referensi ke `window.table`.

    Parameter:
        window — instance MainWindow, dipakai untuk connect context menu
    """
    table = QTableWidget()
    table.setColumnCount(6)
    table.setHorizontalHeaderLabels([
        "Nama File", "Ukuran", "Progress", "Kecepatan", "Status", "GID"
    ])

    header = table.horizontalHeader()
    header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
    table.setColumnWidth(1, 90)
    table.setColumnWidth(2, 160)
    table.setColumnWidth(3, 100)
    table.setColumnWidth(4, 110)
    table.setColumnWidth(5, 80)

    table.verticalHeader().setVisible(False)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setShowGrid(False)

    # Aktifkan context menu klik kanan
    table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    table.customContextMenuRequested.connect(window._show_context_menu)

    # Sync tombol toggle saat baris dipilih
    table.itemSelectionChanged.connect(window._sync_pause_resume_btn)

    window.table = table
    return table


def update_table(window, downloads: list, stat: dict):
    """
    Perbarui isi tabel dengan data terbaru dari aria2.
    Juga update label kecepatan & stat bar di window.

    Parameter:
        window    — instance MainWindow
        downloads — list data download dari aria2
        stat      — dict global stat dari aria2
    """
    window._downloads = downloads   # cache untuk context menu & detail dialog
    window.table.setRowCount(len(downloads))

    for row, d in enumerate(downloads):
        total  = int(d.get("totalLength", 0))
        done   = int(d.get("completedLength", 0))
        speed  = int(d.get("downloadSpeed", 0))
        status = d.get("status", "unknown")
        pct    = int(done / total * 100) if total > 0 else 0

        # Nama file
        window.table.setItem(row, 0, QTableWidgetItem(get_filename(d)))

        # Ukuran
        window.table.setItem(row, 1, QTableWidgetItem(
            fmt_size(total) if total else "—"
        ))

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
        window.table.setCellWidget(row, 2, bar)

        # Kecepatan
        window.table.setItem(row, 3, QTableWidgetItem(
            fmt_speed(speed) if status == "active" else "—"
        ))

        # Status
        label, color = STATUS_LABELS.get(status, (status, "#94a3b8"))
        st_item = QTableWidgetItem(label)
        st_item.setForeground(QColor(color))
        window.table.setItem(row, 4, st_item)

        # GID
        gid_item = QTableWidgetItem(d.get("gid", ""))
        gid_item.setForeground(QColor("#334155"))
        window.table.setItem(row, 5, gid_item)

        window.table.setRowHeight(row, 42)

    # Update label kecepatan global
    window.lbl_dl.setText(f"⬇ {fmt_speed(stat.get('downloadSpeed', 0))}")
    window.lbl_ul.setText(f"⬆ {fmt_speed(stat.get('uploadSpeed', 0))}")

    # Update status bar
    window._lbl_stat.setText(
        f"Aktif: {stat.get('numActive', 0)}  |  "
        f"Antrian: {stat.get('numWaiting', 0)}  |  "
        f"Total: {len(downloads)}"
    )
