"""
cli — the `front` Click driver.

Maps `front <skill> <action> [args ...]` to the right script in the
matching skill folder. Shells out via subprocess; never imports the
target script. This keeps the stdlib-only scripts (validate, lint,
contrast, cvd, site-indexes) zero-dep when invoked directly.

Author
------
`Warith Harchaoui, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional

import click

from front_cli import __version__


# Per-skill script directory layout. Each value is the relative path inside
# a skill folder where the script lives.
SCRIPTS_SUBDIR = "scripts"

# Search order for finding a skill folder by name. Each element is a base
# directory that contains `front-<name>/` folders.
def _candidate_bases() -> list[Path]:
    bases: list[Path] = []
    env = os.environ.get("FRONT_SKILLS_PATH", "")
    for chunk in env.split(":"):
        chunk = chunk.strip()
        if chunk:
            bases.append(Path(chunk).expanduser())
    bases.append(Path.cwd())
    bases.append(Path.home() / ".claude" / "skills")
    bases.append(Path.home() / ".opencode" / "skills")
    return bases


def _find_skill(skill_name: str) -> Optional[Path]:
    """Return the absolute path to the skill folder, or None if missing."""
    for base in _candidate_bases():
        candidate = base / skill_name
        if (candidate / SCRIPTS_SUBDIR).is_dir():
            return candidate
        # Fallback: assume `base` *is* the repo root and `skill_name` lives
        # directly inside it (the in-repo layout).
        candidate = base / skill_name
        if (candidate / "SKILL.md").is_file() and (candidate / SCRIPTS_SUBDIR).is_dir():
            return candidate
    return None


def _run_script(skill: str, script: str, extra: tuple[str, ...]) -> int:
    """Execute `python <skill>/scripts/<script>` with the extra args."""
    skill_root = _find_skill(skill)
    if skill_root is None:
        bases = "\n  ".join(str(b) for b in _candidate_bases())
        click.echo(
            f"front: skill {skill!r} not found.\n"
            f"Searched (in order):\n  {bases}\n"
            f"Set $FRONT_SKILLS_PATH or install the skill folder under one of these.",
            err=True,
        )
        return 2
    target = skill_root / SCRIPTS_SUBDIR / script
    if not target.is_file():
        click.echo(f"front: {script} not found inside {skill_root}.", err=True)
        return 2
    completed = subprocess.run([sys.executable, str(target), *extra])
    return completed.returncode


# ── Root group ──────────────────────────────────────────────────────────────

CONTEXT_SETTINGS = {
    # Forward unknown options to the wrapped script.
    "allow_extra_args": True,
    "ignore_unknown_options": True,
    "help_option_names": ["-h", "--help"],
}


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, "-V", "--version", prog_name="front")
def cli() -> None:
    """
    front — unified driver for the four front skills.

    Each sub-command shells out to the matching script in the matching
    skill folder. Skills are discovered via $FRONT_SKILLS_PATH, the current
    working directory, ~/.claude/skills/ or ~/.opencode/skills/.
    """


# ── ui ──────────────────────────────────────────────────────────────────────

@cli.group(help="UI generation skill (front-ui).")
def ui() -> None:
    """front-ui — UI generation and pre-ship validation."""


@ui.command(name="validate", context_settings=CONTEXT_SETTINGS,
            help="Run the front-ui pre-ship quality gate.")
@click.pass_context
def ui_validate(ctx: click.Context) -> None:
    sys.exit(_run_script("front-ui", "validate.py", tuple(ctx.args)))


# ── a11y ────────────────────────────────────────────────────────────────────

@cli.group(help="Accessibility skill (front-a11y).")
def a11y() -> None:
    """front-a11y — pre-commit a11y gates and content tooling."""


@a11y.command(name="lint", context_settings=CONTEXT_SETTINGS,
              help="Static a11y lint over HTML files (14 rules).")
@click.pass_context
def a11y_lint(ctx: click.Context) -> None:
    sys.exit(_run_script("front-a11y", "lint_a11y.py", tuple(ctx.args)))


@a11y.command(name="contrast", context_settings=CONTEXT_SETTINGS,
              help="WCAG contrast audit + OKLCH-neighbour fix hint.")
@click.pass_context
def a11y_contrast(ctx: click.Context) -> None:
    sys.exit(_run_script("front-a11y", "audit_contrast.py", tuple(ctx.args)))


@a11y.command(name="cvd", context_settings=CONTEXT_SETTINGS,
              help="Color-vision-deficiency (protanopia / deuteranopia / tritanopia) rendering.")
@click.pass_context
def a11y_cvd(ctx: click.Context) -> None:
    sys.exit(_run_script("front-a11y", "simulate_cvd.py", tuple(ctx.args)))


@a11y.command(name="alt", context_settings=CONTEXT_SETTINGS,
              help="W3C-compliant alt text via a local Ollama vision model.")
@click.pass_context
def a11y_alt(ctx: click.Context) -> None:
    sys.exit(_run_script("front-a11y", "alt_from_ollama.py", tuple(ctx.args)))


@a11y.command(name="captions", context_settings=CONTEXT_SETTINGS,
              help="WebVTT / SRT / plain-text captions via local whisper.cpp.")
@click.pass_context
def a11y_captions(ctx: click.Context) -> None:
    sys.exit(_run_script("front-a11y", "captions_from_whisper.py", tuple(ctx.args)))


@a11y.command(name="install-alt-ai", context_settings=CONTEXT_SETTINGS,
              help="Install Ollama and pull the vision model used by `front a11y alt`.")
@click.pass_context
def a11y_install_alt_ai(ctx: click.Context) -> None:
    sys.exit(_run_script("front-a11y", "install_alt_ai.py", tuple(ctx.args)))


@a11y.command(name="install-captions", context_settings=CONTEXT_SETTINGS,
              help="Install pywhispercpp and download the model used by `front a11y captions`.")
@click.pass_context
def a11y_install_captions(ctx: click.Context) -> None:
    sys.exit(_run_script("front-a11y", "install_captions.py", tuple(ctx.args)))


# ── publish ─────────────────────────────────────────────────────────────────

@cli.group(help="Publishing skill (front-publish): MD → site, meta, favicons, indexes, plain language.")
def publish() -> None:
    """front-publish — site, meta, favicons, indexes, plain language."""


@publish.command(name="favicons", context_settings=CONTEXT_SETTINGS,
                 help="Generate favicon / PWA icon set + manifest from a logo.")
@click.pass_context
def publish_favicons(ctx: click.Context) -> None:
    sys.exit(_run_script("front-publish", "favicons.py", tuple(ctx.args)))


@publish.command(name="meta", context_settings=CONTEXT_SETTINGS,
                 help="Draft per-page meta tags (title, description, OG, Twitter, JSON-LD).")
@click.pass_context
def publish_meta(ctx: click.Context) -> None:
    sys.exit(_run_script("front-publish", "meta_from_ollama.py", tuple(ctx.args)))


@publish.command(name="indexes", context_settings=CONTEXT_SETTINGS,
                 help="Emit robots.txt + sitemap.xml + llms.txt + Atom/RSS + humans.txt.")
@click.pass_context
def publish_indexes(ctx: click.Context) -> None:
    sys.exit(_run_script("front-publish", "site_indexes.py", tuple(ctx.args)))


@publish.command(name="plain", context_settings=CONTEXT_SETTINGS,
                 help="Rewrite UI copy in plain language at a target grade.")
@click.pass_context
def publish_plain(ctx: click.Context) -> None:
    sys.exit(_run_script("front-publish", "plain_language.py", tuple(ctx.args)))


@publish.command(name="lint-md", context_settings=CONTEXT_SETTINGS,
                 help="Lint Markdown — headings, alt text, links, LaTeX delimiters, Mermaid (rendered locally).")
@click.pass_context
def publish_lint_md(ctx: click.Context) -> None:
    sys.exit(_run_script("front-publish", "lint_markdown.py", tuple(ctx.args)))


@publish.command(name="md-to-html", context_settings=CONTEXT_SETTINGS,
                 help="Convert Markdown → HTML with local Mermaid PNG embed, KaTeX LaTeX, Inter + Tailwind shell.")
@click.pass_context
def publish_md_to_html(ctx: click.Context) -> None:
    sys.exit(_run_script("front-publish", "md_to_html.py", tuple(ctx.args)))
