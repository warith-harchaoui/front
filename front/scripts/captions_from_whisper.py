#!/usr/bin/env python3
"""
captions_from_whisper
=====================

Generate captions / transcripts for an audio or video file using the local
``whisper-cli`` binary from whisper.cpp. The companion installer
(``install_captions.py``) puts the binary and the GGML weights in place.

The script accepts any common container (mp4, mov, mp3, wav, m4a, …),
extracts a 16 kHz mono WAV stream (which whisper.cpp expects) using the
project author's `audio-helper`_ / `video-helper`_ when installed, and
falls back to a plain ``ffmpeg`` subprocess otherwise.

Outputs (one of three formats):

* ``vtt``   — WebVTT, drops into a ``<track kind="captions" src="…vtt">``.
* ``srt``   — SubRip subtitles.
* ``text``  — plain transcript (no timecodes), for audio-only transcripts.

Cache shape mirrors :mod:`alt_from_ollama`: SHA-256 of (extracted-audio
bytes + model + lang + format), short hex name, stored under
``~/.cache/front-skill/captions/``.

Usage
-----
::

    # Captions for a video → input.vtt next to the file
    python captions_from_whisper.py video.mp4

    # Plain transcript for an audio-only file
    python captions_from_whisper.py podcast.mp3 --format text

    # Specific language + SRT
    python captions_from_whisper.py interview.wav --lang fr --format srt

    # Override the model (smaller / faster)
    python captions_from_whisper.py call.m4a --model small

Notes
-----
* Python 3.9+. ``audio-helper`` / ``video-helper`` are *optional* — the
  script falls back to ``ffmpeg`` when they are not importable.
* whisper.cpp's ``whisper-cli`` is installed by
  :mod:`install_captions`.

.. _audio-helper: https://github.com/warith-harchaoui/audio-helper
.. _video-helper: https://github.com/warith-harchaoui/video-helper

Author
------
`Warith Harchaoui, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional


# ── Module-level configuration ────────────────────────────────────────────────

#: Cache directory shared with the rest of the skill's helpers.
CACHE_DIR: Path = Path(
    os.environ.get("FRONT_CACHE_DIR", Path.home() / ".cache" / "front-skill")
) / "captions"

#: Where install_captions.py stores GGML weights.
WHISPER_DIR: Path = Path(
    os.environ.get("FRONT_CACHE_DIR", Path.home() / ".cache" / "front-skill")
) / "whisper"

#: Cache toggle, mirroring the other Ollama helpers.
NO_CACHE: bool = bool(os.environ.get("FRONT_NO_CACHE"))

#: Default model alias if the user does not pass ``--model``.
DEFAULT_MODEL: str = "large-v3-turbo"

#: Extensions recognized as audio-only inputs (no video stream).
AUDIO_EXTS: frozenset[str] = frozenset({".mp3", ".m4a", ".wav", ".flac", ".ogg", ".opus"})

#: Extensions recognized as video containers (have an audio track to extract).
VIDEO_EXTS: frozenset[str] = frozenset({".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"})


# ── Binary + model location ─────────────────────────────────────────────────

def find_whisper_cli() -> str:
    """
    Resolve the path to a whisper-cli binary.

    Different package managers ship the executable under different names;
    the function tries the common ones in order.

    Returns
    -------
    str
        Path / name of an executable to invoke via subprocess.

    Raises
    ------
    SystemExit
        When none of the candidate binaries are on PATH.
    """
    for candidate in ("whisper-cli", "whisper", "main"):
        path: Optional[str] = shutil.which(candidate)
        if path is not None:
            return path
    sys.exit(
        "whisper.cpp binary not found on PATH. Run:\n"
        "    python front/scripts/install_captions.py\n"
    )


def find_model(name: str) -> Path:
    """
    Resolve the path to a GGML model file.

    Parameters
    ----------
    name : str
        Either a model alias (``large-v3-turbo``) or an absolute path.

    Returns
    -------
    Path
        File path to the GGML weights.

    Raises
    ------
    SystemExit
        When the model file is missing and no override is supplied.
    """
    # An explicit path wins.
    if env := os.environ.get("FRONT_WHISPER_MODEL"):
        path = Path(env)
        if path.is_file():
            return path

    # Prebuilt mapping in install_captions.
    candidate: Path = WHISPER_DIR / f"ggml-{name}.bin"
    if candidate.is_file():
        return candidate
    sys.exit(
        f"Model file {candidate} not found. Run:\n"
        f"    python front/scripts/install_captions.py --model {name}\n"
    )


# ── Audio extraction (helper libs first, ffmpeg fallback) ───────────────────

def extract_audio(src: Path, dst: Path) -> None:
    """
    Re-encode the audio track of ``src`` to a 16 kHz mono WAV at ``dst``.

    The helper libraries `audio-helper`_ / `video-helper`_ are tried first;
    if either is unavailable, the function falls back to a ``ffmpeg``
    subprocess.

    Parameters
    ----------
    src : Path
        Source audio or video file.
    dst : Path
        Output WAV path. The parent directory is created if missing.

    Raises
    ------
    SystemExit
        On any extraction failure (no helper, no ``ffmpeg``).
    """
    dst.parent.mkdir(parents=True, exist_ok=True)

    # Optimistic import — the helpers are not required.
    try:
        from video_helper import extract_audio as video_extract  # type: ignore
        if src.suffix.lower() in VIDEO_EXTS:
            video_extract(str(src), str(dst), sample_rate=16000, mono=True)
            return
    except ImportError:
        pass
    try:
        from audio_helper import to_wav as audio_to_wav  # type: ignore
        audio_to_wav(str(src), str(dst), sample_rate=16000, mono=True)
        return
    except ImportError:
        pass

    # ffmpeg fallback. Quiet, single-pass, overwrite if present.
    if shutil.which("ffmpeg") is None:
        sys.exit(
            "Neither `audio-helper` / `video-helper` nor `ffmpeg` is available.\n"
            "Install one of:\n"
            "    pip install git+https://github.com/warith-harchaoui/audio-helper\n"
            "    pip install git+https://github.com/warith-harchaoui/video-helper\n"
            "    brew install ffmpeg   (macOS)\n"
            "    apt install ffmpeg    (Debian / Ubuntu)\n"
            "    winget install Gyan.FFmpeg   (Windows)\n"
        )
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(src),
         "-ac", "1", "-ar", "16000", str(dst)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


# ── Cache helpers ───────────────────────────────────────────────────────────

def _cache_key(audio: bytes, model_path: Path, lang: str, fmt: str) -> str:
    """
    Compute a 32-character cache key from the inputs that affect the output.

    Parameters
    ----------
    audio : bytes
        Bytes of the extracted 16 kHz mono WAV.
    model_path : Path
        Path to the GGML weights (the filename is enough).
    lang : str
        Two-letter language code, or empty for autodetect.
    fmt : str
        Output format (``vtt`` / ``srt`` / ``text``).

    Returns
    -------
    str
        32 hex characters.
    """
    h = hashlib.sha256()
    h.update(audio)
    h.update(b"\x00")
    h.update(f"{model_path.name}\x00{lang}\x00{fmt}".encode("utf-8"))
    return h.hexdigest()[:32]


def _cache_get(key: str) -> Optional[str]:
    """Return cached output for ``key``, or ``None`` on a miss."""
    if NO_CACHE:
        return None
    for ext in ("vtt", "srt", "txt"):
        path = CACHE_DIR / f"{key}.{ext}"
        if path.is_file():
            return path.read_text(encoding="utf-8")
    return None


def _cache_set(key: str, text: str, fmt: str) -> None:
    """Store ``text`` in the cache. Failures are swallowed."""
    if NO_CACHE:
        return
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        ext = "txt" if fmt == "text" else fmt
        (CACHE_DIR / f"{key}.{ext}").write_text(text, encoding="utf-8")
    except OSError:
        pass


# ── whisper-cli invocation ─────────────────────────────────────────────────

def run_whisper(
    wav: Path,
    model_path: Path,
    lang: str,
    fmt: str,
    whisper_bin: str,
) -> str:
    """
    Run ``whisper-cli`` against ``wav`` and return the requested output.

    Parameters
    ----------
    wav : Path
        16 kHz mono WAV file produced by :func:`extract_audio`.
    model_path : Path
        Path to the GGML model.
    lang : str
        Two-letter language code; empty string triggers autodetect.
    fmt : str
        Output format: ``vtt`` / ``srt`` / ``text``.
    whisper_bin : str
        Path to the executable.

    Returns
    -------
    str
        File contents of the requested output format.

    Raises
    ------
    SystemExit
        When whisper-cli exits non-zero.
    """
    # whisper-cli writes outputs next to the input WAV. We work in a temp
    # directory so the cache logic can attach our own filename.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_wav: Path = Path(tmp) / "in.wav"
        shutil.copyfile(wav, tmp_wav)
        cmd: list[str] = [
            whisper_bin,
            "-m", str(model_path),
            "-f", str(tmp_wav),
            # Output flags:
            "-otxt" if fmt == "text" else f"-o{fmt}",
            "-of", str(tmp_wav.with_suffix("")),
        ]
        if lang:
            cmd.extend(["-l", lang])
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            sys.exit(
                f"whisper-cli failed (exit {result.returncode}):\n"
                f"{result.stderr}"
            )
        ext: str = "txt" if fmt == "text" else fmt
        out_path: Path = tmp_wav.with_suffix(f".{ext}")
        return out_path.read_text(encoding="utf-8")


# ── Public API ────────────────────────────────────────────────────────────

def transcribe(
    src: Path,
    *,
    model: str = DEFAULT_MODEL,
    lang: str = "",
    fmt: str = "vtt",
) -> str:
    """
    Transcribe ``src`` and return the output as a string.

    Parameters
    ----------
    src : Path
        Audio or video file path.
    model : str, optional
        Model alias from :mod:`install_captions`. Default ``large-v3-turbo``.
    lang : str, optional
        Two-letter language code. Empty (default) lets whisper autodetect.
    fmt : str, optional
        Output format: ``vtt`` (default), ``srt``, or ``text``.

    Returns
    -------
    str
        File contents in the requested format.
    """
    whisper_bin = find_whisper_cli()
    model_path = find_model(model)

    with tempfile.TemporaryDirectory() as tmp:
        wav_path = Path(tmp) / "input.wav"
        extract_audio(src, wav_path)
        audio_bytes: bytes = wav_path.read_bytes()

        key = _cache_key(audio_bytes, model_path, lang, fmt)
        cached = _cache_get(key)
        if cached is not None:
            return cached

        output = run_whisper(wav_path, model_path, lang, fmt, whisper_bin)
        _cache_set(key, output, fmt)
        return output


# ── CLI entry point ───────────────────────────────────────────────────────

def main() -> int:
    """CLI entry point. Writes the output to a sibling file by default."""
    p = argparse.ArgumentParser(
        description="Generate captions or transcripts via whisper.cpp.",
    )
    p.add_argument("source", type=Path, help="Audio or video file.")
    p.add_argument(
        "--format", choices=["vtt", "srt", "text"], default="vtt",
        help="Output format (default: vtt).",
    )
    p.add_argument(
        "--lang", default="",
        help="Two-letter language code. Empty lets whisper.cpp autodetect.",
    )
    p.add_argument(
        "--model", default=DEFAULT_MODEL,
        help=f"Model alias (default: {DEFAULT_MODEL}).",
    )
    p.add_argument(
        "--out", type=Path,
        help="Output path. Default: sibling of the source with the format extension.",
    )
    p.add_argument(
        "--no-cache", action="store_true",
        help="Bypass the on-disk cache for this run.",
    )
    args = p.parse_args()
    if args.no_cache:
        global NO_CACHE
        NO_CACHE = True

    if not args.source.is_file():
        sys.stderr.write(f"No such file: {args.source}\n")
        return 1

    text = transcribe(
        args.source,
        model=args.model,
        lang=args.lang,
        fmt=args.format,
    )

    # Resolve a sibling output path.
    ext: str = "txt" if args.format == "text" else args.format
    out_path: Path = args.out or args.source.with_suffix(f".{ext}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    print(f"→ Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
