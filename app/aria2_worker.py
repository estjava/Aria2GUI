"""
aria2_worker.py
Background thread untuk polling data download dari aria2 secara berkala.
"""

import time
from PyQt6.QtCore import QThread, pyqtSignal


class RefreshWorker(QThread):
    """
    Menjalankan polling ke aria2 tiap 1 detik di thread terpisah
    agar UI tidak freeze.

    Signal:
        data_ready(list, dict) — list download + global stat
    """
    data_ready = pyqtSignal(list, dict)

    def __init__(self, client):
        super().__init__()
        self.client = client
        self._running = True

    def run(self):
        while self._running:
            try:
                active  = self.client.tell_active()
                waiting = self.client.tell_waiting()
                stopped = self.client.tell_stopped()
                all_downloads = active + waiting + stopped
                stat = self.client.get_global_stat()
                self.data_ready.emit(all_downloads, stat)
            except Exception:
                pass
            time.sleep(1)

    def stop(self):
        """Hentikan loop polling."""
        self._running = False
