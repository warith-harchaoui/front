#!/usr/bin/env python3
"""
install_captions
================

Cross-platform installer for the local caption / transcript generator.

Uses **pywhispercpp** (Python binding for whisper.cpp). Pre-compiled
wheels for macOS / Linux / Windows are published to PyPI, so the install
collapses to a single ``pip install``.

The script:

1. Verifies (or installs) the ``pywhispercpp`` Python package. If the
   import fails, ``pip install pywhispercpp`` is run in the active
   interpreter.
2. Pre-downloads the requested GGML weights into
   ``~/.cache/front-skill/whisper/`` so the first real transcription is
   not gated on a model download. Default model: ``large-v3-turbo``.

Usage
-----
::

    python install_captions.py                          # default: large-v3-turbo
    python install_captions.py --model small            # smaller / faster

Notes
-----
* Python 3.9+. The installer itself is stdlib + pip.
* ``pywhispercpp.utils.download_model`` is the canonical way to pre-fetch
  weights; pointing the generator at a local file with
  ``FRONT_WHISPER_MODEL=<path>`` is also supported.
* Audio extraction (video → WAV) is handled by the generator, not the
  installer; install ``ffmpeg`` or the author's audio-helper /
  video-helper packages separately if needed.

Author
------
`Warith Harchaoui, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys
from pathlib import Path


#: Where the GGML weights are cached. Override the parent dir via
#: ``FRONT_CACHE_DIR``; the trailing ``whisper`` subfolder is fixed so
#: every helper agrees on the lookup path.
WHISPER_DIR: Path = Path(
    os.environ.get("FRONT_CACHE_DIR", Path.home() / ".cache" / "front-skill")
) / "whisper"

#: Aliases that pywhispercpp understands directly via the model registry.
SUPPORTED_MODELS: tuple[str, ...] = (
    "tiny", "tiny.en",
    "base", "base.en",
    "small", "small.en",
    "medium", "medium.en",
    "large-v1", "large-v2", "large-v3", "large-v3-turbo",
)

#: Default when no ``--model`` flag is provided.
DEFAULT_MODEL: str = "large-v3-turbo"


# ── pywhispercpp install ─────────────────────────────────────────────────

def _is_installed(pkg: str) -> bool:
    """
    Return ``True`` when ``pkg`` is importable in the active interpreter.

    Uses :func:`importlib.util.find_spec` so the check has no side effects:
    nothing is actually imported, no exception is swallowed.

    Parameters
    ----------
    pkg : str
        Top-level package name to probe.

    Returns
    -------
    bool
        ``True`` when ``find_spec`` resolves to a real spec.
    """
    return importlib.util.find_spec(pkg) is not None


def ensure_pywhispercpp() -> None:
    """
    Install the ``pywhispercpp`` PyPI package if it is not importable.

    Calls ``pip install pywhispercpp`` in the current interpreter when
    :func:`_is_installed` reports it missing. Wheels exist for the three
    major desktop platforms, so the install almost always avoids a compile.

    Raises
    ------
    SystemExit
        When ``pip`` itself is unavailable, the install command exits
        non-zero, or the post-install check still cannot find the package.
    """
    if _is_installed("pywhispercpp"):
        print("→ pywhispercpp already installed.")
        return

    print("→ Installing pywhispercpp via pip…")
    proc = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pywhispercpp"],
    )
    if proc.returncode != 0:
        sys.exit(
            f"pip install pywhispercpp failed (exit {proc.returncode}).\n"
            "Make sure pip is available in this Python environment and try again."
        )
    # Post-install probe — fail fast if pip reported success but the
    # package is not on the active import path.
    if not _is_installed("pywhispercpp"):
        sys.exit(
            "pywhispercpp installed by pip but cannot be located in the "
            "active interpreter's import path. Check virtualenv / PYTHONPATH."
        )


# ── Model download ───────────────────────────────────────────────────────

def download_model(name: str) -> Path:
    """
    Pre-fetch the requested GGML model file into :data:`WHISPER_DIR`.

    Delegates to ``pywhispercpp.utils.download_model`` which handles the
    Hugging Face mirror, checksum validation, and resume-on-interruption.

    Parameters
    ----------
    name : str
        Model alias from :data:`SUPPORTED_MODELS`.

    Returns
    -------
    Path
        Local path to the downloaded GGML weights.

    Raises
    ------
    SystemExit
        On unknown model or download failure.
    """
    if name not in SUPPORTED_MODELS:
        sys.exit(
            f"Unknown model: {name}. Known: {', '.join(SUPPORTED_MODELS)}."
        )

    WHISPER_DIR.mkdir(parents=True, exist_ok=True)

    # ``download_model`` exists in pywhispercpp >= 1.x. The function takes
    # (model_name, download_dir) and returns the absolute path to the file.
    from pywhispercpp.utils import download_model as _download_model

    print(f"→ Pre-downloading model `{name}` into {WHISPER_DIR}…")
    try:
        path: str = _download_model(name, str(WHISPER_DIR))
    except Exception as e:
        sys.exit(f"Model download failed: {e}")

    file_path = Path(path)
    size_mb: int = file_path.stat().st_size // (1024 * 1024)
    print(f"→ Wrote {file_path} ({size_mb} MB).")
    return file_path


# ── CLI entry point ─────────────────────────────────────────────────────

def main() -> int:
    """Run the pip-install + model-prefetch pipeline."""
    p = argparse.ArgumentParser(
        description="Install pywhispercpp and pre-download a GGML caption model.",
    )
    p.add_argument(
        "--model", default=DEFAULT_MODEL, choices=list(SUPPORTED_MODELS),
        help=f"Model alias to pre-download (default: {DEFAULT_MODEL}).",
    )
    args = p.parse_args()

    ensure_pywhispercpp()
    download_model(args.model)
    print()
    print("→ Ready. Test with:")
    print("    python front/scripts/captions_from_whisper.py path/to/audio-or-video")
    return 0


if __name__ == "__main__":
    sys.exit(main())
