"""
aria2_manager.py
Modul untuk menjalankan dan menghentikan proses aria2c secara otomatis.
"""

import os
import sys
import subprocess


class Aria2Manager:
    def __init__(self):
        self.process = None
        self.port = 6800
        self.secret = ""

    def find_aria2(self):
        """Cari aria2c di PATH atau lokasi umum lainnya."""
        import shutil
        path = shutil.which("aria2c")
        if path:
            return path

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
        """
        Jalankan aria2c dengan RPC aktif di background.
        Return: (True, "OK") jika berhasil, (False, pesan_error) jika gagal.
        """
        aria2_path = self.find_aria2()
        if not aria2_path:
            return False, (
                "aria2c tidak ditemukan. Pastikan aria2 sudah terinstall dan ada di PATH.\n"
                "• Linux : sudo apt install aria2\n"
                "• macOS : brew install aria2\n"
                "• Windows: download dari github.com/aria2/aria2/releases"
            )

        self.port = port
        self.secret = secret

        cmd = [
            aria2_path,
            "--enable-rpc=true",
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
            kwargs = dict(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

            self.process = subprocess.Popen(cmd, **kwargs)
            return True, "OK"
        except Exception as e:
            return False, str(e)

    def stop(self):
        """Hentikan proses aria2c yang sedang berjalan."""
        if self.process:
            self.process.terminate()
            self.process = None

    def is_running(self):
        """Cek apakah proses aria2c masih aktif."""
        if self.process is None:
            return False
        return self.process.poll() is None
