---
name: front-a11y
description: >-
  Pre-commit accessibility tooling for vanilla-JS + Tailwind output — static
  a11y lint over HTML files (14 rules, no browser), WCAG contrast audit with
  OKLCH-neighbour fix suggestions, color-vision-deficiency (protanopia /
  deuteranopia / tritanopia) simulation, W3C-compliant alt-text drafting via a
  local Ollama vision model, and WebVTT / SRT captions from a local
  whisper.cpp. For solo developers and small teams who need a fast,
  deterministic, CI-friendly gate before shipping — NOT a replacement for axe-
  core / Pa11y / Lighthouse (runtime DOM audits catch what a static parser
  cannot). Trigger phrases: "a11y lint", "WCAG check", "contrast audit", "is
  my palette accessible", "alt text for this image", "describe this image",
  "captions", "transcript", "colorblind preview", "deuteranope", "CVD". Output
  is JSON / stdout / exit codes suitable for pre-commit and CI.
license: Unlicense
metadata:
  author: Warith Harchaoui
  version: 0.6.2
  lang_pair: "en,fr"  # override per-project; e.g. "en,de" or "en,ja"
---

# front-a11y — accessibility audits and content tooling

## Audience and positioning

Solo developers and small teams who:

- Need a **pre-commit gate** that fails fast on a11y regressions.
- Ship without a dedicated a11y reviewer or QA team.
- Want a11y content (alt text, captions) drafted locally with no SaaS cost or data exfiltration.
- Want a designer-grade contrast audit without a Figma plugin.

This skill is **not** a substitute for runtime DOM testing. Pair it with axe-core / Pa11y / Lighthouse for runtime checks; pair it with manual screen-reader passes for the things only a human can verify (logical reading order, dynamic ARIA states, focus traps after `dialog.showModal()`).

## Honest framing of what each tool covers

| Tool | Layer | Catches | Misses |
|---|---|---|---|
| `scripts/lint_a11y.py` | static HTML source | missing alt, unlabelled inputs, button-without-text, `div onclick`, missing dialog close, lang attr, bad heading order, color-only state, motion-reduce guards — 14 rules decidable from source | anything that depends on JS running (dynamic ARIA, runtime contrast after theme switch, focus order after portal mount, screen-reader announcement of live regions). Pair with **axe-core** or **Pa11y**. |
| `scripts/audit_contrast.py` | palette JSON | WCAG ratio violations on (label × surface) pairs in both light + dark schemes; suggests nearest OKLCH-neighbour fix | does not verify that the suggested fix preserves brand identity or tonal hierarchy. The auto-fix is a **starting point** for a designer, not a finished decision. |
| `scripts/simulate_cvd.py` | image transform | how the surface looks to a protanope / deuteranope / tritanope (Machado et al. matrices). Catches red/green pairing before ship. | does not test motion sensitivity, low-vision blur, or contrast sensitivity beyond color. |
| `scripts/alt_from_ollama.py` | local AI | W3C-compliant alt for informative / decorative / functional / text / complex / group purposes, biased by surrounding page text | model-quality drafts — verify each draft before committing. Top-tier hosted vision (Claude vision, GPT-4o vision, Gemini) is more accurate. |
| `scripts/captions_from_whisper.py` *(WiP)* | local AI | WebVTT / SRT / plain-text captions via whisper.cpp; project-vocab biasing | not real-time; hosted services (Deepgram, AssemblyAI) are better for live captions. **WiP gaps**: per-language WER baselines (en / fr / es extractor wired, baselines not yet published); the `vocab-biasing-clip.wav` is user-supplied. Track shape via `tests/fixtures/audio/README.md`. |

State this when reporting results, especially `lint_a11y` — "passed the static gate" ≠ "WCAG-compliant".

## Decision tree

| Trigger | Tool | Run |
|---|---|---|
| "a11y lint" / "check this HTML for accessibility" / "WCAG check" | `lint_a11y.py` | `python scripts/lint_a11y.py <file-or-dir>` — 14 rules, exit 1 on any finding |
| "contrast audit" / "WCAG ratio" / "is my palette accessible" | `audit_contrast.py` | `python scripts/audit_contrast.py [--palette p.json] [--target 4.5\|7\|3] [--fix]` — walks every (label, surface) pair, suggests OKLCH-neighbour fix |
| "color blind preview" / "CVD check" / "how does this look to a deuteranope" | `simulate_cvd.py` | `python scripts/simulate_cvd.py <image> [--grid]` — renders protanopia / deuteranopia / tritanopia |
| "alt text" / `<img>` with no `alt` / "describe this image" | `alt_from_ollama.py` | Match W3C image-purpose decision tree → `python scripts/alt_from_ollama.py [--kind informative\|decorative\|functional\|text\|complex\|group] [--lang fr] [--in DOC] [--vocab-from DIR] <src>`. Tag drafts with `data-alt-source="ai"`. |
| "captions" / "transcribe video" / "transcribe audio" *(WiP — see below)* | `captions_from_whisper.py` | `python scripts/install_captions.py` then `python scripts/captions_from_whisper.py <audio-or-video> [--format vtt\|srt\|text] [--lang fr] [--vocab-from DIR] [--auto-project]`. Always emit `<track kind="captions">` on `<video>` / `<audio>`. |

## Tool composition (take initiative)

When emitting an `<img>` whose source path appears in a Markdown or HTML doc:

```bash
python scripts/alt_from_ollama.py --in <that-doc> <image>
```

— the surrounding text becomes both `--context` and vocabulary biasing.

When emitting `<video>` or `<audio>`:

```bash
python scripts/captions_from_whisper.py --auto-project <media>
```

— and always emit `<track kind="captions" srclang="…" default>` on the element. Add `<track kind="subtitles">` for translations, `<track kind="descriptions">` for audio descriptions, `<track kind="chapters">` for navigation when chapters exist.

When auditing a UI deliverable end-to-end:

```bash
python scripts/lint_a11y.py public/         # static gate
python scripts/audit_contrast.py --palette palette.json  # WCAG ratios
python scripts/simulate_cvd.py screenshot.png --grid     # CVD pass
```

Then pair with a runtime audit (axe-core / Pa11y / Lighthouse) before shipping.

## Changing the language pair

`front-a11y` inherits **bilingual** defaults (EN/FR by default —
configurable via `lang_pair`). The pair lives in this file's
frontmatter under `metadata.lang_pair` as two comma-separated BCP-47
base tags. It controls the default `--lang` for `alt_from_ollama.py`
and `captions_from_whisper.py`, and is mirrored in
`front-ui/SKILL.md` and `front-publish/SKILL.md` so the three skills
stay in lock-step. To switch (Berlin → `en,de`; Tokyo → `en,ja`;
Madrid → `en,es`), edit the value in all three files. The full
recipe — including meta tags, sitemap `hreflang`, and the
plain-language rewriter — lives in
`front-publish/SKILL.md` → "Changing the language pair" and
`front-publish/references/i18n.md`.

**Runtime override.** Set the `FRONT_LANG_PAIR` environment variable to
override the pair from the shell — its first comma-split entry becomes
the default `--lang` for `alt_from_ollama.py` and
`captions_from_whisper.py` when no flag is passed:

```bash
export FRONT_LANG_PAIR="en,de"
python front-a11y/scripts/alt_from_ollama.py photo.jpg   # → German alt text
```

Precedence (highest first): explicit `--lang` flag → `FRONT_LANG_PAIR`
first entry → langdetect on available text → POSIX locale fallback.

## When NOT to use this skill

- You need runtime DOM-aware a11y testing (React-mounted components, dynamic ARIA states, focus management after async state change) → use **axe-core** + Playwright.
- You need real-time live captions (live streams, video calls) → use **Deepgram** or **AssemblyAI**.
- You need top-quality alt text and don't care about local-only / cost → use **Claude vision** or **GPT-4o vision** APIs.
- You need a designer-grade palette redesign — `audit_contrast.py --fix` is a hint, not a final decision. Loop a designer in.

## References

- `references/lint-a11y.md` — Static a11y linter rule catalogue (14 rules) and CI integration.
- `references/contrast-audit.md` — WCAG contrast audit and OKLCH-neighbour fix suggester.
- `references/cvd-simulation.md` — Color-blindness simulator (protanopia / deuteranopia / tritanopia).
- `references/alt-text-ai.md` — W3C-compliant alt text via local Ollama + Gemma vision (per-purpose decision tree).
- `references/captions-ai.md` — Local pywhispercpp captions / transcripts for video and audio, with vocabulary biasing.

## Scripts

| Script | Install | Purpose |
|---|---|---|
| `scripts/lint_a11y.py` | stdlib only | 14-rule static a11y lint. Exit 1 on any finding. **Not** a substitute for runtime audit. |
| `scripts/audit_contrast.py` | stdlib only | WCAG contrast audit + OKLCH-neighbour fix suggester. Hint to designer, not final decision. |
| `scripts/simulate_cvd.py` | `pip install -r scripts/requirements-cvd.txt` | Protanopia / deuteranopia / tritanopia rendering (Machado matrices). |
| `scripts/alt_from_ollama.py` | `pip install -r scripts/requirements-alt-text.txt` + Ollama | W3C-compliant alt text via local vision model. |
| `scripts/install_alt_ai.py` | subprocess | Installs Ollama + pulls vision model. |
| `scripts/captions_from_whisper.py` *(WiP)* | `pip install -r scripts/requirements-captions.txt` | WebVTT / SRT / plain-text captions via local whisper.cpp. Script works today; per-language WER baselines + vocab-biasing reference clip still being collected. |
| `scripts/install_captions.py` | subprocess | Installs pywhispercpp + downloads model. |
| `scripts/_lang.py`, `scripts/_vocab.py`, `scripts/_ollama.py` | (internal helpers) | Language detection, project-vocab biasing, shared Ollama client. |

## Companion skills

| You also need… | Install |
|---|---|
| Vanilla-JS + Tailwind UI generation | `front-ui` |
| Wrap a CLI in a GUI | `front-cli-gui` |
| Markdown → website + meta + favicons + indexes | `front-publish` |
