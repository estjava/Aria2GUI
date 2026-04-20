"""
localization/id.py
Semua string UI dalam Bahasa Indonesia.
"""

STRINGS = {
    # ── Window ──────────────────────────────────────────────
    "app_title":                "Aria2 GUI",

    # ── Menu: File ──────────────────────────────────────────
    "menu_file":                "File",
    "menu_file_add_torrent":    "Tambah Torrent...",
    "menu_file_exit":           "Keluar",

    # ── Menu: Settings ──────────────────────────────────────
    "menu_settings":            "Pengaturan",
    "menu_settings_dl_folder":  "Folder Download...",
    "menu_settings_language":   "Bahasa",
    "menu_settings_lang_id":    "Indonesia",
    "menu_settings_lang_en":    "English",

    # ── Menu: Help ───────────────────────────────────────────
    "menu_help":                "Bantuan",
    "menu_help_about":          "Tentang",

    # ── Header ──────────────────────────────────────────────
    "header_title":             "Aria2 GUI",
    "btn_folder":               "  Folder Download",

    # ── URL Bar ─────────────────────────────────────────────
    "url_placeholder":          "Masukkan URL download (HTTP, FTP, Magnet)...",
    "btn_add":                  "  Tambah",
    "btn_torrent":              "  Torrent",

    # ── Toolbar ─────────────────────────────────────────────
    "btn_pause":                "  Pause",
    "btn_resume":               "  Resume",
    "btn_remove":               "  Hapus",
    "btn_clear":                "  Bersihkan Selesai",

    # ── Table headers ────────────────────────────────────────
    "col_name":                 "Nama File",
    "col_size":                 "Ukuran",
    "col_progress":             "Progress",
    "col_speed":                "Kecepatan",
    "col_status":               "Status",
    "col_gid":                  "GID",

    # ── Download status labels ───────────────────────────────
    "status_active":            "⬇ Mengunduh",
    "status_waiting":           "⏸ Menunggu",
    "status_paused":            "⏸ Dijeda",
    "status_complete":          "✔ Selesai",
    "status_error":             "✖ Error",
    "status_removed":           "✖ Dihapus",

    # ── Status bar ───────────────────────────────────────────
    "sb_connecting":            "Menghubungkan...",
    "sb_starting":              "Memulai aria2...",
    "sb_trying":                "Mencoba koneksi ke aria2...",
    "sb_starting_auto":         "aria2 tidak berjalan, mencoba menjalankan otomatis...",
    "sb_connected":             "✔ Terhubung ke aria2 v{ver}",
    "sb_connected_label":       "aria2 v{ver} — terhubung",
    "sb_disconnected":          "Tidak terhubung",
    "sb_failed":                "✖ Gagal: {msg}",
    "sb_added":                 "✔ Download ditambahkan: {url}",
    "sb_torrent_added":         "✔ Torrent ditambahkan: {name}",
    "sb_paused":                "⏸ Download di-pause",
    "sb_resumed":               "▶ Download dilanjutkan",
    "sb_removed":               "🗑 Download dihapus",
    "sb_cleared":               "✔ Download selesai dibersihkan",
    "sb_folder_changed":        "📁 Folder download: {path}",
    "sb_active":                "Aktif",
    "sb_waiting":               "Antrian",
    "sb_total":                 "Total",

    # ── Dialogs ──────────────────────────────────────────────
    "dlg_not_connected_title":  "Tidak Terhubung",
    "dlg_not_connected_msg":    "aria2 belum terhubung.",
    "dlg_failed_title":         "Gagal",
    "dlg_failed_add":           "Gagal menambahkan URL.",
    "dlg_failed_torrent":       "Gagal menambahkan torrent.",
    "dlg_connect_fail_title":   "Gagal Terhubung",
    "dlg_connect_fail_msg":     "Tidak bisa terhubung ke aria2.\n\n{msg}",
    "dlg_remove_title":         "Hapus Download",
    "dlg_remove_msg":           "Yakin ingin menghapus download ini?",
    "dlg_close_title":          "Tutup Aplikasi",
    "dlg_close_msg":            "Apakah ingin menghentikan aria2 juga?",
    "dlg_folder_title":         "Pilih Folder Download",
    "dlg_torrent_title":        "Pilih file .torrent",
    "dlg_torrent_filter":       "Torrent Files (*.torrent)",
    "dlg_open_folder_fail":     "Tidak bisa membuka folder:\n{err}",

    # ── Context menu ─────────────────────────────────────────
    "ctx_pause":                "  Pause",
    "ctx_resume":               "  Resume",
    "ctx_pause_resume":         "  Pause / Resume",
    "ctx_open_folder":          "  Buka Folder File",
    "ctx_detail":               "  Lihat Detail",
    "ctx_remove":               "  Hapus",

    # ── Detail dialog ────────────────────────────────────────
    "detail_title":             "Detail Download",
    "detail_filename":          "Nama File",
    "detail_path":              "Path",
    "detail_url":               "URL",
    "detail_gid":               "GID",
    "detail_status":            "Status",
    "detail_total":             "Ukuran Total",
    "detail_downloaded":        "Terunduh",
    "detail_progress":          "Progress",
    "detail_speed_dl":          "Kecepatan ⬇",
    "detail_speed_ul":          "Kecepatan ⬆",
    "detail_connections":       "Koneksi",
    "detail_seeders":           "Seeders",
    "btn_close":                "Tutup",

    # ── About dialog ─────────────────────────────────────────
    "about_title":              "Tentang Aria2 GUI",
    "about_desc":               "Download manager GUI untuk aria2\nDibangun dengan Python & PyQt6",
    "about_version":            "Versi: 1.0.0",
    "about_license":            "Lisensi: MIT",
}