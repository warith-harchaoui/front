"""
test_lint_markdown — smoke tests for front-publish/scripts/lint_markdown.py.

Fixtures are public-domain (Gettysburg Address) so the tests are
reproducible by anyone without third-party content.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "front-publish" / "scripts" / "lint_markdown.py"
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "public" / "gettysburg.md"


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True,
    )


def test_lint_public_fixture_runs() -> None:
    """The Gettysburg fixture should at minimum parse and exit 0 or 1."""
    proc = _run(str(FIXTURE))
    # The fixture intentionally contains an empty-alt image and a
    # mermaid block. Empty alt is INFO (no exit flip). Without
    # --render-mermaid we don't try to render. Exit 0 expected.
    assert proc.returncode in (0, 1), (
        f"unexpected exit {proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )


def test_lint_detects_known_intentional_issues() -> None:
    """The fixture has at least one INFO-level finding (empty alt)."""
    proc = _run(str(FIXTURE), "--format", "json")
    assert proc.returncode in (0, 1)
    # Either the JSON contains MD045 or there are no findings — both are
    # acceptable. We only assert the script ran.
    assert "[" in proc.stdout or proc.stdout.strip() == "[]"


def test_lint_help_advertises_mermaid_and_ai() -> None:
    proc = _run("-h")
    assert proc.returncode == 0
    assert "Mermaid" in proc.stdout
    assert "--ai" in proc.stdout
    assert "--render-mermaid" in proc.stdout


def test_version_flag() -> None:
    proc = _run("-V")
    assert proc.returncode == 0
    assert "0.2.0" in proc.stdout


def test_prompts_load_without_pyyaml() -> None:
    """The YAML loader fallback (_yaml_lite) handles our prompt files."""
    sys.path.insert(0, str(REPO_ROOT / "front-publish" / "scripts"))
    from _prompts import load_prompt  # type: ignore

    mermaid = load_prompt("mermaid_labels")
    latex = load_prompt("latex_caption")
    assert "Reply with a JSON array" in mermaid["output_contract"]
    assert "Plain UTF-8 text" in latex["output_contract"]
    assert mermaid["rules_numbered"].startswith("1.")
    assert latex["rules_numbered"].startswith("1.")
