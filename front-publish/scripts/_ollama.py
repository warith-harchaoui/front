"""
_ollama.py — shared Ollama client helpers used by alt_from_ollama,
captions_from_whisper (vocab biasing), and other scripts that talk to a
local Ollama daemon.

Author
------
`Warith Harchaoui, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import locale
import os
import platform
from typing import Optional


OLLAMA_URL: str = os.environ.get("OLLAMA_URL", "http://localhost:11434")

DEFAULT_BASE: str = os.environ.get("OLLAMA_MODEL_BASE", "gemma4:e4b")


BANNED_PREFIXES: dict[str, tuple[str, ...]] = {
    "en": ("image of", "picture of", "photo of", "photograph of", "illustration of"),
    "fr": ("image de", "photo de", "photographie de", "illustration de"),
    "es": ("imagen de", "foto de", "fotografía de"),
    "de": ("bild von", "foto von", "darstellung von"),
    "it": ("immagine di", "foto di"),
    "pt": ("imagem de", "foto de"),
    "nl": ("afbeelding van", "foto van"),
    "ar": ("صورة لـ", "صورة من"),
    "ja": ("の画像", "の写真"),
    "zh": ("的图片", "的照片"),
}


LANG_INSTRUCTIONS: dict[str, str] = {
    "en": "Write the alt text in English.",
    "fr": "Rédige le texte alternatif en français.",
    "es": "Escribe el texto alternativo en español.",
    "de": "Schreibe den Alt-Text auf Deutsch.",
    "it": "Scrivi il testo alternativo in italiano.",
    "pt": "Escreva o texto alternativo em português.",
    "nl": "Schrijf de alternatieve tekst in het Nederlands.",
    "ar": "اكتب النص البديل باللغة العربية.",
    "ja": "代替テキストを日本語で書いてください。",
    "zh": "用中文写替代文本。",
}


def pick_default_model() -> str:
    """Pick the Ollama model tag for the current hardware."""
    if model := os.environ.get("OLLAMA_MODEL"):
        return model
    mlx_capable = platform.system() == "Darwin" and platform.machine() in {"arm64", "aarch64"}
    return f"{DEFAULT_BASE}-mlx" if mlx_capable else DEFAULT_BASE


def detect_lang() -> str:
    """Detect the desired output language as a two-letter code."""
    raw: Optional[str] = (
        os.environ.get("ALT_LANG")
        or os.environ.get("LC_ALL")
        or os.environ.get("LANG")
    )
    if not raw:
        try:
            raw, _ = locale.getlocale()
        except (TypeError, ValueError):
            raw = "en"
    raw = (raw or "en").lower()
    return raw.split("_")[0].split(".")[0][:2]
