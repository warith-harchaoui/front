#!/usr/bin/env python3
"""
install_alt_ai
==============

Cross-platform installer for the local Ollama-based alt-text generator.

The script:

1. Installs Ollama if it is missing, using the most appropriate package
   manager available on the host:

   * **Homebrew** (``brew install ollama``) — preferred on Darwin and on
     Linux when present.
   * **Official installer** (``curl -fsSL https://ollama.com/install.sh | sh``)
     on Linux when Homebrew is absent.
   * **winget** (``winget install Ollama.Ollama``) on Windows.

2. Starts the Ollama daemon (``ollama serve``) in the background if it is
   not already running.

3. Pulls the vision model used by :mod:`alt_from_ollama`:

   * Default tag: ``gemma4:e2b``.
   * On MLX-capable hardware (Darwin + arm64/aarch64), the ``-mlx``
     variant is selected automatically.
   * Override the tag with ``OLLAMA_MODEL=<tag>`` or change the base
     with ``OLLAMA_MODEL_BASE=<base>`` before running.

Usage
-----
::

    # First-time install (cross-platform)
    python install_alt_ai.py

    # Re-run is idempotent: no-ops when Ollama and the model are present
    python install_alt_ai.py

    # Override to a different on-device vision model
    OLLAMA_MODEL=gemma3n:e2b python install_alt_ai.py

After this finishes:

::

    python scripts/alt_from_ollama.py path/to/image.jpg

Notes
-----
* Python 3.9+, stdlib only (``subprocess``, ``urllib``, ``shutil``).
* No third-party dependencies for the installer itself.
* On Linux the official installer is downloaded and piped to ``sh`` via
  an intermediate string, which avoids the standard ``curl | sh`` security
  caveat while still being one command.

Author
------
`Warith Harchaoui, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.request


# ── Module-level configuration ────────────────────────────────────────────────

#: Base model tag. The ``-mlx`` suffix is appended at runtime on MLX-capable
#: hardware. Override with the ``OLLAMA_MODEL_BASE`` env var.
BASE: str = os.environ.get("OLLAMA_MODEL_BASE", "gemma4:e2b")


# ── Hardware / model picking ────────────────────────────────────────────────

def pick_model() -> str:
    """
    Pick the model tag for the current hardware.

    Resolution order:

    1. ``OLLAMA_MODEL`` env var (explicit override, e.g. for testing).
    2. ``<BASE>-mlx`` on Darwin + arm64/aarch64 (Apple-Silicon-class).
    3. ``<BASE>`` everywhere else.

    Returns
    -------
    str
        Ollama model tag to pull.
    """
    if model := os.environ.get("OLLAMA_MODEL"):
        return model
    mlx_capable: bool = (
        platform.system() == "Darwin"
        and platform.machine() in {"arm64", "aarch64"}
    )
    return f"{BASE}-mlx" if mlx_capable else BASE


# ── Tiny subprocess helpers ────────────────────────────────────────────────

def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    """
    Echo a command and run it via :func:`subprocess.run`.

    Parameters
    ----------
    cmd : list of str
        Argument vector for the child process.
    **kw
        Forwarded to :func:`subprocess.run`.

    Returns
    -------
    subprocess.CompletedProcess
        The completed process. The caller is responsible for checking
        ``returncode`` unless ``check=True`` was passed.
    """
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, **kw)


def has(cmd: str) -> bool:
    """
    Return ``True`` when ``cmd`` resolves on ``PATH``.

    Parameters
    ----------
    cmd : str
        Executable name (no path components).

    Returns
    -------
    bool
        ``True`` if ``shutil.which(cmd)`` finds the binary.
    """
    return shutil.which(cmd) is not None


# ── Installation steps ─────────────────────────────────────────────────────

def install_ollama() -> None:
    """
    Install Ollama if it is missing, picking the right package manager.

    Strategy by platform:

    * **Darwin**: Homebrew if present, otherwise instruct the user.
    * **Linux**: official installer script (``ollama.com/install.sh``).
    * **Windows**: winget if available, otherwise instruct the user.

    Raises
    ------
    SystemExit
        When no installer is available on the host.
    """
    if has("ollama"):
        print("→ Ollama already installed.")
        return

    system: str = platform.system()
    print(f"→ Installing Ollama on {system}…")

    if system == "Darwin":
        if has("brew"):
            run(["brew", "install", "ollama"], check=True)
        else:
            # No silent download attempts — direct the user to install
            # Homebrew or grab the official ``.dmg``.
            sys.exit(
                "Homebrew not found. Install Homebrew (https://brew.sh) then re-run,\n"
                "or download Ollama directly from https://ollama.com/download."
            )
    elif system == "Linux":
        if not has("curl"):
            sys.exit("curl not found. Install curl, then re-run.")
        # Two-step variant of ``curl … | sh``: download the script first into
        # an in-memory string, then feed it to ``sh`` on stdin. That avoids
        # the ``curl | sh`` race window where the bytes piped to ``sh`` are
        # never visible to the user.
        with urllib.request.urlopen("https://ollama.com/install.sh", timeout=30) as resp:
            installer: str = resp.read().decode("utf-8")
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
        sys.exit(
            f"Unsupported OS: {system}. "
            f"Install Ollama manually from https://ollama.com/download."
        )


def daemon_up() -> bool:
    """
    Probe whether the Ollama daemon is running.

    Returns
    -------
    bool
        ``True`` when ``ollama list`` returns successfully within ten seconds.
        Any other outcome (missing binary, timeout, non-zero exit) returns
        ``False``.
    """
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
    """
    Start the Ollama daemon in the background if it is not already running.

    The function polls :func:`daemon_up` for up to ten seconds after starting
    the process; if the daemon never reports ready, the script exits.
    """
    if daemon_up():
        return

    print("→ Starting the Ollama daemon in the background…")
    # ``start_new_session=True`` detaches the daemon from the installer's
    # process group so closing this terminal does not kill the daemon.
    subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    # Poll once per second. Ten seconds is generous on every supported host.
    for _ in range(10):
        time.sleep(1)
        if daemon_up():
            return
    sys.exit("Ollama did not start within 10 seconds.")


def pull_model(tag: str) -> None:
    """
    Pull the requested model if it is not already present locally.

    Parameters
    ----------
    tag : str
        Ollama model tag (e.g. ``gemma4:e2b`` or ``gemma4:e2b-mlx``).

    Raises
    ------
    SystemExit
        When the pull fails. The error message names the override env var
        so the user can retry with a different tag.
    """
    listing: str = subprocess.run(
        ["ollama", "list"], capture_output=True, text=True, timeout=10,
    ).stdout
    # ``ollama list`` prints a header line; skip it and read the first field
    # of every remaining row (the tag).
    installed: list[str] = [
        line.split()[0] for line in listing.splitlines()[1:] if line.strip()
    ]
    if tag in installed:
        print(f"→ {tag} already present.")
        return

    print(f"→ Pulling {tag}…")
    proc = subprocess.run(["ollama", "pull", tag])
    if proc.returncode != 0:
        sys.stderr.write(
            f"\nCould not pull `{tag}`. Check your network connection and the model tag.\n"
            "To try a different on-device vision model, set OLLAMA_MODEL and re-run, e.g.:\n"
            "    OLLAMA_MODEL=gemma3n:e2b python scripts/install_alt_ai.py\n"
            "Browse tags at https://ollama.com/library\n"
        )
        sys.exit(1)


# ── CLI entry point ────────────────────────────────────────────────────────

def main() -> int:
    """
    Run the install / start / pull pipeline end-to-end.

    Returns
    -------
    int
        Process exit code. ``0`` on success; other return paths exit via
        :func:`sys.exit` with a context-specific code.
    """
    model: str = pick_model()
    print(f"→ Platform: {platform.system()} {platform.machine()}")
    print(f"→ Target model: {model}")

    install_ollama()
    ensure_daemon()
    pull_model(model)

    print("\n→ Ready. Test with:")
    print("    python scripts/alt_from_ollama.py /path/to/image.jpg")
    return 0


if __name__ == "__main__":
    sys.exit(main())
