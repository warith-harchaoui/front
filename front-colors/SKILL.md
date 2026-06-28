---
name: front-colors
description: >-
  Pre-commit color tooling for vanilla-JS + Tailwind output — WCAG contrast
  audit with OKLCH-neighbour fix suggestions, color-vision-deficiency
  (protanopia / deuteranopia / tritanopia) simulation on screenshots, a
  curated Apple-inspired palette with semantic projections (base, emotion,
  concepts, psychology), perceptual lighten / darken on the OKLCH L axis,
  and stdlib-only conversions (sRGB ↔ linear, hex ↔ RGB, OKLab / OKLCH).
  Deterministic — no model, no network. For solo developers and small
  teams who need a fast, CI-friendly color gate before shipping.
  Trigger phrases: "WCAG check", "contrast audit", "is my palette
  accessible", "colorblind preview", "deuteranope", "CVD", "lighten this
  color", "perceptual palette", "OKLCH", "color name", "Apple palette",
  "emotion color". Output is JSON / stdout / exit codes suitable for
  pre-commit and CI.
license: Unlicense
compatibility: >-
  Runtime: Claude.ai, Claude Code, OpenCode. Core scripts (audit_contrast,
  simulate_cvd) need Python 3.9+ stdlib + Pillow (for simulate_cvd only).
  No network or model required at any point.
metadata:
  author: Warith Harchaoui
  version: 0.2.0
---

# front-colors — color audit, curation, and perceptual transforms

## Audience and positioning

Solo developers and small teams who:

- Need a **pre-commit gate** that fails fast on contrast regressions.
- Want a curated starter palette rather than picking colors at random.
- Want CVD (color-blindness) review without a browser extension or SaaS.
- Need perceptual color shifts (lighten / darken / hue rotate) for
  generating tints and shades — not the naïve RGB offsets that wash
  saturated hues into pastels.

This skill is **not** a substitute for designer judgment. The
auto-fix from `audit_contrast.py --fix` is a *starting point* — it walks
the OKLCH lightness axis to find the nearest accessible neighbour, but
it can't tell you whether the resulting tonal hierarchy still matches
your brand. Loop a designer in for the final call.

## Honest framing of what each tool covers

| Tool | Catches | Misses |
|---|---|---|
| `scripts/audit_contrast.py` | WCAG ratio violations on (label × surface) pairs; suggests nearest OKLCH-neighbour fix | does not verify brand identity or tonal hierarchy. The fix is a hint, not a final decision. |
| `scripts/simulate_cvd.py` | how a surface looks to a protanope / deuteranope / tritanope (Machado et al. 2009 matrices). Catches red/green pairing before ship. | does not test motion sensitivity, low-vision blur, or contrast sensitivity beyond color. |
| `scripts/_colors.py` | shared primitives: sRGB ↔ linear, hex parsing, WCAG luminance / contrast, OKLab / OKLCH (Björn Ottosson), CVD matrices, perceptual `lighten` / `darken`, palette accessors | not a full-blown color library — no CMYK, no Lab D50, no gamut mapping beyond the OKLCH L axis search. |

## Decision tree

| Trigger | Tool | Run |
|---|---|---|
| "contrast audit" / "WCAG ratio" / "is my palette accessible" | `audit_contrast.py` | `python scripts/audit_contrast.py [--palette p.json] [--target 4.5\|7\|3] [--fix]` — walks every (label, surface) pair, suggests OKLCH-neighbour fix |
| "color blind preview" / "CVD check" / "how does this look to a deuteranope" | `simulate_cvd.py` | `python scripts/simulate_cvd.py <image> [--grid]` — renders protanopia / deuteranopia / tritanopia |
| "what's the hex for Red" / "give me an emotion color" / "Apple palette" | `_colors.py` accessors | `from _colors import name_to_hex, emotion_to_hex, concept_search, psychology_for, apple_palette` |
| "lighten this color" / "darken" / "tint" / "shade" | `_colors.lighten` / `_colors.darken` | OKLCH L-axis shift; hue and chroma preserved (unlike a naïve RGB offset). |

## The unified palette

`references/palette.csv` is **one canonical row per color**, with semantic
projections as columns:

| Hex | Base | Emotion | Concepts | Psychology (+) | Psychology (−) |
|---|---|---|---|---|---|
| #FF3B30 | Red | Anger | Excitement, Youthful, Bold | Power, Passion, Energy… | Anger, Danger, Warning… |
| #FF9500 | Orange | Surprise | Friendly, Cheerful, Confidence | Courage, Confidence… | Deprivation, Frustration… |
| … | … | … | … | … | … |

The same hex can serve multiple semantics — e.g. `#FF3B30` is *Red* (base), *Anger* (emotion), and carries both
"Excitement" (concept) and "Power" (psychology positive). A single source
of truth keeps these projections consistent.

Accessors in `_colors.py`:

```python
from _colors import (
    apple_palette,         # {"Red": "#FF3B30", "Orange": "#FF9500", ...}
    name_to_hex,           # "Red"     → "#FF3B30"
    name_to_rgb,           # "Red"     → (255, 59, 48)
    light_variant,         # "Red"     → "#FFD8D6" (curated)
    emotion_to_hex,        # "Anger"   → "#FF3B30"
    concept_search,        # "Bold"    → ["#FF3B30"]
    psychology_for,        # "Red"     → {"positive": [...], "negative": [...]}
)
```

## Perceptual lighten / darken

The classical "add 70 to each RGB channel" approach washes saturated
hues into pastels and shifts apparent hue. `_colors.lighten` and
`_colors.darken` shift the OKLCH **L** axis instead, keeping chroma
and hue intact:

```python
from _colors import lighten, darken, Color

lighten("#007AFF", 0.15)   # "#5FA8FF" — same hue, lighter
darken("#FFCC00", 0.10)    # "#D9AE00" — same hue, darker

# Or via the Color class
brand = Color("#007AFF")
brand.lighten(0.15).contrast_with("#FFFFFF")
brand.meets_wcag("#FFFFFF", level="AA", size="normal")  # True
```

## Tool composition

For a UI deliverable end-to-end:

```bash
python front-colors/scripts/audit_contrast.py --palette palette.json --fix    # WCAG ratios
python front-colors/scripts/simulate_cvd.py screenshot.png --grid             # CVD pass
python front-accessibility/scripts/lint_a11y.py public/                                # static a11y gate
```

Pair with a runtime audit (axe-core / Pa11y / Lighthouse) before shipping.

## When NOT to use this skill

- You need a full-featured design-token pipeline (Style Dictionary / Theo /
  Tokens Studio) — use those; this skill is a deterministic gate, not a
  pipeline.
- You need print color (CMYK, Pantone matching) — out of scope.
- You need a designer-grade palette redesign — `audit_contrast.py --fix`
  is a hint, not a final decision. Loop a designer in.
- You need automatic theming (light/dark generation from a single hue) —
  the perceptual primitives are here, but a thoughtful theme is a design
  decision, not an algorithmic one.

## References

- `references/contrast-audit.md` — WCAG contrast audit and OKLCH-neighbour fix suggester.
- `references/cvd-simulation.md` — Color-blindness simulator (protanopia / deuteranopia / tritanopia).
- `references/palette.csv` — Curated palette with semantic projections.

## Scripts

| Script | Install | Purpose |
|---|---|---|
| `scripts/audit_contrast.py` | stdlib only | WCAG contrast audit + OKLCH-neighbour fix suggester. Hint to designer, not final decision. |
| `scripts/simulate_cvd.py` | `pip install -r scripts/requirements-cvd.txt` (Pillow) | Protanopia / deuteranopia / tritanopia rendering (Machado matrices). |
| `scripts/_colors.py` | stdlib only | Shared color primitives — sRGB ↔ linear, hex ↔ RGB, OKLab / OKLCH, WCAG, CVD matrices, perceptual lighten / darken, palette accessors, `Color` class. Internal helper; not invoked directly via the CLI router. |

## Companion skills

| You also need… | Install |
|---|---|
| Static HTML a11y lint | `front-accessibility` |
| AI alt text via local Ollama vision | `front-vision` |
| Local WebVTT / SRT captions via whisper.cpp | `front-audio` |
| Vanilla-JS + Tailwind UI generation | `front-ui` |
| Wrap a CLI in a GUI | `front-cli-gui` |
| Markdown → website + meta + favicons + indexes | `front-publish` |
