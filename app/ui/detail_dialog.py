"""
ui/detail_dialog.py
Dialog informasi lengkap untuk satu item download.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout,
    QLabel, QProgressBar, QDialogButtonBox,
)
from PyQt6.QtCore import Qt

from localization import tr
from helpers import fmt_size, fmt_speed, get_filename
from ui.download_table import STATUS_MAP



def show_detail(parent, d: dict):
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

    tr_key, _ = STATUS_MAP.get(status, ("status_error", "#94a3b8"))

    rows = [
        (tr("detail_filename"),    get_filename(d)),
        (tr("detail_path"),        path),
        (tr("detail_url"),         url if len(url) < 80 else url[:77] + "..."),
        (tr("detail_gid"),         gid),
        (tr("detail_status"),      tr(tr_key)),
        (tr("detail_total"),       fmt_size(total) if total else "—"),
        (tr("detail_downloaded"),  fmt_size(done)),
        (tr("detail_progress"),    f"{pct}%"),
        (tr("detail_speed_dl"),    fmt_speed(speed_dl)),
        (tr("detail_speed_ul"),    fmt_speed(speed_ul)),
        (tr("detail_connections"), str(conns)),
        (tr("detail_seeders"),     str(peers)),
    ]

    dlg = QDialog(parent)
    dlg.setWindowTitle(tr("detail_title"))
    dlg.setMinimumWidth(480)

    grid = QGridLayout()
    grid.setSpacing(10)
    grid.setContentsMargins(20, 20, 20, 10)
    grid.setColumnMinimumWidth(0, 130)

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

    btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
    btn_box.button(QDialogButtonBox.StandardButton.Close).setText(tr("btn_close"))
    btn_box.rejected.connect(dlg.reject)

    layout = QVBoxLayout(dlg)
    layout.setSpacing(12)
    layout.addLayout(grid)
    layout.addWidget(bar)
    layout.addWidget(btn_box)

    dlg.exec()