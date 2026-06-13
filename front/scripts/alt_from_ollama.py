#!/usr/bin/env python3
"""
alt_from_ollama.py — generate accessible alt text per W3C / WAI guidance.

Source authority: https://www.w3.org/WAI/tutorials/images/decision-tree/

W3C categorizes images by *purpose* in the page, not by pixel content:

  informative   conveys meaning              → describe the meaning concisely
  decorative    no information / ornamental  → emit alt=""  (no model call)
  functional    inside <a> or <button>       → describe the action/destination
  text          mostly readable text         → alt = the text verbatim
  complex       chart, diagram, infographic  → short alt + long description elsewhere
                                                (via aria-describedby or <figcaption>)
  group         several images, one meaning  → describe as a whole

Pass the purpose with --kind; the prompt is tuned per category.

Multilingual: --lang <bcp-47> or ALT_LANG / LANG env. Default: detect from system.

Requires Python 3.9+ and `requests`. Pillow is used opportunistically if
installed (to downscale large images before sending to Ollama).
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import locale
import os
import platform
import re
import sys
import urllib.request
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    sys.stderr.write(
        "This script needs `requests`. Install with:\n"
        "    pip install -r front/scripts/requirements.txt\n"
    )
    sys.exit(2)

try:
    from PIL import Image  # type: ignore
    HAVE_PILLOW = True
except ImportError:
    HAVE_PILLOW = False


# ── Configuration ─────────────────────────────────────────────────────────────

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
DEFAULT_BASE = os.environ.get("OLLAMA_MODEL_BASE", "gemma4:e2b")
MAX_CHARS = 150  # W3C says no fixed limit; ~150 chars stays comfortable for screen readers.

CACHE_DIR = Path(os.environ.get("FRONT_CACHE_DIR", Path.home() / ".cache" / "front-skill")) / "alt"
NO_CACHE = bool(os.environ.get("FRONT_NO_CACHE"))


def _cache_key(image_bytes: bytes, kind: str, lang: str, context: str, model: str) -> str:
    h = hashlib.sha256()
    h.update(image_bytes)
    h.update(b"\x00")
    h.update(f"{kind}\x00{lang}\x00{context}\x00{model}".encode("utf-8"))
    return h.hexdigest()[:32]


def _cache_get(key: str) -> Optional[str]:
    if NO_CACHE:
        return None
    path = CACHE_DIR / f"{key}.txt"
    if path.is_file():
        return path.read_text(encoding="utf-8").rstrip("\n")
    return None


def _cache_set(key: str, text: str) -> None:
    if NO_CACHE:
        return
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        (CACHE_DIR / f"{key}.txt").write_text(text + "\n", encoding="utf-8")
    except OSError:
        pass  # Fail open: caching is opportunistic, never fatal.


def pick_default_model() -> str:
    """Use the -mlx variant on MLX-capable hardware automatically."""
    if model := os.environ.get("OLLAMA_MODEL"):
        return model
    mlx_capable = platform.system() == "Darwin" and platform.machine() in {"arm64", "aarch64"}
    return f"{DEFAULT_BASE}-mlx" if mlx_capable else DEFAULT_BASE


# ── Per-language banned prefixes (W3C: never say "image of …") ───────────────

BANNED_PREFIXES = {
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


LANG_INSTRUCTIONS = {
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


def detect_lang() -> str:
    raw = os.environ.get("ALT_LANG") or os.environ.get("LC_ALL") or os.environ.get("LANG")
    if not raw:
        try:
            raw, _ = locale.getlocale()
        except Exception:
            raw = "en"
    raw = (raw or "en").lower()
    return raw.split("_")[0].split(".")[0][:2]


# ── Prompts, one per W3C category ────────────────────────────────────────────

BASE_RULES = (
    f"Reply with the alt text only — no quotes, no prefix, no trailing punctuation tricks. "
    f"Stay under {MAX_CHARS} characters. "
    f"Match the meaning of the image in its likely page context, not its pixels. "
    f"Do not start with 'image of', 'picture of', 'photo of', 'illustration of', "
    f"or the equivalent in your language. "
    f"Be specific where relevant to meaning (e.g. for a news photo, name visible people, "
    f"setting, action). Don't invent facts you can't see."
)


def prompt_for(kind: str, lang: str, context: str = "") -> str:
    lang_line = LANG_INSTRUCTIONS.get(lang, LANG_INSTRUCTIONS["en"])

    if kind == "informative":
        head = "Write alt text for this informative image."
    elif kind == "functional":
        head = (
            "This image is inside a link or button. "
            "Describe the action or destination the control performs, NOT the image's appearance. "
            "Example: a magnifying-glass icon inside a search button → 'Search'."
        )
    elif kind == "text":
        head = (
            "This image is mostly text. "
            "Return the readable text verbatim, exactly as it appears, with no description added."
        )
        return f"{lang_line} {head}"  # banned-prefix rule doesn't apply to text-as-text.
    elif kind == "complex":
        head = (
            "This is a complex image (chart, diagram, infographic). "
            "Write a SHORT alt that names the chart type and the single takeaway. "
            "A separate long description will live in <figcaption> or aria-describedby — "
            "do NOT try to fit everything into the alt."
        )
    elif kind == "group":
        head = "Describe the group of images as a whole, conveying their combined meaning."
    else:
        head = "Write alt text for this image."

    ctx = f" Page context: {context}." if context else ""
    return f"{lang_line} {head}{ctx} {BASE_RULES}"


# ── Image loading + optional downscale (Pillow if available) ─────────────────

def load_image_bytes(src: str) -> bytes:
    if re.match(r"^https?://", src, re.I):
        with urllib.request.urlopen(src, timeout=10) as resp:
            return resp.read()
    return Path(src).read_bytes()


def maybe_resize(data: bytes, max_edge: int) -> bytes:
    """Downscale to max_edge px on the long side if Pillow is available."""
    if not HAVE_PILLOW or max_edge <= 0:
        return data
    try:
        im = Image.open(io.BytesIO(data))
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGB")
        w, h = im.size
        if max(w, h) <= max_edge:
            return data
        scale = max_edge / float(max(w, h))
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=88, optimize=True)
        return buf.getvalue()
    except Exception:
        return data  # Fail open: if we can't resize, send the original.


# ── Output post-processing (W3C: no ellipsis-truncation) ─────────────────────

def post_process(text: str, lang: str) -> str:
    text = text.strip()

    # Strip a single layer of wrapping quotes.
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {'"', "'", "“", "”", "«", "»"}:
        text = text[1:-1].strip()

    # Strip banned prefixes if the model ignored the instruction.
    for prefix in BANNED_PREFIXES.get(lang, ()) + BANNED_PREFIXES["en"]:
        # Case-insensitive removal at the start, with optional ":" or "—" separator.
        m = re.match(rf"^{re.escape(prefix)}[\s:,.\-—]*", text, flags=re.IGNORECASE)
        if m:
            text = text[m.end():].lstrip()
            break

    # W3C: don't truncate with ellipsis. Hard cap at a word boundary, no "…".
    if len(text) > MAX_CHARS:
        head = text[:MAX_CHARS].rsplit(" ", 1)[0] or text[:MAX_CHARS]
        text = head.rstrip(",.;:—-")
    return text


# ── Public API ───────────────────────────────────────────────────────────────

def describe(
    src: str,
    *,
    kind: str = "informative",
    lang: Optional[str] = None,
    context: str = "",
    resize: int = 1024,
    model: Optional[str] = None,
) -> str:
    """Return alt text for `src` (path or URL). Empty string if kind=='decorative'."""
    if kind == "decorative":
        return ""

    lang = (lang or detect_lang()).lower()[:2]
    model = model or pick_default_model()

    data = maybe_resize(load_image_bytes(src), resize)

    key = _cache_key(data, kind, lang, context, model)
    cached = _cache_get(key)
    if cached is not None:
        return cached

    image_b64 = base64.b64encode(data).decode("ascii")

    payload = {
        "model": model,
        "prompt": prompt_for(kind, lang, context),
        "images": [image_b64],
        "stream": False,
        "options": {"temperature": 0.2, "num_predict": 120},
    }

    try:
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        sys.stderr.write(
            f"Cannot reach Ollama at {OLLAMA_URL}.\n"
            f"Start the daemon (`ollama serve`) or run:\n"
            f"    python front/scripts/install_alt_ai.py\n"
        )
        sys.exit(2)
    except requests.exceptions.HTTPError as e:
        sys.stderr.write(f"Ollama responded with HTTP error: {e}\n")
        sys.exit(2)

    body = resp.json()
    text = post_process(body.get("response", ""), lang)
    _cache_set(key, text)
    return text


# ── CLI ──────────────────────────────────────────────────────────────────────

def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Generate W3C-compliant alt text for an image via a local Ollama vision model.",
    )
    p.add_argument("src", help="Path or URL to the image. Ignored when --kind decorative.")
    p.add_argument(
        "--kind",
        choices=["informative", "decorative", "functional", "text", "complex", "group"],
        default="informative",
        help="Image purpose per W3C decision tree. Default: informative.",
    )
    p.add_argument("--lang", "-l", help="BCP-47 base tag (en, fr, es, de, …).")
    p.add_argument(
        "--context", "-c", default="",
        help="Page-context hint. For --kind functional, name the action/destination.",
    )
    p.add_argument(
        "--resize", type=int, default=1024,
        help="Downscale long edge to N px before sending (Pillow). 0 disables. Default: 1024.",
    )
    p.add_argument("--model", help="Override the Ollama model tag.")
    p.add_argument("--no-cache", action="store_true", help="Bypass the on-disk cache for this run.")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    global NO_CACHE
    args = _build_argparser().parse_args(argv)
    if args.no_cache:
        NO_CACHE = True
    if args.kind == "decorative":
        # W3C: decorative images get alt="" — caller renders <img alt=""> only.
        return 0
    text = describe(
        args.src,
        kind=args.kind,
        lang=args.lang,
        context=args.context,
        resize=args.resize,
        model=args.model,
    )
    if not text and args.kind == "complex":
        sys.stderr.write(
            "Note: returned alt is empty. For complex images, the W3C decision tree "
            "calls for a short alt AND a long description elsewhere (<figcaption> or "
            "aria-describedby). Provide a context hint and retry.\n"
        )
    sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
