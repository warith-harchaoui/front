"""Smoke tests for the front-cli driver. No Click → tests skip cleanly."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

click = pytest.importorskip("click")
from click.testing import CliRunner  # noqa: E402

from front_cli.cli import cli  # noqa: E402
from front_cli import __version__  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_root_help_lists_all_groups() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    for group in ("ui", "a11y", "publish"):
        assert group in result.output


def test_root_version_includes_version_string() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_subgroup_help_lists_actions() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["a11y", "--help"])
    assert result.exit_code == 0
    for action in ("lint", "contrast", "cvd", "alt", "captions"):
        assert action in result.output


def test_ui_validate_runs_against_repo() -> None:
    """`front ui validate` should pass on the in-repo front-ui skill."""
    env = os.environ.copy()
    env["FRONT_SKILLS_PATH"] = str(REPO_ROOT)
    result = subprocess.run(
        [sys.executable, "-m", "front_cli", "ui", "validate"],
        capture_output=True, text=True, env=env,
    )
    assert result.returncode == 0, (
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "PASS — skill is shippable." in result.stdout


def test_leaf_help_forwards_to_wrapped_script() -> None:
    """
    Regression test: ``front a11y alt --help`` must show the wrapped
    script's actual options (``--kind``, ``--lang``, ``--longdesc``, …),
    not Click's one-line driver stub.

    The bug — fixed by setting ``add_help_option=False`` on every leaf
    command — was that the driver intercepted ``--help`` at its own
    wrapper level instead of forwarding it through the subprocess. Users
    typing ``front a11y alt --help`` saw nothing useful.
    """
    env = os.environ.copy()
    env["FRONT_SKILLS_PATH"] = str(REPO_ROOT)
    result = subprocess.run(
        [sys.executable, "-m", "front_cli", "a11y", "alt", "--help"],
        capture_output=True, text=True, env=env,
    )
    assert result.returncode == 0, (
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    # Markers that prove the wrapped script's help fired, not Click's stub.
    for marker in ("--kind", "--lang", "--longdesc", "informative"):
        assert marker in result.stdout, (
            f"{marker!r} missing from `front a11y alt --help` output — "
            f"driver may be intercepting --help again.\nstdout:\n{result.stdout}"
        )
