"""
test_cli_help — every front script answers ``-h`` and ``--version`` cleanly.

These are no-Ollama, no-network smoke tests. They verify that the
argparse migration did not break invocation for any shipped script.

Tests are parametrised so a future script just needs to be added to
``SCRIPTS`` to be covered.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent


SCRIPTS = [
    # front-a11y
    REPO_ROOT / "front-a11y"   / "scripts" / "lint_a11y.py",
    REPO_ROOT / "front-a11y"   / "scripts" / "audit_contrast.py",
    REPO_ROOT / "front-a11y"   / "scripts" / "simulate_cvd.py",
    REPO_ROOT / "front-a11y"   / "scripts" / "install_captions.py",
    REPO_ROOT / "front-a11y"   / "scripts" / "captions_from_whisper.py",
    REPO_ROOT / "front-a11y"   / "scripts" / "alt_from_ollama.py",
    # front-publish
    REPO_ROOT / "front-publish" / "scripts" / "favicons.py",
    REPO_ROOT / "front-publish" / "scripts" / "meta_from_ollama.py",
    REPO_ROOT / "front-publish" / "scripts" / "site_indexes.py",
    REPO_ROOT / "front-publish" / "scripts" / "plain_language.py",
    REPO_ROOT / "front-publish" / "scripts" / "lint_markdown.py",
    REPO_ROOT / "front-publish" / "scripts" / "md_to_html.py",
]


def _run(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True, text=True,
    )


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: f"{p.parent.parent.name}/{p.name}")
def test_version_flag(script: Path) -> None:
    """`-V` / `--version` must exit 0 and mention the 0.2.0 release."""
    proc = _run(script, "--version")
    assert proc.returncode == 0, (
        f"{script} exited {proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    assert "0.2.0" in proc.stdout


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: f"{p.parent.parent.name}/{p.name}")
def test_help_flag_announces_prog(script: Path) -> None:
    """`-h` must exit 0 and start with the canonical kebab-cased prog name."""
    proc = _run(script, "-h")
    assert proc.returncode == 0, (
        f"{script} exited {proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    # `front-<skill>-<action>` — what `make_parser(prog=…)` sets.
    assert "front-" in proc.stdout
    assert "[-h]" in proc.stdout or "[--help]" in proc.stdout
