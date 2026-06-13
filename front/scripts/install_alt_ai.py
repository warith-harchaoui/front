#!/usr/bin/env python3
"""
install_alt_ai.py — cross-platform installer for the local Ollama-based
alt-text generator.

Detects the OS and tries the appropriate package manager:

  Darwin   → Homebrew (`brew install ollama`)
  Linux    → official installer (`curl -fsSL https://ollama.com/install.sh | sh`)
  Windows  → winget (`winget install Ollama.Ollama`)

Then starts the Ollama daemon if not already running, and pulls the
right model tag:

  Default:                 gemma4:e2b
  MLX-capable hardware:    gemma4:e2b-mlx     (selected automatically)
  Override:                OLLAMA_MODEL=<tag>

After this finishes:

  python front/scripts/alt_from_ollama.py path/to/image.jpg

Python 3.9 or newer. No third-party dependencies for this installer.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.request


BASE = os.environ.get("OLLAMA_MODEL_BASE", "gemma4:e2b")


def pick_model() -> str:
    if model := os.environ.get("OLLAMA_MODEL"):
        return model
    mlx_capable = platform.system() == "Darwin" and platform.machine() in {"arm64", "aarch64"}
    return f"{BASE}-mlx" if mlx_capable else BASE


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, **kw)


def has(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def install_ollama() -> None:
    if has("ollama"):
        print("→ Ollama already installed.")
        return

    system = platform.system()
    print(f"→ Installing Ollama on {system}…")

    if system == "Darwin":
        if has("brew"):
            run(["brew", "install", "ollama"], check=True)
        else:
            sys.exit(
                "Homebrew not found. Install Homebrew (https://brew.sh) then re-run,\n"
                "or download Ollama directly from https://ollama.com/download."
            )
    elif system == "Linux":
        if not has("curl"):
            sys.exit("curl not found. Install curl, then re-run.")
        # Two-step: download script, then run it explicitly (safer than `curl | sh`).
        with urllib.request.urlopen("https://ollama.com/install.sh", timeout=30) as resp:
            installer = resp.read().decode("utf-8")
        proc = subprocess.run(["sh"], input=installer, text=True)
        if proc.returncode != 0:
            sys.exit(f"Linux installer failed with exit code {proc.returncode}.")
    elif system == "Windows":
        if has("winget"):
            run(
                ["winget", "install", "--id", "Ollama.Ollama", "-e",
                 "--accept-source-agreements", "--accept-package-agreements"],
                check=True,
            )
        else:
            sys.exit(
                "winget not found. Install the App Installer from the Microsoft Store,\n"
                "or download Ollama from https://ollama.com/download."
            )
    else:
        sys.exit(f"Unsupported OS: {system}. Install Ollama manually from https://ollama.com/download.")


def daemon_up() -> bool:
    try:
        proc = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return proc.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def ensure_daemon() -> None:
    if daemon_up():
        return
    print("→ Starting the Ollama daemon in the background…")
    # On every platform, `ollama serve` starts the local API server.
    subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    for _ in range(10):
        time.sleep(1)
        if daemon_up():
            return
    sys.exit("Ollama did not start within 10 seconds.")


def pull_model(tag: str) -> None:
    listing = subprocess.run(
        ["ollama", "list"], capture_output=True, text=True, timeout=10,
    ).stdout
    installed = [line.split()[0] for line in listing.splitlines()[1:] if line.strip()]
    if tag in installed:
        print(f"→ {tag} already present.")
        return

    print(f"→ Pulling {tag}…")
    proc = subprocess.run(["ollama", "pull", tag])
    if proc.returncode != 0:
        sys.stderr.write(
            f"\nCould not pull `{tag}`. Check your network connection and the model tag.\n"
            "To try a different on-device vision model, set OLLAMA_MODEL and re-run, e.g.:\n"
            "    OLLAMA_MODEL=gemma3n:e2b python front/scripts/install_alt_ai.py\n"
            "Browse tags at https://ollama.com/library\n"
        )
        sys.exit(1)


def main() -> int:
    model = pick_model()
    print(f"→ Platform: {platform.system()} {platform.machine()}")
    print(f"→ Target model: {model}")
    install_ollama()
    ensure_daemon()
    pull_model(model)
    print("\n→ Ready. Test with:")
    print(f"    python front/scripts/alt_from_ollama.py /path/to/image.jpg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
