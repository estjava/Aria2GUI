# Aria2 GUI — PyQt6

Download manager GUI untuk aria2, dengan auto-connect RPC.

---

## Cara Install

### 1. Install aria2

**Linux (Debian/Ubuntu):**
```bash
sudo apt install aria2
```

**Linux (Arch):**
```bash
sudo pacman -S aria2
```

**Windows:**
Download `aria2c.exe` dari:
https://github.com/aria2/aria2/releases
Letakkan `aria2c.exe` di folder yang sama dengan `aria2_gui.py`,
atau tambahkan ke PATH.

**macOS:**
```bash
brew install aria2
```

---

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

Atau manual:
```bash
pip install PyQt6 requests
```

---

### 3. Jalankan

```bash
python aria2_gui.py
```

Aplikasi akan **otomatis menjalankan aria2** di background dan connect ke RPC-nya.
Tidak perlu menjalankan aria2 secara manual.

---

## Fitur

- ✅ Auto-start & auto-connect aria2 RPC
- ✅ Tambah download dari URL (HTTP, FTP, Magnet)
- ✅ Tambah download dari file .torrent
- ✅ Progress bar real-time per file
- ✅ Pause / Resume / Hapus download
- ✅ Bersihkan download selesai
- ✅ Pilih folder download
- ✅ Tampilan kecepatan download & upload global
- ✅ Dark mode UI

---

## Struktur File

```
aria2gui/
├── aria2_gui.py       ← File utama
├── requirements.txt   ← Dependencies Python
└── README.md          ← Dokumentasi ini
```

---

## Troubleshooting

**"aria2c tidak ditemukan"**
→ Pastikan `aria2c` sudah terinstall dan bisa dijalankan dari terminal.
   Cek dengan: `aria2c --version`

**Port sudah dipakai**
→ Pastikan tidak ada instance aria2 lain yang berjalan di port 6800.
   Matikan dengan: `pkill aria2c` (Linux/macOS) atau Task Manager (Windows).
