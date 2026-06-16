#!/usr/bin/env python3
"""
alt_from_ollama
===============

Generate W3C/WAI-compliant alternative text for an image, using a local
vision model served by Ollama. Output is cached on disk so the same image
+ parameters never hit the model twice.

The script implements the W3C image decision tree
(https://www.w3.org/WAI/tutorials/images/decision-tree/), which categorizes
images by their *purpose* in the page rather than by their pixel content:

    informative   conveys meaning              describe the meaning concisely
    decorative    no information / ornamental  emit alt="" (no model call)
    functional    inside <a> or <button>       describe the action / destination
    text          mostly readable text         alt = the text verbatim
    complex       chart, diagram, infographic  short alt + long description elsewhere
    group         several images, one meaning  describe the group as a whole

Each purpose maps to a different prompt; pass it with ``--kind``.

Usage
-----
::

    # informative (default)
    python alt_from_ollama.py ./public/hero.jpg

    # functional: describe the destination, not the icon
    python alt_from_ollama.py --kind functional --context "Submit signup" ./icons/check.png

    # text-as-image: extract verbatim text
    python alt_from_ollama.py --kind text ./quote.png

    # complex: short alt; pair with a long description in <figcaption>
    python alt_from_ollama.py --kind complex --context "Weekly users" ./chart.png

    # French output, bypass cache for this run
    python alt_from_ollama.py --lang fr --no-cache ./hero.jpg

Notes
-----
* Requires Python 3.9+, ``requests``. Pillow is opportunistic
  (used to downscale images before sending; if missing, the original is sent).
* Default model: ``gemma4:e2b`` (the ``-mlx`` variant is selected automatically
  on MLX-capable hardware). Override with ``OLLAMA_MODEL=<tag>`` or ``--model``.
* Default Ollama endpoint: ``http://localhost:11434``. Override with ``OLLAMA_URL``.
* On-disk cache lives under ``~/.cache/front-skill/alt/`` by default. Override
  with ``FRONT_CACHE_DIR``; disable globally with ``FRONT_NO_CACHE=1`` or for
  a single run with ``--no-cache``.

Author
------
`Warith Harchaoui, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
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

# ``requests`` is the one hard third-party dependency; declared as a runtime
# requirement in ``front/scripts/requirements.txt``.
import requests

# Vocabulary + language helpers — shared with the other Ollama-backed scripts.
sys.path.insert(0, str(Path(__file__).parent))
from _vocab import resolve_vocab_terms, surrounding_text  # noqa: E402
from _lang import detect_text_language  # noqa: E402

# Pillow is *optional*. If available it is used to downscale the image before
# sending to the model (faster inference, smaller HTTP payload). The script
# stays functional without it; large images simply travel uncompressed.
try:
    from PIL import Image  # type: ignore[import-not-found]
    HAVE_PILLOW: bool = True
except ImportError:
    HAVE_PILLOW = False


# ── Module-level configuration ────────────────────────────────────────────────

#: Ollama daemon endpoint. Override with the ``OLLAMA_URL`` env var.
OLLAMA_URL: str = os.environ.get("OLLAMA_URL", "http://localhost:11434")

#: Base model tag. The "-mlx" variant is appended at runtime on MLX-capable
#: hardware; both flavors are visible to Ollama as separate tags.
DEFAULT_BASE: str = os.environ.get("OLLAMA_MODEL_BASE", "gemma4:e2b")

#: Hard cap on output length. W3C does not mandate a fixed maximum, but ~150
#: characters is the upper bound that stays comfortable for screen-reader users.
MAX_CHARS: int = 150

#: Directory where successful generations are cached. Override with the
#: ``FRONT_CACHE_DIR`` env var (useful in tests, CI, or for shared caches).
CACHE_DIR: Path = Path(
    os.environ.get("FRONT_CACHE_DIR", Path.home() / ".cache" / "front-skill")
) / "alt"

#: When true, the cache is consulted neither for reads nor for writes.
#: Toggled at runtime by ``--no-cache`` or globally by ``FRONT_NO_CACHE``.
NO_CACHE: bool = bool(os.environ.get("FRONT_NO_CACHE"))


# ── Cache helpers ────────────────────────────────────────────────────────────

def _cache_key(image_bytes: bytes, kind: str, lang: str, context: str, model: str) -> str:
    """
    Compute a 32-character cache key from the inputs that affect the output.

    The key incorporates the *post-resize* image bytes, the purpose category,
    the output language, any context hint, and the model tag. A change to
    any of these invalidates the cache entry.

    Parameters
    ----------
    image_bytes : bytes
        Raw bytes of the (possibly downscaled) image actually sent to the model.
    kind : str
        W3C purpose category (``informative``, ``functional``, …).
    lang : str
        Two-letter language code (``en``, ``fr``, …).
    context : str
        Page-context hint passed via ``--context``.
    model : str
        Ollama model tag, e.g. ``gemma4:e2b-mlx``.

    Returns
    -------
    str
        32 hex characters, suitable as a filename stem.
    """
    h = hashlib.sha256()
    h.update(image_bytes)
    # NUL separator keeps the concatenation of textual parameters unambiguous.
    h.update(b"\x00")
    h.update(f"{kind}\x00{lang}\x00{context}\x00{model}".encode("utf-8"))
    return h.hexdigest()[:32]


def _cache_get(key: str) -> Optional[str]:
    """
    Return the cached alt text for ``key``, or ``None`` on a miss.

    Cache reads are silent on any error and behave as a miss; the model call
    will run and (best-effort) refresh the entry.
    """
    if NO_CACHE:
        return None
    path = CACHE_DIR / f"{key}.txt"
    if path.is_file():
        # Strip the trailing newline written by ``_cache_set``.
        return path.read_text(encoding="utf-8").rstrip("\n")
    return None


def _cache_set(key: str, text: str) -> None:
    """
    Store ``text`` in the cache under ``key``. Failures are swallowed.

    The cache is opportunistic — a read-only filesystem or a quota exhaustion
    must not break the user's primary action.
    """
    if NO_CACHE:
        return
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        (CACHE_DIR / f"{key}.txt").write_text(text + "\n", encoding="utf-8")
    except OSError:
        # Intentional silent fail — see docstring.
        pass


# ── Model + language helpers ────────────────────────────────────────────────

def pick_default_model() -> str:
    """
    Pick the model tag for the current hardware.

    On Apple-Silicon-class arm64 macOS, the MLX-optimized variant
    (``<base>-mlx``) is preferred — its first-token latency is materially
    lower. Everywhere else the base tag is used.

    Returns
    -------
    str
        The model tag to pass to Ollama.
    """
    # ``OLLAMA_MODEL`` is the per-call escape hatch and wins outright.
    if model := os.environ.get("OLLAMA_MODEL"):
        return model
    # ``platform.machine()`` returns ``arm64`` on Apple Silicon, ``aarch64`` on
    # some Linux ARM hosts; both run MLX (the former natively, the latter not,
    # but Ollama silently downgrades the request if the tag is unsupported).
    mlx_capable = platform.system() == "Darwin" and platform.machine() in {"arm64", "aarch64"}
    return f"{DEFAULT_BASE}-mlx" if mlx_capable else DEFAULT_BASE


#: Per-language phrases that the model must NOT begin its output with. W3C is
#: explicit that screen readers already announce "image" — the model parroting
#: "Image of …" in any language is noise.
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

#: One-sentence instruction telling the model which language to reply in.
#: The instruction is itself written in the target language to nudge the model
#: into committing to the output language immediately.
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


def detect_lang() -> str:
    """
    Detect the desired output language as a two-letter code.

    Resolution order:

    1. ``ALT_LANG`` env var (explicit override).
    2. ``LC_ALL`` / ``LANG`` env vars (POSIX locale).
    3. ``locale.getlocale()`` (system locale, may be ``(None, None)``).
    4. Fallback to English.

    Returns
    -------
    str
        Lower-case two-letter language code (``en``, ``fr``, …).
    """
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
    # Locale strings look like ``fr_FR.UTF-8`` — strip the encoding and region.
    return raw.split("_")[0].split(".")[0][:2]


# ── Prompt construction ─────────────────────────────────────────────────────

#: Generic rules appended to every prompt except the ``text`` purpose (where
#: the verbatim-extraction goal makes generic rules counter-productive).
BASE_RULES: str = (
    f"Reply with the alt text only — no quotes, no prefix, no trailing punctuation tricks. "
    f"Stay under {MAX_CHARS} characters. "
    f"Match the meaning of the image in its likely page context, not its pixels. "
    f"Do not start with 'image of', 'picture of', 'photo of', 'illustration of', "
    f"or the equivalent in your language. "
    f"Be specific where relevant to meaning (e.g. for a news photo, name visible "
    f"people, setting, action). Don't invent facts you can't see."
)


def long_prompt_for(kind: str, lang: str, context: str = "") -> str:
    """
    Build the prompt for a long-form description of a complex image.

    Long descriptions are intended for ``<figcaption>`` or for an element
    referenced by ``aria-describedby``. They name the chart type, the axes,
    a handful of key values or outliers, and the takeaway — in that order.

    Parameters
    ----------
    kind : str
        W3C purpose category. Long descriptions only make sense for
        ``complex`` (and to a lesser extent ``group``); other kinds fall
        back to a generic structural prompt.
    lang : str
        Two-letter target language code.
    context : str, optional
        Free-form page-context hint, by default ``""``.

    Returns
    -------
    str
        The fully assembled prompt.
    """
    lang_line: str = LANG_INSTRUCTIONS.get(lang, LANG_INSTRUCTIONS["en"])

    if kind == "complex":
        # Structured request that matches what screen-reader users need from
        # charts and diagrams: type → axes → key values → outliers → takeaway.
        body = (
            "Write a LONG description for this complex image (chart, "
            "diagram, or infographic). The description will be placed in "
            "<figcaption> or in an element referenced by aria-describedby — "
            "it is read by a screen-reader user who cannot see the image. "
            "Structure it as Markdown with this order:\n"
            "  1. One sentence: chart type / diagram type.\n"
            "  2. One sentence: axes or dimensions (what is mapped where).\n"
            "  3. A short bullet list of 3 key values or relationships.\n"
            "  4. One sentence: outliers or notable features (if any).\n"
            "  5. One sentence: the single takeaway.\n"
            "Stay under 400 words. Do not invent numbers — if a value is "
            "ambiguous from the image, describe the relative position "
            "(\"highest\", \"middle\", \"lowest\") instead. "
            "Do not start with 'image of', 'photo of', or the equivalent."
        )
    elif kind == "group":
        body = (
            "Write a LONG description for this group of related images. "
            "Cover the relationship between the images, the combined "
            "meaning, and any notable individual elements. Markdown. "
            "Stay under 400 words."
        )
    else:
        body = (
            "Write a long-form description of this image for use in "
            "<figcaption> or via aria-describedby. Cover the meaningful "
            "structure and context. Stay under 400 words."
        )

    ctx: str = f" Page context: {context}." if context else ""
    return f"{lang_line} {body}{ctx}"


def prompt_for(kind: str, lang: str, context: str = "") -> str:
    """
    Build the full prompt sent to the vision model, tuned to the image purpose.

    Parameters
    ----------
    kind : str
        Image purpose per the W3C decision tree.
    lang : str
        Two-letter target language code.
    context : str, optional
        Free-form page-context hint, by default ``""``.

    Returns
    -------
    str
        The fully assembled prompt, ready to send to Ollama.
    """
    # The language line opens every prompt so the model commits early.
    lang_line: str = LANG_INSTRUCTIONS.get(lang, LANG_INSTRUCTIONS["en"])

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
        # Banned-prefix rule does not apply when the goal is verbatim extraction.
        return f"{lang_line} {head}"
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


# ── Image loading + optional downscale ──────────────────────────────────────

def load_image_bytes(src: str) -> bytes:
    """
    Load the bytes of an image from a local path or an HTTP(S) URL.

    Parameters
    ----------
    src : str
        Either a filesystem path or a fully-qualified ``http(s)://`` URL.

    Returns
    -------
    bytes
        Raw bytes of the image, as fetched.

    Raises
    ------
    urllib.error.URLError
        On any network failure during URL fetch.
    OSError
        On any filesystem failure during local read.
    """
    if re.match(r"^https?://", src, re.I):
        # ``urllib`` is preferred over ``requests`` here because it streams from
        # the response object directly and avoids an extra dependency boundary.
        with urllib.request.urlopen(src, timeout=10) as resp:
            return resp.read()
    return Path(src).read_bytes()


def maybe_resize(data: bytes, max_edge: int) -> bytes:
    """
    Downscale ``data`` so the longest edge is ≤ ``max_edge`` pixels.

    The downscale is best-effort: if Pillow is not installed, or if the image
    cannot be decoded, the original bytes are returned unchanged.

    Parameters
    ----------
    data : bytes
        Raw image bytes.
    max_edge : int
        Target maximum dimension in pixels. ``0`` disables resizing.

    Returns
    -------
    bytes
        Possibly-resized image bytes, encoded as JPEG (q=88) if resizing
        actually occurred; otherwise the original bytes.
    """
    if not HAVE_PILLOW or max_edge <= 0:
        return data
    try:
        im = Image.open(io.BytesIO(data))
        # Convert palette / alpha-only modes to RGB so the JPEG re-encode works.
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGB")
        w, h = im.size
        if max(w, h) <= max_edge:
            # Already smaller than the target — no work to do.
            return data
        # Use the float ratio to keep the aspect ratio precise after rounding.
        scale: float = max_edge / float(max(w, h))
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=88, optimize=True)
        return buf.getvalue()
    except Exception:
        # Fail open: a malformed or exotic image type should not break the call.
        return data


# ── Output post-processing ──────────────────────────────────────────────────

def post_process(text: str, lang: str) -> str:
    """
    Clean up a raw model reply for use as an ``alt`` attribute value.

    Three transformations are applied, in order:

    1. Strip a single layer of surrounding quotes (the model sometimes wraps
       the reply in straight or typographic quotes).
    2. Strip a banned prefix (``"image of"`` and its translations) when it
       appears at the start. The matching is case-insensitive and tolerant
       of common punctuation separators (``:``, ``,``, ``—``).
    3. Hard cap at :data:`MAX_CHARS`. **No trailing ellipsis** — per W3C,
       truncating alt text with ``…`` confuses screen readers; cut cleanly
       at a word boundary instead.

    Parameters
    ----------
    text : str
        Raw text returned by the model.
    lang : str
        Two-letter language code used to choose the banned-prefix list.

    Returns
    -------
    str
        Post-processed text, safe to drop straight into an ``alt`` attribute.
    """
    text = text.strip()

    # 1. Strip wrapping quotes (single layer only — chained quotes are rare
    # and stripping them blindly would corrupt verbatim text in "text" mode).
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {'"', "'", "“", "”", "«", "»"}:
        text = text[1:-1].strip()

    # 2. Strip banned prefixes. Try the target language first, fall back to
    # English (the model sometimes lapses into English even when instructed
    # otherwise).
    for prefix in BANNED_PREFIXES.get(lang, ()) + BANNED_PREFIXES["en"]:
        m = re.match(rf"^{re.escape(prefix)}[\s:,.\-—]*", text, flags=re.IGNORECASE)
        if m:
            text = text[m.end():].lstrip()
            break  # Only one prefix could possibly match; stop after the first hit.

    # 3. Hard cap at MAX_CHARS without ellipsis. ``rsplit(" ", 1)[0]`` cuts at
    # the last word boundary inside the window; if there is no space, fall
    # back to the raw truncation (extremely long single word, unlikely).
    if len(text) > MAX_CHARS:
        head = text[:MAX_CHARS].rsplit(" ", 1)[0] or text[:MAX_CHARS]
        text = head.rstrip(",.;:—-")
    return text


# ── Public API ──────────────────────────────────────────────────────────────

def describe_long(
    src: str,
    *,
    kind: str = "complex",
    lang: Optional[str] = None,
    context: str = "",
    resize: int = 1024,
    model: Optional[str] = None,
) -> str:
    """
    Generate a long description for a complex image.

    Parameters
    ----------
    src : str
        Path or URL to the image.
    kind : str, optional
        W3C purpose. Defaults to ``"complex"`` since that is the only kind
        for which a long description is normally meaningful.
    lang : str or None, optional
        BCP-47 base tag. Detected from the environment when ``None``.
    context : str, optional
        Page-context hint (e.g. "Weekly active users for the marketing site").
    resize : int, optional
        Maximum long-edge in pixels for the image sent to the model.
    model : str or None, optional
        Ollama model tag to use.

    Returns
    -------
    str
        Markdown long description, suitable for ``<figcaption>`` or
        ``aria-describedby``. Empty string when the model returns nothing.

    Raises
    ------
    SystemExit
        With code ``2`` when Ollama is unreachable.
    """
    lang = (lang or detect_lang()).lower()[:2]
    model = model or pick_default_model()
    data: bytes = maybe_resize(load_image_bytes(src), resize)

    # The cache key distinguishes long descriptions from short alt by
    # appending ``"long"`` to the parameter mix.
    key = _cache_key(data, f"{kind}:long", lang, context, model)
    cached = _cache_get(key)
    if cached is not None:
        return cached

    image_b64: str = base64.b64encode(data).decode("ascii")
    payload: dict = {
        "model": model,
        "prompt": long_prompt_for(kind, lang, context),
        "images": [image_b64],
        "stream": False,
        # Long descriptions need more tokens than short alt — 400 words
        # comfortably fits in 600 tokens for most languages.
        "options": {"temperature": 0.25, "num_predict": 600},
    }

    try:
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=180)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        sys.stderr.write(
            f"Cannot reach Ollama at {OLLAMA_URL}.\n"
            f"Start the daemon (`ollama serve`) or run:\n"
            f"    python scripts/install_alt_ai.py\n"
        )
        sys.exit(2)
    except requests.exceptions.HTTPError as e:
        sys.stderr.write(f"Ollama responded with HTTP error: {e}\n")
        sys.exit(2)

    body: dict = resp.json()
    text: str = (body.get("response") or "").strip()
    # Long descriptions are NOT post-processed by ``post_process`` — that
    # would strip Markdown bullets and clip mid-list. They are still cached.
    _cache_set(key, text)
    return text


def compose_vocabulary_hint(terms: list[str]) -> str:
    """
    Build the vocabulary suffix appended to the alt prompt.

    Unlike the captions prompt (which tells whisper "these terms may
    appear"), the alt prompt asks the model to *prefer* the supplied
    names **only when they match what is actually visible** — this guards
    against hallucination.

    Parameters
    ----------
    terms : list of str
        Candidate terms drawn from the surrounding document or project.

    Returns
    -------
    str
        A short instruction fragment, or empty string when ``terms`` is empty.
    """
    if not terms:
        return ""
    # Cap at ~60 terms to keep the prompt compact and within Gemma's context.
    kept = terms[:60]
    return (
        " When labeling visible elements, prefer these specific names if "
        "they apply to what you see: " + ", ".join(kept) +
        ". Do NOT include a term unless it actually matches what is in the image."
    )


def describe(
    src: str,
    *,
    kind: str = "informative",
    lang: Optional[str] = None,
    context: str = "",
    resize: int = 1024,
    model: Optional[str] = None,
    vocabulary: Optional[list[str]] = None,
) -> str:
    """
    Generate alt text for an image.

    Parameters
    ----------
    src : str
        Path or URL to the image. Ignored when ``kind == "decorative"``.
    kind : str, optional
        Image purpose per the W3C decision tree — one of ``informative``
        (default), ``decorative``, ``functional``, ``text``, ``complex``,
        ``group``.
    lang : str or None, optional
        BCP-47 base tag (``en``, ``fr``, …). When ``None`` (default), the
        language is detected from the environment via :func:`detect_lang`.
    context : str, optional
        Page-context hint. For ``--kind functional``, this is where the
        caller names the action or destination.
    resize : int, optional
        Maximum long-edge in pixels for the image sent to the model.
        ``0`` disables resizing. Default ``1024``.
    model : str or None, optional
        Ollama model tag to use. ``None`` (default) picks the right tag for
        the current hardware via :func:`pick_default_model`.

    Returns
    -------
    str
        Post-processed alt text, ``≤ MAX_CHARS`` characters. Empty string
        when ``kind == "decorative"``.

    Raises
    ------
    SystemExit
        With code ``2`` when Ollama is unreachable or returns an HTTP error.

    Examples
    --------
    >>> describe("hero.jpg", kind="informative")              # doctest: +SKIP
    'Teacher leading a class'
    >>> describe("divider.svg", kind="decorative")
    ''
    """
    # Decorative images bypass the model entirely: the caller renders
    # ``<img alt="">`` directly. W3C explicitly forbids both omitting the
    # attribute and decorating it with ``role="presentation"``.
    if kind == "decorative":
        return ""

    # Normalize language and pick the model tag once so the cache key is stable.
    lang = (lang or detect_lang()).lower()[:2]
    model = model or pick_default_model()

    # Resize before computing the cache key so size-equivalent images share an
    # entry (two photos that downscale to the same JPEG hit the same key).
    data: bytes = maybe_resize(load_image_bytes(src), resize)

    # Vocabulary suffix on the prompt — and on the cache key so different
    # vocab produces a different cached output.
    vocab_suffix: str = compose_vocabulary_hint(vocabulary or [])

    key = _cache_key(data, kind, lang, context + vocab_suffix, model)
    cached = _cache_get(key)
    if cached is not None:
        # Cache hit — return immediately, no network round-trip.
        return cached

    # Encode the image once. Base64 is what Ollama's REST API expects in the
    # ``images`` array.
    image_b64: str = base64.b64encode(data).decode("ascii")

    payload: dict = {
        "model": model,
        "prompt": prompt_for(kind, lang, context) + vocab_suffix,
        "images": [image_b64],
        "stream": False,
        # ``temperature`` low to make the output reproducible across runs.
        # ``num_predict`` bounds the model output token count; alt text is short
        # so 120 tokens is generous.
        "options": {"temperature": 0.2, "num_predict": 120},
    }

    try:
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        sys.stderr.write(
            f"Cannot reach Ollama at {OLLAMA_URL}.\n"
            f"Start the daemon (`ollama serve`) or run:\n"
            f"    python scripts/install_alt_ai.py\n"
        )
        sys.exit(2)
    except requests.exceptions.HTTPError as e:
        sys.stderr.write(f"Ollama responded with HTTP error: {e}\n")
        sys.exit(2)

    body: dict = resp.json()
    text = post_process(body.get("response", ""), lang)
    _cache_set(key, text)
    return text


# ── CLI ─────────────────────────────────────────────────────────────────────

def _build_argparser() -> argparse.ArgumentParser:
    """
    Construct the CLI ``ArgumentParser``.

    Returns
    -------
    argparse.ArgumentParser
        Parser with all flags registered.
    """
    p = argparse.ArgumentParser(
        description="Generate W3C-compliant alt text for an image via a local Ollama vision model.",
    )
    p.add_argument(
        "src",
        help="Path or URL to the image. Ignored when --kind decorative.",
    )
    p.add_argument(
        "--kind",
        choices=["informative", "decorative", "functional", "text", "complex", "group"],
        default="informative",
        help="Image purpose per W3C decision tree. Default: informative.",
    )
    p.add_argument(
        "--lang", "-l",
        help="BCP-47 base tag (en, fr, es, de, …).",
    )
    p.add_argument(
        "--context", "-c", default="",
        help="Page-context hint. For --kind functional, name the action/destination.",
    )
    p.add_argument(
        "--resize", type=int, default=1024,
        help="Downscale long edge to N px before sending (Pillow). 0 disables. Default: 1024.",
    )
    p.add_argument(
        "--model",
        help="Override the Ollama model tag.",
    )
    p.add_argument(
        "--no-cache", action="store_true",
        help="Bypass the on-disk cache for this run.",
    )
    p.add_argument(
        "--longdesc", action="store_true",
        help=(
            "ALSO generate a long description (for <figcaption> or "
            "aria-describedby). Writes it to <src>.longdesc.md beside the "
            "image. Only meaningful with --kind complex or group."
        ),
    )
    # Vocabulary biasing — same shape as captions_from_whisper.py.
    p.add_argument(
        "--in", dest="in_doc", type=Path, metavar="DOC",
        help=(
            "Document the image is embedded in. The text around every "
            "reference to the image inside DOC is used both as --context "
            "and as a vocabulary source. Highest signal for alt text."
        ),
    )
    p.add_argument(
        "--vocab", type=Path,
        help="Glossary file; one term per line; '#' starts a comment.",
    )
    p.add_argument(
        "--vocab-from", type=Path, dest="vocab_from",
        help="File or directory whose text is mined for proper nouns and identifiers.",
    )
    p.add_argument(
        "--auto-project", action="store_true",
        help=(
            "Walk upward from the source to find the project root, then "
            "collect vocabulary from the whole tree."
        ),
    )
    return p


def main(argv: Optional[list[str]] = None) -> int:
    """
    CLI entry point.

    Parameters
    ----------
    argv : list of str or None, optional
        Argument vector excluding ``argv[0]``. When ``None`` (default),
        ``argparse`` reads from ``sys.argv``.

    Returns
    -------
    int
        Process exit code. ``0`` on success, ``2`` on infrastructure failure
        (Ollama unreachable / HTTP error).
    """
    # ``global`` is unfortunate but keeps the cache-bypass flag colocated with
    # the module-level switch the helpers read.
    global NO_CACHE
    args = _build_argparser().parse_args(argv)
    if args.no_cache:
        NO_CACHE = True

    if args.kind == "decorative":
        # W3C: decorative images get alt="" — the caller renders <img alt=""> only.
        # No model call, no output. Exit code 0 signals success.
        return 0

    # Resolve vocabulary from the supplied sources (--in / --vocab /
    # --vocab-from / --auto-project / sibling auto-detect).
    src_path = Path(args.src)
    vocabulary: list[str] = resolve_vocab_terms(
        src_path,
        in_doc=args.in_doc,
        vocab_file=args.vocab,
        vocab_from=args.vocab_from,
        auto_project=args.auto_project,
    )

    # --in DOC also feeds the explicit context hint with the surrounding
    # text — strongest signal for what the image is doing on the page.
    context: str = args.context
    if args.in_doc is not None:
        ctx_from_doc: str = surrounding_text(args.in_doc, src_path)
        if ctx_from_doc:
            context = (context + "\n" + ctx_from_doc).strip() if context else ctx_from_doc

    # Language: explicit --lang wins. Otherwise detect from any available
    # text (surrounding doc, context hint, vocabulary join) via langdetect,
    # falling back to the env-derived locale.
    lang: Optional[str] = args.lang
    if lang is None:
        detection_text: str = " ".join(
            [context] + (vocabulary or [])
        ).strip()
        if detection_text:
            lang = detect_text_language(detection_text, fallback=detect_lang())

    text = describe(
        args.src,
        kind=args.kind,
        lang=lang,
        context=context,
        resize=args.resize,
        model=args.model,
        vocabulary=vocabulary,
    )

    if not text and args.kind == "complex":
        # Empty output for a complex image is almost always a sign that the
        # caller forgot to supply a context hint. Nudge them.
        sys.stderr.write(
            "Note: returned alt is empty. For complex images, the W3C decision tree "
            "calls for a short alt AND a long description elsewhere (<figcaption> or "
            "aria-describedby). Provide a context hint and retry.\n"
        )

    sys.stdout.write(text + "\n")

    # Long description path — runs after the short alt is written so the
    # caller still gets the short alt on stdout even if the long path fails.
    if args.longdesc:
        if args.kind not in {"complex", "group"}:
            sys.stderr.write(
                "Note: --longdesc is only meaningful with --kind complex or group.\n"
            )
        long_text = describe_long(
            args.src,
            kind=args.kind,
            lang=args.lang,
            context=args.context,
            resize=args.resize,
            model=args.model,
        )
        # Resolve a sibling path: ``<src>.longdesc.md`` for files; for URLs
        # write into the current working directory under a sanitized name.
        src_path = Path(args.src)
        if re.match(r"^https?://", args.src, re.I):
            out_path = Path(re.sub(r"[^A-Za-z0-9._-]+", "_", args.src) + ".longdesc.md")
        else:
            out_path = src_path.with_suffix(src_path.suffix + ".longdesc.md")
        out_path.write_text(long_text + "\n", encoding="utf-8")
        sys.stderr.write(f"Long description written to {out_path}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
