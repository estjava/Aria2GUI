"""
ui/download_table.py
Komponen tabel download — setup kolom dan fungsi update data real-time.
"""

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QProgressBar, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from localization import tr
from helpers import fmt_size, fmt_speed, get_filename

# Mapping status aria2 → (key tr, warna)
STATUS_MAP = {
    "active":   ("status_active",   "#4ade80"),
    "waiting":  ("status_waiting",  "#facc15"),
    "paused":   ("status_paused",   "#94a3b8"),
    "complete": ("status_complete", "#60a5fa"),
    "error":    ("status_error",    "#f87171"),
    "removed":  ("status_removed",  "#f87171"),
}


def build_table(window) -> QTableWidget:
    table = QTableWidget()
    table.setColumnCount(6)
    table.setHorizontalHeaderLabels([
        tr("col_name"), tr("col_size"), tr("col_progress"),
        tr("col_speed"), tr("col_status"), tr("col_gid"),
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

    table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    table.customContextMenuRequested.connect(window._show_context_menu)
    table.itemSelectionChanged.connect(window._sync_pause_resume_btn)

    window.table = table
    return table


def update_table(window, downloads: list, stat: dict):
    window._downloads = downloads
    window.table.setRowCount(len(downloads))

    for row, d in enumerate(downloads):
        total  = int(d.get("totalLength", 0))
        done   = int(d.get("completedLength", 0))
        speed  = int(d.get("downloadSpeed", 0))
        status = d.get("status", "unknown")
        pct    = int(done / total * 100) if total > 0 else 0

        window.table.setItem(row, 0, QTableWidgetItem(get_filename(d)))
        window.table.setItem(row, 1, QTableWidgetItem(
            fmt_size(total) if total else "—"
        ))

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

        window.table.setItem(row, 3, QTableWidgetItem(
            fmt_speed(speed) if status == "active" else "—"
        ))

        tr_key, color = STATUS_MAP.get(status, ("status_error", "#94a3b8"))
        st_item = QTableWidgetItem(tr(tr_key))
        st_item.setForeground(QColor(color))
        window.table.setItem(row, 4, st_item)

        gid_item = QTableWidgetItem(d.get("gid", ""))
        gid_item.setForeground(QColor("#334155"))
        window.table.setItem(row, 5, gid_item)

        window.table.setRowHeight(row, 42)

    window.lbl_dl.setText(f"⬇ {fmt_speed(stat.get('downloadSpeed', 0))}")
    window.lbl_ul.setText(f"⬆ {fmt_speed(stat.get('uploadSpeed', 0))}")
    window._lbl_stat.setText(
        f"{tr('sb_active')}: {stat.get('numActive', 0)}  |  "
        f"{tr('sb_waiting')}: {stat.get('numWaiting', 0)}  |  "
        f"{tr('sb_total')}: {len(downloads)}"
    )