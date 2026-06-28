---
name: front-accessibility
description: >-
  Pre-commit static HTML accessibility lint for vanilla-JS + Tailwind output.
  Fourteen rules decidable from source — missing alt, unlabelled inputs,
  button-without-text, ``<div onclick>``, missing dialog close, ``lang``
  attribute, bad heading order, color-only state, motion-reduce guards, and
  more — without a browser or runtime DOM. For solo developers and small
  teams who need a fast, deterministic, CI-friendly gate before shipping —
  NOT a replacement for axe-core / Pa11y / Lighthouse (runtime DOM audits
  catch what a static parser cannot). Color contrast lives in the companion
  ``front-colors`` skill, AI alt-text in ``front-vision``, AI captions in
  ``front-audio``. Trigger phrases: "a11y lint", "check this HTML for
  accessibility", "static a11y check", "WCAG-friendly lint", "a11y
  pre-commit". Output is JSON / stdout / exit codes suitable for pre-commit
  and CI.
license: Unlicense
compatibility: >-
  Runtime: Claude.ai, Claude Code, OpenCode. The lint_a11y script needs
  Python 3.9+ stdlib only — no third-party deps, no browser, no network.
metadata:
  author: Warith Harchaoui
  version: 0.9.0
  lang_pair: "en,fr"  # override per-project; e.g. "en,de" or "en,ja"
---

# front-accessibility — static HTML a11y lint

## Audience and positioning

Solo developers and small teams who:

- Need a **pre-commit gate** that fails fast on a11y regressions in
  HTML source — no browser, no runtime DOM, no waiting for a CI
  container to spin up a headless Chromium.
- Want **stdlib-only Python** (3.9+) so the gate fits in any base
  container and adds zero install time.
- Don't ship without a designer or QA team, and want the most obvious
  static-decidable rules covered automatically before the diff lands.

This skill is **not** a substitute for runtime DOM testing. Pair it
with **axe-core** / **Pa11y** / **Lighthouse** for runtime checks
(dynamic ARIA states, focus traps after ``dialog.showModal()``,
color contrast after a runtime theme switch, name/role/value after
portal mounts), and with manual screen-reader passes for the things
only a human can verify (logical reading order, dynamic ARIA states
changing, screen-reader announcement of live regions).

## Two modes — make and audit

This skill is **audit-only** in the front-* duality — by design:

| Mode | Tool | Purpose |
|---|---|---|
| **Make** — generate accessible output | _(none — companions cover this)_ | `front-ui` ships semantic HTML + dark-mode peers + focus rings as defaults; `front-vision` drafts W3C alt text; `front-audio` drafts WebVTT / SRT captions. |
| **Audit** — gate before ship | `scripts/lint_a11y.py` | 14 static rules over HTML (missing alt, unlabelled inputs, button-without-text, `div onclick`, missing dialog close, lang attr, bad heading order, color-only state, motion-reduce guards). Stdlib only, no browser. |

For runtime DOM audits (post-JS, dynamic ARIA, focus traps after async)
pair this skill with `axe-core` / `Pa11y` / `Lighthouse`. A green
static lint is not WCAG compliance — it is the cheapest pre-commit
gate that catches the static-decidable rules.

## What `lint_a11y.py` catches

Fourteen rules decidable from the HTML source — no JavaScript
execution required:

1. ``<img>`` without ``alt`` attribute.
2. ``<input>`` / ``<select>`` / ``<textarea>`` without a label or
   ``aria-label`` / ``aria-labelledby``.
3. ``<button>`` with no accessible text content (no text node, no
   ``aria-label``, no labelled child icon).
4. ``<div onclick>`` / ``<span onclick>`` masquerading as a button.
5. ``<dialog>`` without a close mechanism (``method="dialog"``
   button, ``form method="dialog"`` or visible close affordance).
6. ``<html>`` missing the ``lang`` attribute.
7. Skipped heading levels (e.g. ``<h2>`` → ``<h4>``) inside the same
   landmark.
8. Color-only state cues (no other affordance — text, icon, border —
   carrying the same information).
9. Missing ``prefers-reduced-motion`` guard on any animation block.
10. ``<a>`` without ``href`` or ``role="button"``.
11. Multiple ``<h1>`` per landmark.
12. Form ``<label>`` whose ``for`` does not resolve to any element id.
13. ``alt=""`` decorative override paired with ``role="img"`` or
    ``aria-label`` (contradictory signals).
14. Tab-order ``tabindex`` > 0 anywhere (anti-pattern; use DOM order
    instead).

Exit code is non-zero on any finding. Use ``--format json`` for CI
parsing, ``--format text`` for terminal review.

> "Passed the static gate" ≠ "WCAG-compliant". State this when
> reporting results — the rules above cover the *decidable* a11y
> regressions; everything dependent on runtime DOM still needs a
> browser-based audit.

## Decision tree

| Trigger | Tool | Run |
|---|---|---|
| "a11y lint" / "check this HTML for accessibility" / "static a11y check" | `lint_a11y.py` | `python scripts/lint_a11y.py <file-or-dir>` — 14 rules, exit 1 on any finding |
| "contrast audit" / "WCAG ratio" / "colorblind preview" | (see `front-colors`) | `python front-colors/scripts/audit_contrast.py [--palette p.json] [--fix]` and `python front-colors/scripts/simulate_cvd.py <image>`. |
| "alt text" / `<img>` with no `alt` / "describe this image" | (see `front-vision`) | `python front-vision/scripts/alt_from_ollama.py [--kind informative\|decorative\|functional\|text\|complex\|group] [--lang fr] [--in DOC] [--vocab-from DIR] <src>`. |
| "captions" / "transcribe video" / "transcribe audio" / "subtitle file" | (see `front-audio`) | `python front-audio/scripts/install_captions.py` then `python front-audio/scripts/captions_from_whisper.py <audio-or-video> [--format vtt\|srt\|text] [--lang fr] [--vocab-from DIR] [--auto-project]`. |

## Tool composition

For a UI deliverable end-to-end:

```bash
python front-accessibility/scripts/lint_a11y.py public/                  # static a11y gate
python front-colors/scripts/audit_contrast.py --palette palette.json     # WCAG ratios
python front-colors/scripts/simulate_cvd.py screenshot.png --grid        # CVD pass
python front-vision/scripts/alt_from_ollama.py public/hero.jpg           # AI alt text
python front-audio/scripts/captions_from_whisper.py public/podcast.mp4   # AI captions
```

Then pair with a runtime audit (axe-core / Pa11y / Lighthouse) before
shipping.

## Changing the language pair

`front-accessibility` inherits **bilingual** defaults (EN/FR by default
— configurable via `lang_pair`). The pair lives in this file's
frontmatter under `metadata.lang_pair` as two comma-separated BCP-47
base tags. The lint output messages are English-only today; the
``lang_pair`` token is mirrored across every front-* SKILL.md so a
project-wide language switch stays consistent. See
`front-publish/SKILL.md` → "Changing the language pair" and
`front-publish/references/i18n.md` for the canonical recipe.

## When NOT to use this skill

- You need **runtime DOM-aware a11y testing** (React-mounted components,
  dynamic ARIA states, focus management after async state change) →
  use **axe-core** + Playwright.
- You need **a designer-grade palette / contrast audit** with
  OKLCH-neighbour fix hints — use the companion ``front-colors`` skill.
- You need **AI alt text** drafted from images — use the companion
  ``front-vision`` skill.
- You need **AI captions / transcripts** from audio / video — use the
  companion ``front-audio`` skill.

## References

- ``references/lint-a11y.md`` — Static a11y linter rule catalogue (14
  rules) and CI integration.

## Scripts

| Script | Install | Purpose |
|---|---|---|
| ``scripts/lint_a11y.py`` | stdlib only | 14-rule static a11y lint. Exit 1 on any finding. **Not** a substitute for runtime audit. |
| ``scripts/_argparse.py`` | (internal helper) | Argparse parser factory shared across the skill family (duplicated per-skill for autonomy). |

## Companion skills

| You also need… | Install |
|---|---|
| WCAG contrast audit, CVD simulation, curated palette, perceptual lighten / darken | ``front-colors`` |
| W3C alt text via local Ollama vision (``gemma4:e4b`` / ``-mlx`` on Apple silicon) | ``front-vision`` |
| Local WebVTT / SRT captions via whisper.cpp | ``front-audio`` |
| Vanilla-JS + Tailwind UI generation | ``front-ui`` |
| Wrap a CLI in a GUI | ``front-cli-gui`` |
| Markdown → website + meta + favicons + indexes | ``front-publish`` |
