"""
ui/detail_dialog.py
Dialog informasi lengkap untuk satu item download.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout,
    QLabel, QProgressBar, QDialogButtonBox,
)
from PyQt6.QtCore import Qt

from helpers import fmt_size, fmt_speed, get_filename, STATUS_LABELS


DIALOG_STYLE = """
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
"""


def show_detail(parent, d: dict):
    """
    Tampilkan dialog detail informasi download.

    Parameter:
        parent — widget parent (MainWindow)
        d      — dict data download dari aria2
    """
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
        ("Nama File",    get_filename(d)),
        ("Path",         path),
        ("URL",          url if len(url) < 80 else url[:77] + "..."),
        ("GID",          gid),
        ("Status",       label_status),
        ("Ukuran Total", fmt_size(total) if total else "—"),
        ("Terunduh",     fmt_size(done)),
        ("Progress",     f"{pct}%"),
        ("Kecepatan ⬇",  fmt_speed(speed_dl)),
        ("Kecepatan ⬆",  fmt_speed(speed_ul)),
        ("Koneksi",      str(conns)),
        ("Seeders",      str(peers)),
    ]

    # ── Build dialog ─────────────────────────────────
    dlg = QDialog(parent)
    dlg.setWindowTitle("Detail Download")
    dlg.setMinimumWidth(480)
    dlg.setStyleSheet(DIALOG_STYLE)

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
