#!/usr/bin/env python3
"""
validate.py — pre-ship quality gate for the front skill.

Run from anywhere; the script resolves the skill root from its own location.
Exits non-zero on any failure. Prints a one-line summary per check.

Checks performed:
  1. SKILL.md exists and has a valid YAML frontmatter block.
  2. SKILL.md description is between 50 and 1024 characters.
  3. No forbidden framework imports anywhere in the skill source.
  4. No trademarked UI-platform terms in user-facing docs (install-context
     references for the alt-text helper are exempt).
  5. No LLM-marketing phrases (production-grade, non-negotiable, …).
  6. No README.md inside the skill folder (Anthropic spec).
  7. Every reference path declared by ui-guidelines/INDEX.md resolves.

Python 3.9 or newer. No third-party dependencies.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
FAIL = 0


def ok(msg: str) -> None:
    print(f"✓ {msg}")


def bad(msg: str, lines: list[str] | None = None) -> None:
    global FAIL
    print(f"✗ {msg}", file=sys.stderr)
    for ln in (lines or [])[:10]:
        print(f"  → {ln}", file=sys.stderr)
    FAIL += 1


def all_files(*globs: str) -> list[Path]:
    out: list[Path] = []
    for g in globs:
        out.extend(SKILL_ROOT.rglob(g))
    return [p for p in out if "node_modules" not in p.parts]


# ── 1. Frontmatter shape ────────────────────────────────────────────────────

skill_md = SKILL_ROOT / "SKILL.md"
frontmatter_text = ""
if not skill_md.is_file():
    bad(f"SKILL.md missing at {skill_md}")
else:
    body = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", body, re.S)
    if not m:
        bad("SKILL.md does not start with a valid '---\\n…\\n---\\n' frontmatter block")
    else:
        ok("SKILL.md frontmatter is well-formed")
        frontmatter_text = m.group(1)

# ── 2. Description length ───────────────────────────────────────────────────

desc_match = re.search(
    r"^description:\s*(.*?)(?=^[a-z][a-z_]*:\s|\Z)",
    frontmatter_text,
    re.M | re.S,
)
if not desc_match:
    bad("SKILL.md frontmatter missing 'description:' field")
else:
    desc = " ".join(desc_match.group(1).split())
    if len(desc) < 50:
        bad(f"SKILL.md description too short ({len(desc)} chars; need ≥ 50)")
    elif len(desc) > 1024:
        bad(f"SKILL.md description exceeds 1024 chars ({len(desc)})")
    else:
        ok(f"SKILL.md description length OK ({len(desc)} / 1024 chars)")

# ── 3. Forbidden framework imports ──────────────────────────────────────────

framework_pat = re.compile(
    r"""(?x)
    (?: from \s+ ["']
      | require \s* \( \s* ["']
    )
    (?: react | vue | svelte | solid-js | next | nuxt | @angular )
    """,
)
hits: list[str] = []
for f in all_files("*.md", "*.html", "*.mjs", "*.js"):
    for i, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        if framework_pat.search(line):
            hits.append(f"{f.relative_to(SKILL_ROOT)}:{i}:{line.strip()}")
if hits:
    bad("Framework import detected:", hits)
else:
    ok("No framework imports")

# ── 4. Trademarked UI-platform terms in user-facing docs ────────────────────

trademark_pat = re.compile(
    r"\b(Apple|Apple Silicon|iOS|iPadOS|macOS|watchOS|tvOS|visionOS|HIG)\b"
    r"|SF\s*(Pro|Mono|Symbol)\b"
    r"|San\s*Francisco\b",
)

# Install-context exemptions: the alt-text helper documentation and the
# top-level READMEs (which credit third-party design systems as knowledge
# sources) may name them.
def is_user_facing_doc(path: Path, line: str) -> bool:
    rel = path.relative_to(SKILL_ROOT).as_posix()
    if rel == "references/alt-text-ai.md":
        return False
    if rel == "references/ui-guidelines/foundations/images.md" and (
        "install_alt_ai" in line or "alt_from_ollama" in line or "MLX" in line
    ):
        return False
    if rel == "references/material-design.md":
        return False  # Material Design comparison file, deliberately names Material.
    if rel == "SKILL.md" and (
        "alt-text-ai.md" in line or "alt_from_ollama" in line or "install_alt_ai" in line
    ):
        return False
    return True


hits = []
for f in all_files("*.md", "*.html"):
    for i, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        if trademark_pat.search(line) and is_user_facing_doc(f, line):
            hits.append(f"{f.relative_to(SKILL_ROOT)}:{i}:{line.strip()}")
if hits:
    bad("Trademarked UI-platform term in user-facing docs:", hits)
else:
    ok("No trademarked UI-platform terms in user-facing docs")

# ── 5. LLM-marketing phrases ────────────────────────────────────────────────

marketing_words = [
    "production-grade", "non-negotiable", "world-class",
    "cutting-edge", "state-of-the-art", "seamlessly",
    "effortlessly", "gracefully", "leverages", "leverage",
    "empowers", "empower", "robust", "comprehensive", "turnkey",
]
marketing_pat = re.compile(r"\b(" + "|".join(marketing_words) + r")\b", re.I)

hits = []
for f in all_files("*.md"):
    # The anti-patterns file defines these phrases for refusal; exempt it.
    if f.relative_to(SKILL_ROOT).as_posix() == "references/anti-patterns.md":
        continue
    for i, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        if marketing_pat.search(line):
            hits.append(f"{f.relative_to(SKILL_ROOT)}:{i}:{line.strip()}")
if hits:
    bad("LLM-marketing phrase detected:", hits)
else:
    ok("No LLM-marketing phrases")

# ── 6. No README.md inside the skill folder ─────────────────────────────────

if (SKILL_ROOT / "README.md").is_file():
    bad("README.md exists inside the skill folder (Anthropic spec forbids it)")
else:
    ok("No README.md inside the skill folder")

# ── 7. Every INDEX.md path resolves ─────────────────────────────────────────

idx = SKILL_ROOT / "references" / "ui-guidelines" / "INDEX.md"
missing: list[str] = []
if idx.is_file():
    refs = sorted(set(re.findall(r"`([a-z][a-z0-9_/\-]*\.md)`", idx.read_text(encoding="utf-8"))))
    for rel in refs:
        if rel.startswith("references/"):
            target = SKILL_ROOT / rel
        elif "/" in rel:
            target = SKILL_ROOT / "references" / "ui-guidelines" / rel
        else:
            target = SKILL_ROOT / "references" / rel
        if not target.exists():
            missing.append(rel)
    if missing:
        bad("INDEX.md references missing files:", missing)
    else:
        ok("All ui-guidelines/INDEX.md paths exist")

# ── Summary ─────────────────────────────────────────────────────────────────

print()
if FAIL == 0:
    print("PASS — skill is shippable.")
    sys.exit(0)
else:
    print(f"FAIL — {FAIL} check(s) failed.")
    sys.exit(1)
