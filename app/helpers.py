"""
helpers.py
Fungsi utilitas dan konstanta yang dipakai oleh modul lain.
"""

import os


# ── Format ukuran bytes ──────────────────────

def fmt_size(b):
    """Konversi bytes ke string yang mudah dibaca (KB, MB, GB)."""
    try:
        b = int(b)
        if b < 1024:
            return f"{b} B"
        elif b < 1024 ** 2:
            return f"{b / 1024:.1f} KB"
        elif b < 1024 ** 3:
            return f"{b / 1024 ** 2:.1f} MB"
        else:
            return f"{b / 1024 ** 3:.2f} GB"
    except Exception:
        return "—"


def fmt_speed(b):
    """Konversi bytes/s ke string kecepatan."""
    try:
        b = int(b)
        if b == 0:
            return "—"
        return fmt_size(b) + "/s"
    except Exception:
        return "—"


# ── Ambil nama file dari data download ──────

def get_filename(d):
    """Ekstrak nama file dari objek download aria2."""
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
    except Exception:
        pass
    return d.get("gid", "Unknown")


# ── Label & warna status download ───────────

STATUS_LABELS = {
    "active":   ("⬇ Downloading", "#4ade80"),
    "waiting":  ("⏸ Waiting",     "#facc15"),
    "paused":   ("⏸ Paused",      "#94a3b8"),
    "complete": ("✔ Complete",    "#60a5fa"),
    "error":    ("✖ Error",       "#f87171"),
    "removed":  ("✖ Removed",     "#f87171"),
}
