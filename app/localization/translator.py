"""
localization/translator.py
Engine localization — singleton Translator untuk akses string dari mana saja.

Cara pakai:
    from localization import tr, set_language

    tr("btn_add")               → "  Tambah"  (sesuai bahasa aktif)
    tr("sb_connected", ver="1.37.0")  → "✔ Terhubung ke aria2 v1.37.0"
    set_language("en")          → ganti ke English
"""

from localization import id as lang_id
from localization import en as lang_en

_LANGUAGES = {
    "id": lang_id.STRINGS,
    "en": lang_en.STRINGS,
}

_DEFAULT_LANG = "id"

# Callback yang dipanggil saat bahasa diganti
# Daftarkan fungsi via: Translator.on_change(callback)
_listeners: list = []


class _Translator:
    def __init__(self):
        self._lang   = _DEFAULT_LANG
        self._strings = _LANGUAGES[_DEFAULT_LANG]

    @property
    def language(self) -> str:
        return self._lang

    def set_language(self, lang: str):
        """Ganti bahasa aktif. lang: 'id' atau 'en'."""
        if lang not in _LANGUAGES:
            raise ValueError(f"Bahasa tidak didukung: '{lang}'. Pilih: {list(_LANGUAGES.keys())}")
        self._lang    = lang
        self._strings = _LANGUAGES[lang]
        for cb in _listeners:
            cb()

    def t(self, key: str, **kwargs) -> str:
        """
        Ambil string berdasarkan key, dengan format opsional.
        Jika key tidak ditemukan, kembalikan key itu sendiri.

        Contoh:
            t("btn_add")
            t("sb_connected", ver="1.37.0")
        """
        s = self._strings.get(key, key)
        if kwargs:
            try:
                s = s.format(**kwargs)
            except KeyError:
                pass
        return s

    def on_change(self, callback):
        """Daftarkan callback yang dipanggil saat bahasa diganti."""
        if callback not in _listeners:
            _listeners.append(callback)

    def off_change(self, callback):
        """Hapus callback."""
        if callback in _listeners:
            _listeners.remove(callback)

    def available_languages(self) -> dict:
        """Kembalikan dict {kode: nama} bahasa yang tersedia."""
        return {
            "id": "Indonesia",
            "en": "English",
        }


# ── Singleton global ──────────────────────────────────────────────────────────
Translator = _Translator()

def tr(key: str, **kwargs) -> str:
    """Shortcut untuk Translator.t()"""
    return Translator.t(key, **kwargs)

def set_language(lang: str):
    """Shortcut untuk Translator.set_language()"""
    Translator.set_language(lang)