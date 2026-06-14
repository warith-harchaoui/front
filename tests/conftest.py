"""
conftest.py — shared pytest configuration for the front-skill test suite.

Adds ``front/scripts/`` to ``sys.path`` so test modules can ``import
alt_from_ollama`` etc. directly, mirroring how the scripts use each
other at runtime.

Author
------
`Warith Harchaoui, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "front" / "scripts"

# Inject the scripts directory at the front of sys.path so its modules
# resolve before any like-named package elsewhere in the environment.
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture(autouse=True)
def isolate_cache(tmp_path, monkeypatch):
    """
    Redirect the skill's on-disk cache to a per-test temp directory.

    Every helper resolves its cache path from ``FRONT_CACHE_DIR``. Setting
    this env var per test prevents test runs from polluting (or being
    polluted by) the developer's real cache at ``~/.cache/front-skill/``.
    """
    monkeypatch.setenv("FRONT_CACHE_DIR", str(tmp_path / "front-skill"))
    # The cache toggle survives across tests if a module reads it at
    # import time; make sure each test sees the same default.
    monkeypatch.delenv("FRONT_NO_CACHE", raising=False)


@pytest.fixture
def repo_root() -> Path:
    """Return the repository root path."""
    return REPO_ROOT
