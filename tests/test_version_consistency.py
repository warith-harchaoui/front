"""
test_version_consistency — the release version is single-valued across the repo.

The version is hand-maintained in three kinds of place:

* the ``metadata.version`` field of every ``front-*/SKILL.md`` (9 skills),
* the ``SKILL_VERSION`` literal in each skill's ``scripts/_argparse.py`` and
  ``scripts/_click.py`` copies,
* ``front-cli/pyproject.toml``'s ``project.version``.

A release bumps all of them. With that many hand-edited sources, a missed one is
the obvious failure mode — this test makes any drift a red build, and doubles as
a check that the CHANGELOG has a matching top section.

Author
------
Project maintainers.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

_SKILL_VERSION_RE = re.compile(r'^\s*SKILL_VERSION\s*=\s*["\']([\d.]+)["\']', re.MULTILINE)
_METADATA_VERSION_RE = re.compile(r'^\s*version:\s*([\d.]+)\s*$', re.MULTILINE)
_DUNDER_VERSION_RE = re.compile(r'^\s*__version__\s*=\s*["\']([\d.]+)["\']', re.MULTILINE)


def _pyproject_version() -> tuple[str, str]:
    path = REPO_ROOT / "front-cli" / "pyproject.toml"
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return str(path.relative_to(REPO_ROOT)), data["project"]["version"]


def _collect() -> dict[str, str]:
    """Map every version source (relative path) to the version string it declares."""
    sources: dict[str, str] = {}

    for skill_md in sorted(REPO_ROOT.glob("front-*/SKILL.md")):
        m = _METADATA_VERSION_RE.search(skill_md.read_text(encoding="utf-8"))
        assert m, f"{skill_md.relative_to(REPO_ROOT)} has no metadata.version"
        sources[str(skill_md.relative_to(REPO_ROOT))] = m.group(1)

    for helper in sorted(REPO_ROOT.glob("front-*/scripts/_argparse.py")) + \
            sorted(REPO_ROOT.glob("front-*/scripts/_click.py")):
        m = _SKILL_VERSION_RE.search(helper.read_text(encoding="utf-8"))
        if m:  # not every helper defines it; check the ones that do
            sources[str(helper.relative_to(REPO_ROOT))] = m.group(1)

    rel, version = _pyproject_version()
    sources[rel] = version

    # The installed package's ``__version__`` — what ``front --version`` prints.
    init_py = REPO_ROOT / "front-cli" / "src" / "front_cli" / "__init__.py"
    m = _DUNDER_VERSION_RE.search(init_py.read_text(encoding="utf-8"))
    assert m, f"{init_py.relative_to(REPO_ROOT)} has no __version__"
    sources[str(init_py.relative_to(REPO_ROOT))] = m.group(1)

    return sources


def test_all_version_sources_agree() -> None:
    """Every SKILL.md, SKILL_VERSION literal, and pyproject version must match."""
    sources = _collect()
    distinct = set(sources.values())
    assert len(distinct) == 1, (
        "version drift across the repo — every source must declare the same version.\n"
        + "\n".join(f"  {v}  <- {p}" for p, v in sorted(sources.items()))
    )


def test_changelog_has_matching_top_section() -> None:
    """The CHANGELOG's most recent ``## [x.y.z]`` section must match the version."""
    (version,) = set(_collect().values())
    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    m = re.search(r"^##\s*\[([\d.]+)\]", changelog, re.MULTILINE)
    assert m, "CHANGELOG.md has no '## [x.y.z]' release section"
    assert m.group(1) == version, (
        f"CHANGELOG top section is [{m.group(1)}] but the repo version is {version}. "
        "Add the release section before tagging."
    )
