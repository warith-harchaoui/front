# EXAMPLES

A runnable cookbook for the `front-*` skill suite — one section per skill,
each with a copy-paste command and the output you should expect. Commands are
written to run from the **repository root** and use the checked-in fixtures
under `tests/fixtures/`, so every deterministic recipe here runs with no setup
beyond the skill's own dependencies.

See also: [`README.md`](README.md) for the skill map, [`GALLERY.md`](GALLERY.md)
for real projects shipped with the suite, and each skill's `SKILL.md` for the
full flag surface.

## Two kinds of recipe

- **Deterministic** (🟢) — pure Python, no model, no network. Runs anywhere;
  output is byte-stable. These are the audit gates and the make-from-data
  generators. Safe in CI and `pre-commit`.
- **Local-AI** (🤖) — calls a **local** model (Ollama for vision/text, a local
  whisper.cpp build for audio). Never a SaaS. Requires a one-time `install_*`
  step; output varies by model. Draft-quality — verify before shipping.

Exit codes follow the usual convention: `0` = clean / success, non-zero =
findings or error (so the audits gate a commit).

---

## front-accessibility 🟢 — static a11y lint

Lint a static HTML file for the 14 source-decidable accessibility rules
(missing `alt`, unlabelled inputs, `<div onclick>`, heading order, …):

```bash
python3 front-accessibility/scripts/lint_a11y.py tests/fixtures/html/landing.html
```

Expected output (a clean fixture):

```text

0 findings.
```

Exit code `0`. A file with problems prints one line per finding (`file:line:
RULE message`) and exits non-zero. Add `--fix` to apply the safe repairs
(lang attribute, redundant ARIA, positive tabindex, aria-hidden-interactive,
motion-reduce guard) in place, and `--json` for machine-readable output.

## front-ux-laws 🟢 — Laws-of-UX audit

Audit HTML for the mechanically-detectable Laws of UX (Hick, Miller, Fitts,
Jakob, Tesler, Aesthetic-Usability, …), as JSON:

```bash
python3 front-ux-laws/scripts/audit_laws_of_ux.py tests/fixtures/html/landing.html --json
```

Expected output (shape):

```json
[
  {
    "law": "aesthetic-usability",
    "severity": "warning",
    "path": "tests/fixtures/html/landing.html",
    "line": 24,
    "message": "<a> has no focus-visible:ring-* class. Add the house focus token.",
    "snippet": ""
  }
]
```

`--fix` applies the four mechanical fixers (Fitts / Aesthetic-Usability /
Miller / Jakob) with an idempotent convergence loop; `--only hick,jakob` and
`--ignore tesler,miller` scope the run; `--strict` upgrades warnings to errors.

## front-colors 🟢 — WCAG contrast, CVD, palette → Tailwind

Audit a palette for WCAG contrast (suggests OKLCH-neighbour fixes):

```bash
python3 front-colors/scripts/audit_contrast.py --palette palette.json --target 4.5
```

Turn the canonical palette CSV into a drop-in `tailwind.config.js`:

```bash
python3 front-colors/scripts/palette_to_tailwind.py --emit theme > tailwind.theme.js
```

Simulate colour-vision deficiency on a screenshot (writes protanopia /
deuteranopia / tritanopia variants next to the input):

```bash
python3 front-colors/scripts/simulate_cvd.py tests/fixtures/images/chart-bar.png
```

All three are deterministic — no model, no network.

## front-figures 🟢 — data-viz + an auditor

Audit a Vega-Lite spec for data-viz sins (truncated baselines, dual y-axes,
rainbow palettes, missing labels):

```bash
python3 front-figures/scripts/audit_figure.py my_chart.vl.json
```

Make a publication-quality figure in the house style from a data file:

```bash
python3 front-figures/scripts/make_figure.py --data data.csv --kind bar --x category --y value --out chart
```

> **Note — figures loop.** When *generating* a Vega-Lite figure, don't ship it
> blind: render the spec to PNG, look at it, critique (labels, baseline,
> palette, CVD-safety, legibility), revise, and repeat until it reads clearly.
> A spec that validates can still look wrong.

Model-explainability and causal recipes (need the `explain` / `causal` tiers —
`python3 front-figures/scripts/install_figures.py --tier dataviz+explain+causal`):

```bash
python3 front-figures/scripts/explain_model.py --model model.pkl --data X.csv --engine shapash --report shapash --out ./explain/
python3 front-figures/scripts/causal_estimate.py --data d.csv --treatment T --outcome Y --confounders "X1,X2,X3" --dag dag.gml
```

## front-publish 🟢 — Markdown → site, meta, favicons, indexes

Lint a Markdown file (heading sentinel, trailing whitespace, fenced-code
language); `--fix` applies the safe rewrites:

```bash
python3 front-publish/scripts/lint_markdown.py tests/fixtures/public/gettysburg.md
```

A clean file prints nothing and exits `0`. Generate a full favicon / app-icon /
PWA-icon set from one logo (needs Pillow):

```bash
python3 front-publish/scripts/favicons.py logo.png --out public --name "My Project"
```

Emit `robots.txt` + `sitemap.xml` + `llms.txt` + optional Atom feed for a docs
tree:

```bash
python3 front-publish/scripts/site_indexes.py --root . --base-url https://example.com --feed-from posts
```

Narration (`narrate_post.py`) and meta-tag drafting (`meta_from_ollama.py`) are
🤖 local-AI — see below.

## front-cli-gui 🟢 — wrap a CLI in a GUI

Introspect a Python CLI's argument parser (argparse **or** Click — auto-detected)
and emit a single-page vanilla-JS + Tailwind GUI. Point `spec` at a zero-arg
factory that returns the parser/command:

```bash
# demo_cli.py exposes `def make_parser() -> argparse.ArgumentParser`
python3 front-cli-gui/scripts/cli_to_gui.py demo_cli.py:make_parser --out gui.html
```

Expected output:

```text
cli_to_gui: wrote gui.html
```

For any CLI whose factory can't be imported — or a non-Python binary
(clap / cobra / commander) — parse its `--help` text instead:

```bash
python3 front-cli-gui/scripts/cli_to_gui.py --from-help "python3 -m json.tool" --out gui.html
```

The emitted HTML passes both the `front-ux-laws` and `front-accessibility`
audits with zero findings (the emitter is its own customer). A runnable worked
example ships in `front-cli-gui/assets/examples/cli-gui-demo/`.

## front-vision 🤖 — alt text via a local vision model

One-time install (pulls a local Ollama vision model):

```bash
python3 front-vision/scripts/install_alt_ai.py
```

Draft W3C-compliant alt text for an image (bilingual EN/FR by default):

```bash
python3 front-vision/scripts/alt_from_ollama.py tests/fixtures/images/portrait.jpg
```

Prints the drafted alt text to stdout. `--kind informative|decorative|functional|
text|complex|group` forces the purpose; results are cached on disk so the same
image + parameters never hit the model twice. Draft-quality — verify before
committing.

## front-audio 🤖 — captions, diarization, speaker naming

One-time install (pip-installs `vocal-helper` / whisper.cpp and pre-downloads a
GGML model so it runs offline):

```bash
python3 front-audio/scripts/install_captions.py
```

Transcribe audio/video to WebVTT / SRT / plain text (local, never a SaaS):

```bash
python3 front-audio/scripts/captions_from_whisper.py interview.mp4 --format vtt
```

Add "who spoke when" and "who is who" (needs `install_diarize.py` for the NeMo
Sortformer + TitaNet weights):

```bash
python3 front-audio/scripts/diarize_from_nemo.py interview.wav --out interview.diarization.json
python3 front-audio/scripts/caption_diarize.py --captions interview.vtt --diarization interview.diarization.json
```

## front-ui 🟢 — the stack rules + component assets

`front-ui` is reference-first: it sets the vanilla-JS + Tailwind house style
(three-Roboto default, dark-mode peers, focus rings, reduced-motion guards) that
every other skill's output follows. Its make-side assets ship ready to copy:

```bash
# Starter page and law-keyed component snippets
ls front-ui/assets/starter-page.html front-ui/assets/snippets/
```

Validate that a skill folder is spec-compliant (used in CI via
`scripts/validate_all.py`):

```bash
python3 front-ui/scripts/validate.py front-ui
```

---

## Running the whole audit sweep

The deterministic audits are wired as `pre-commit` hooks (see
`.pre-commit-hooks.yaml`) so they gate commits. To run the repo's own checks:

```bash
python3 scripts/validate_all.py     # spec + content gate on all 9 skills
python3 -m pytest -q                 # full test suite (incl. tests/eval/ AI-eval layer)
```
