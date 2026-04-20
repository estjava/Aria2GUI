"""
localization/en.py
All UI strings in English.
"""

STRINGS = {
    # ── Window ──────────────────────────────────────────────
    "app_title":                "Aria2 GUI",

    # ── Menu: File ──────────────────────────────────────────
    "menu_file":                "File",
    "menu_file_add_torrent":    "Add Torrent...",
    "menu_file_exit":           "Exit",

    # ── Menu: Settings ──────────────────────────────────────
    "menu_settings":            "Settings",
    "menu_settings_dl_folder":  "Download Folder...",
    "menu_settings_language":   "Language",
    "menu_settings_lang_id":    "Indonesia",
    "menu_settings_lang_en":    "English",

    # ── Menu: Help ───────────────────────────────────────────
    "menu_help":                "Help",
    "menu_help_about":          "About",

    # ── Header ──────────────────────────────────────────────
    "header_title":             "Aria2 GUI",
    "btn_folder":               "  Download Folder",

    # ── URL Bar ─────────────────────────────────────────────
    "url_placeholder":          "Enter download URL (HTTP, FTP, Magnet)...",
    "btn_add":                  "  Add",
    "btn_torrent":              "  Torrent",

    # ── Toolbar ─────────────────────────────────────────────
    "btn_pause":                "  Pause",
    "btn_resume":               "  Resume",
    "btn_remove":               "  Remove",
    "btn_clear":                "  Clear Completed",

    # ── Table headers ────────────────────────────────────────
    "col_name":                 "File Name",
    "col_size":                 "Size",
    "col_progress":             "Progress",
    "col_speed":                "Speed",
    "col_status":               "Status",
    "col_gid":                  "GID",

    # ── Download status labels ───────────────────────────────
    "status_active":            "⬇ Downloading",
    "status_waiting":           "⏸ Waiting",
    "status_paused":            "⏸ Paused",
    "status_complete":          "✔ Complete",
    "status_error":             "✖ Error",
    "status_removed":           "✖ Removed",

    # ── Status bar ───────────────────────────────────────────
    "sb_connecting":            "Connecting...",
    "sb_starting":              "Starting aria2...",
    "sb_trying":                "Trying to connect to aria2...",
    "sb_starting_auto":         "aria2 is not running, trying to start automatically...",
    "sb_connected":             "✔ Connected to aria2 v{ver}",
    "sb_connected_label":       "aria2 v{ver} — connected",
    "sb_disconnected":          "Not connected",
    "sb_failed":                "✖ Failed: {msg}",
    "sb_added":                 "✔ Download added: {url}",
    "sb_torrent_added":         "✔ Torrent added: {name}",
    "sb_paused":                "⏸ Download paused",
    "sb_resumed":               "▶ Download resumed",
    "sb_removed":               "🗑 Download removed",
    "sb_cleared":               "✔ Completed downloads cleared",
    "sb_folder_changed":        "📁 Download folder: {path}",
    "sb_active":                "Active",
    "sb_waiting":               "Waiting",
    "sb_total":                 "Total",

    # ── Dialogs ──────────────────────────────────────────────
    "dlg_not_connected_title":  "Not Connected",
    "dlg_not_connected_msg":    "aria2 is not connected.",
    "dlg_failed_title":         "Failed",
    "dlg_failed_add":           "Failed to add URL.",
    "dlg_failed_torrent":       "Failed to add torrent.",
    "dlg_connect_fail_title":   "Connection Failed",
    "dlg_connect_fail_msg":     "Cannot connect to aria2.\n\n{msg}",
    "dlg_remove_title":         "Remove Download",
    "dlg_remove_msg":           "Are you sure you want to remove this download?",
    "dlg_close_title":          "Close Application",
    "dlg_close_msg":            "Do you also want to stop aria2?",
    "dlg_folder_title":         "Select Download Folder",
    "dlg_torrent_title":        "Select .torrent file",
    "dlg_torrent_filter":       "Torrent Files (*.torrent)",
    "dlg_open_folder_fail":     "Cannot open folder:\n{err}",

    # ── Context menu ─────────────────────────────────────────
    "ctx_pause":                "  Pause",
    "ctx_resume":               "  Resume",
    "ctx_pause_resume":         "  Pause / Resume",
    "ctx_open_folder":          "  Open File Folder",
    "ctx_detail":               "  View Details",
    "ctx_remove":               "  Remove",

    # ── Detail dialog ────────────────────────────────────────
    "detail_title":             "Download Details",
    "detail_filename":          "File Name",
    "detail_path":              "Path",
    "detail_url":               "URL",
    "detail_gid":               "GID",
    "detail_status":            "Status",
    "detail_total":             "Total Size",
    "detail_downloaded":        "Downloaded",
    "detail_progress":          "Progress",
    "detail_speed_dl":          "Speed ⬇",
    "detail_speed_ul":          "Speed ⬆",
    "detail_connections":       "Connections",
    "detail_seeders":           "Seeders",
    "btn_close":                "Close",

    # ── About dialog ─────────────────────────────────────────
    "about_title":              "About Aria2 GUI",
    "about_desc":               "GUI download manager for aria2\nBuilt with Python & PyQt6",
    "about_version":            "Version: 1.0.0",
    "about_license":            "License: MIT",
}