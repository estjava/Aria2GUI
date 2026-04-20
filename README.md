# Aria2 GUI
<<<<<<< HEAD
![Python](https://img.shields.io/badge/Rust-1.75-orange)
![License](https://img.shields.io/badge/license-MIT-green)

=======
![Python 3.10]
![aria2c 1.37.0]
![License](https://img.shields.io/badge/license-MIT-green)
>>>>>>> 175bbef1e99b10589eb5084d6a98fadf77a8e6eb

Download manager GUI untuk [aria2](https://aria2.github.io/), dibangun dengan Python & PyQt6.
Auto-start dan auto-connect ke aria2 RPC — tidak perlu menjalankan aria2 secara manual.

---

## Fitur

- ⚡ Auto-start & auto-connect aria2 RPC
- ➕ Tambah download dari URL (HTTP, HTTPS, FTP, Magnet)
- 🌱 Tambah download dari file `.torrent`
- 📊 Progress bar real-time per file
- ⏯ Toggle Pause / Resume dalam satu tombol
- 🗑 Hapus download
- 🧹 Bersihkan download selesai sekaligus
- 📁 Pilih folder download
- 🖱 Context menu klik kanan (Pause/Resume, Buka Folder, Detail, Hapus)
- ℹ️ Dialog detail info lengkap per download
- ⬇⬆ Tampilan kecepatan download & upload global
- 🌙 Dark mode UI
- 🎨 Icon via [qtawesome](https://github.com/spyder-ide/qtawesome) (Font Awesome)

---

## Cara Install

### 1. Install aria2

**Windows:**
Download `aria2c.exe` dari https://github.com/aria2/aria2/releases
lalu tambahkan ke PATH, atau letakkan di folder `app/`.

**Linux (Debian/Ubuntu):**
```bash
sudo apt install aria2
```

**Linux (Arch):**
```bash
sudo pacman -S aria2
```

**macOS:**
```bash
brew install aria2
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Jalankan

```bash
cd app
python main.py
```

---

## Struktur Project

```
Aria2GUI/
├── assets/                  ← resource (icons, dll)
├── requirements.txt
└── app/
    ├── main.py              ← entry point
    ├── main_window.py       ← assembly UI + logika bisnis
    ├── helpers.py           ← fungsi utilitas (format size, speed, dll)
    ├── styles.py            ← stylesheet QSS dark mode
    ├── aria2_core/          ← modul komunikasi aria2
    │   ├── __init__.py
    │   ├── aria2_client.py  ← JSON-RPC client
    │   ├── aria2_manager.py ← auto-start/stop proses aria2c
    │   └── aria2_worker.py  ← background thread polling data
    └── ui/                  ← komponen UI
        ├── __init__.py
        ├── icons.py         ← pemetaan icon qtawesome
        ├── header.py        ← header (judul, status koneksi)
        ├── url_bar.py       ← input URL + tombol tambah
        ├── toolbar.py       ← toolbar aksi download
        ├── download_table.py← tabel download + update data
        ├── context_menu.py  ← context menu klik kanan
        └── detail_dialog.py ← dialog detail download
```

---

## Dependencies

| Package | Versi minimum | Kegunaan |
|---|---|---|
| PyQt6 | 6.4.0 | Framework GUI |
| requests | 2.28.0 | HTTP ke aria2 RPC |
| qtawesome | 1.3.0 | Icon Font Awesome |

---

## Troubleshooting

**`aria2c tidak ditemukan`**
→ Pastikan aria2 sudah terinstall dan bisa dijalankan dari terminal.
Cek dengan: `aria2c --version`

**`ImportError: cannot import name 'Aria2Client' from 'aria2'`**
→ Pastikan folder yang dipakai adalah `aria2_core/`, bukan `aria2/`.
Konflik nama dengan package sistem.

**Port sudah dipakai**
→ Pastikan tidak ada instance aria2 lain yang berjalan di port 6800.
Matikan dengan `pkill aria2c` (Linux/macOS) atau Task Manager (Windows).

---

## Lisensi

[MIT](LICENSE)
