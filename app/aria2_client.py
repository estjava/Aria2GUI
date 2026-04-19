"""
aria2_client.py
Modul komunikasi ke aria2 via JSON-RPC.
"""

import requests


class Aria2Client:
    def __init__(self, host="localhost", port=6800, secret=""):
        self.url = f"http://{host}:{port}/jsonrpc"
        self.secret = secret
        self._id = 0

    def _next_id(self):
        self._id += 1
        return str(self._id)

    def _call(self, method, params=None):
        if params is None:
            params = []
        if self.secret:
            params = [f"token:{self.secret}"] + params

        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params
        }
        try:
            res = requests.post(self.url, json=payload, timeout=5)
            data = res.json()
            if "error" in data:
                return None
            return data.get("result")
        except Exception:
            return None

    def is_connected(self):
        return self._call("aria2.getVersion") is not None

    def get_version(self):
        result = self._call("aria2.getVersion")
        return result.get("version", "unknown") if result else None

    def add_uri(self, url, options=None):
        params = [[url]]
        if options:
            params.append(options)
        return self._call("aria2.addUri", params)

    def add_torrent(self, torrent_path, options=None):
        import base64
        with open(torrent_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        return self._call("aria2.addTorrent", [data, [], options or {}])

    def tell_active(self):
        return self._call("aria2.tellActive") or []

    def tell_waiting(self, offset=0, num=100):
        return self._call("aria2.tellWaiting", [offset, num]) or []

    def tell_stopped(self, offset=-1, num=100):
        return self._call("aria2.tellStopped", [offset, num]) or []

    def pause(self, gid):
        return self._call("aria2.pause", [gid])

    def unpause(self, gid):
        return self._call("aria2.unpause", [gid])

    def remove(self, gid):
        result = self._call("aria2.remove", [gid])
        if not result:
            result = self._call("aria2.removeDownloadResult", [gid])
        return result

    def get_global_stat(self):
        return self._call("aria2.getGlobalStat") or {}

    def get_global_option(self):
        return self._call("aria2.getGlobalOption") or {}

    def change_global_option(self, options):
        return self._call("aria2.changeGlobalOption", [options])

    def purge_download_result(self):
        return self._call("aria2.purgeDownloadResult")
