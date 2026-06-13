#!/usr/bin/env python3
"""
install_captions
================

Cross-platform installer for the local whisper.cpp-based caption / transcript
generator. Companion to :mod:`captions_from_whisper`.

The script:

1. Installs the ``whisper-cli`` binary if it is missing:

   * **Darwin** — Homebrew (``brew install whisper-cpp``).
   * **Linux**  — Homebrew if present, otherwise build from source with
     ``cmake`` + ``make`` (compile is single-threaded → patient but works).
   * **Windows** — winget (``winget install ggerganov.whisper.cpp``) when
     available; manual download URL otherwise.

2. Downloads the GGML weights for the chosen model into
   ``~/.cache/front-skill/whisper/`` so the generator can find them without
   path arithmetic:

   * Default model: ``large-v3-turbo`` — small enough to run on a laptop
     and large enough to handle multi-speaker / noisy audio well.

Usage
-----
::

    python install_captions.py                          # default: large-v3-turbo
    python install_captions.py --model small            # smaller / faster

Notes
-----
* Python 3.9+. The installer itself is stdlib-only.
* The downloaded model is referenced by every invocation of the generator;
  removing the file (or pointing ``FRONT_WHISPER_MODEL=<path>``) forces a
  re-download or a different binary.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path


#: Where the GGML weights are cached. Override the directory via the
#: ``FRONT_CACHE_DIR`` env var.
WHISPER_DIR: Path = Path(
    os.environ.get("FRONT_CACHE_DIR", Path.home() / ".cache" / "front-skill")
) / "whisper"

#: Maps the short CLI alias to the canonical Hugging Face filename.
MODELS: dict[str, str] = {
    "tiny":         "ggml-tiny.bin",
    "base":         "ggml-base.bin",
    "small":        "ggml-small.bin",
    "medium":       "ggml-medium.bin",
    "large-v3":     "ggml-large-v3.bin",
    "large-v3-turbo": "ggml-large-v3-turbo.bin",
}

#: Public mirror that hosts every official whisper.cpp GGML file.
MODEL_BASE_URL: str = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/"


# ── Helpers ──────────────────────────────────────────────────────────────

def has(cmd: str) -> bool:
    """Return ``True`` when ``cmd`` resolves on ``PATH``."""
    return shutil.which(cmd) is not None


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    """Echo + run a command via :func:`subprocess.run`."""
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, **kw)


# ── whisper-cli install ──────────────────────────────────────────────────

def install_whisper_cli() -> None:
    """
    Install the ``whisper-cli`` executable if it is missing.

    Raises
    ------
    SystemExit
        When no installer is available on the host.
    """
    if has("whisper-cli") or has("whisper") or has("main"):
        # Different package managers ship the binary under different names.
        # The generator probes for all three.
        print("→ whisper-cli already installed.")
        return

    system: str = platform.system()
    print(f"→ Installing whisper.cpp on {system}…")

    if system in {"Darwin", "Linux"}:
        if has("brew"):
            run(["brew", "install", "whisper-cpp"], check=True)
            return
        if system == "Linux":
            # Fall back to building from source. Requires git + cmake + make.
            for tool in ("git", "make"):
                if not has(tool):
                    sys.exit(
                        f"{tool} not found. Install build tools and re-run, "
                        f"or install Homebrew (https://brew.sh)."
                    )
            tmp: Path = WHISPER_DIR / "src"
            tmp.parent.mkdir(parents=True, exist_ok=True)
            if not tmp.exists():
                run(["git", "clone", "--depth", "1",
                     "https://github.com/ggerganov/whisper.cpp.git", str(tmp)], check=True)
            run(["make", "-C", str(tmp)], check=True)
            # The build produces ``main``; install it as ``whisper-cli`` in
            # the user's local bin if available, else leave it in src/.
            built = tmp / "main"
            if built.is_file():
                target_dir: Path = Path.home() / ".local" / "bin"
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(built, target_dir / "whisper-cli")
                print(f"→ whisper-cli installed at {target_dir / 'whisper-cli'}")
            return
        sys.exit(
            "Homebrew not found. Install Homebrew (https://brew.sh) then re-run.\n"
            "Or build whisper.cpp manually from https://github.com/ggerganov/whisper.cpp."
        )
    if system == "Windows":
        if has("winget"):
            run(["winget", "install", "ggerganov.whisper.cpp", "-e",
                 "--accept-source-agreements", "--accept-package-agreements"],
                check=True)
            return
        sys.exit(
            "winget not found. Download whisper-cli.exe from "
            "https://github.com/ggerganov/whisper.cpp/releases and put it on PATH."
        )
    sys.exit(f"Unsupported OS: {system}.")


# ── Model download ───────────────────────────────────────────────────────

def download_model(name: str) -> Path:
    """
    Download the requested GGML model into :data:`WHISPER_DIR`.

    Parameters
    ----------
    name : str
        Short alias from :data:`MODELS`.

    Returns
    -------
    Path
        Local path to the downloaded file.

    Raises
    ------
    SystemExit
        On unknown model or download failure.
    """
    if name not in MODELS:
        sys.exit(f"Unknown model: {name}. Known: {', '.join(MODELS)}.")
    filename: str = MODELS[name]
    target: Path = WHISPER_DIR / filename
    if target.is_file():
        print(f"→ {filename} already present ({target.stat().st_size // (1024 * 1024)} MB).")
        return target

    WHISPER_DIR.mkdir(parents=True, exist_ok=True)
    url: str = MODEL_BASE_URL + filename
    print(f"→ Downloading {filename}…")
    print(f"  {url}")
    try:
        # ``urlretrieve`` streams to disk without holding the body in memory.
        urllib.request.urlretrieve(url, target)
    except OSError as e:
        sys.exit(f"Download failed: {e}")
    size_mb: int = target.stat().st_size // (1024 * 1024)
    print(f"→ Wrote {target} ({size_mb} MB).")
    return target


# ── CLI entry point ─────────────────────────────────────────────────────

def main() -> int:
    """Run the install + model-download pipeline."""
    p = argparse.ArgumentParser(
        description="Install whisper-cli and pull a GGML caption model.",
    )
    p.add_argument(
        "--model", default="large-v3-turbo", choices=list(MODELS),
        help="Model to download (default: large-v3-turbo).",
    )
    args = p.parse_args()

    install_whisper_cli()
    download_model(args.model)
    print()
    print("→ Ready. Test with:")
    print("    python front/scripts/captions_from_whisper.py path/to/audio-or-video")
    return 0


if __name__ == "__main__":
    sys.exit(main())
