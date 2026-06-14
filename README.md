

# Front

[🇫🇷](LISEZMOI.md) · [🇬🇧](README.md)

<p align="center">
  <img src="assets/logo.png" alt="Front — a Claude skill for vanilla JS + Tailwind + Montserrat frontends" width="240">
</p>

## What this is

`front` is a Claude skill that constrains Claude to a single, consistent frontend stack — vanilla JavaScript, Tailwind CSS, and Montserrat as the only typeface — and gives it a curated design system to draw from. Asking Claude to "build a UI", "create a component", "design a dashboard", or "wrap this CLI in a GUI" produces output in this exact stack with a repeatable point of view: semantic HTML, dark-mode peers on every styled element, focus rings, reduced-motion guards, color choices traceable to a documented psychology, charts via Vega-Lite, alt text drafted to W3C / WAI guidance.



## What it's for

Most LLM-generated frontends share a generic look — purple gradients, glassmorphic cards, marketing buzzwords, three-card hero grids — because the model defaults to its most-common training patterns. This skill replaces those defaults with one stack, one font, one color philosophy, one set of ergonomic criteria. The result is frontend output that's consistent across sessions, free of "AI-generated" tells, and ready to ship in any project that wants this stack.

The flagship use case is **CLI → GUI**: point Claude at an existing command-line tool's `--help`, and the skill produces the matching vanilla-JS + Tailwind GUI in one session. Other use cases: new components, full pages, ergonomic audits, dashboards and dataviz, migrations away from a framework toward vanilla JS, and accessibility tooling (W3C-grade alt text, meta tags, favicon set, validator).

## Inputs → outputs

What you give Claude, and what comes back. Each row is a self-contained flow — pick one, ignore the rest. Every output respects the stack rules in *What the skill enforces*.

| What you provide (input) | How you phrase it | What Claude returns (output) | Tools touched |
|---|---|---|---|
| A working CLI (`tool --help`, source with `argparse` / `clap` / `commander` / `cobra`) | "Wrap this CLI in a GUI" + the project path | One-page `index.html` + `app.js` + Tailwind CSS, sub-commands mapped to forms / streams / tables, wired to your host (Tauri / Electron / FastAPI / Express / browser stub). Montserrat self-hosted. | `front/SKILL.md` → CLI → GUI workflow; `assets/examples/cli-gui-demo/` |
| A folder of Markdown files (README, `docs/**`, blog posts) | "Turn these markdown files into a website" | Static site: one HTML page per `.md`, sticky top bar, sidebar TOC for `docs/`, dark-mode peer, favicons, `<meta>` tags, `robots.txt` + `sitemap.xml` + `llms.txt` + Atom feed. Drops into GitHub Pages / Netlify / S3 / Nginx. | `references/meta-tags.md`, `scripts/favicons.py`, `scripts/meta_from_ollama.py`, `scripts/site_indexes.py` |
| A free-form ask ("primary button", "confirm dialog", "settings page", "bottom sheet") | "Build a `<component>`" | Semantic HTML + Tailwind classes + minimal vanilla JS, focus ring, `dark:` peer, 44×44 hit area, `Escape` close on dialogs, reduced-motion guard. | `references/ui-guidelines/components/*.md`, `assets/components/*.html` |
| A data shape (CSV, JSON, a few rows pasted into chat) | "Chart this" / "Dashboard for X" | Vega-Lite v5 JSON spec + a `<figure>` wrapper. House style (Montserrat, 10 px corners, no top/right spines, palette from `color-psychology.md`), axis labelled with polarity (*↑ higher is better* / *↓ lower is better* / *target = N ± k*), `role="img"` + `aria-label`. | `references/charts-vega.md`, `references/dataviz-chart-selection.md`, `references/dashboard-ergonomics.md`, `assets/components/chart-*.json` |
| An existing HTML page or screenshot | "Audit this" / "Make it look less AI" / "Ergonomic review" / "WCAG check" | Findings against the 8 ergonomic criteria + the anti-patterns catalogue; concrete diffs to fix; pre-ship checklist run. | `references/ergonomics-criteria.md`, `references/anti-patterns.md`, `references/ux-psychology.md`, `references/checklist.md`, `scripts/lint_a11y.py`, `scripts/audit_contrast.py`, `scripts/simulate_cvd.py` |
| An image file (`*.png`, `*.jpg`, …) | "Alt text for this image" (optionally with the host doc) | W3C-compliant alt text for the right purpose category (informative / decorative / functional / text / complex / group), drafted in the page's language, tagged `data-alt-source="ai"`. | `references/alt-text-ai.md`, `scripts/alt_from_ollama.py`, `scripts/install_alt_ai.py` |
| An audio or video file (`.mp4`, `.wav`, `.mp3`, …) | "Captions / transcript" / "Add captions" | WebVTT / SRT / plain-text captions from local Whisper, with project-vocab biasing. `<video>` + `<track kind="captions">` snippet for the page. | `references/captions-ai.md`, `scripts/install_captions.py`, `scripts/captions_from_whisper.py` |
| A logo (`logo.png` / `.svg`) | "Favicon set" / "App icons" / "PWA icons" | `favicon.svg` + `.ico` + PNG set + `apple-touch-icon.png` + maskable PWA icon + `site.webmanifest` + a `head.html` snippet to paste into every page. | `references/ui-guidelines/foundations/app-icons.md`, `references/meta-tags.md`, `scripts/favicons.py` |
| A goal description ("page about X") or an HTML page | "Meta tags" / "SEO" / "OG card" | Title + description + Open Graph + Twitter Card + Schema.org JSON-LD, per `meta-tags.md`. JSON on stdout. | `references/meta-tags.md`, `scripts/meta_from_ollama.py` |
| Draft UI copy | "Plain language" / "Rewrite at grade 8" | Same meaning, marketing voice stripped, output length ≤ 1.1× original. | `references/plain-language.md`, `scripts/plain_language.py` |
| A palette JSON (or none) | "Contrast audit" / "Is my palette accessible?" | Every `(label, surface)` pair walked, failures listed with the nearest OKLCH-neighbour fix. Exit 1 on any failure. | `references/contrast-audit.md`, `scripts/audit_contrast.py` |
| A finished page / screenshot | "Pre-ship check" | The `checklist.md` gate executed: stack purity, semantics, contrast both modes, dark-mode peers, motion, copy, performance, bilingual. | `references/checklist.md`, `scripts/validate.py`, `scripts/lint_a11y.py` |

> Not sure which row you're on? Describe the input in plain English. The skill's `SKILL.md` decision tree maps phrasing → workflow.

For alternatives in every category — and how to decide whether `front` is the right tool — see [LANDSCAPE.md](LANDSCAPE.md).

## Contents

- `front/SKILL.md` — entry point with YAML frontmatter and instructions.
- `front/references/` — progressive-disclosure reference files (color, stack, checklist, UI guidelines, dataviz, meta tags, i18n, anti-patterns, UX psychology, Material Design, alt text, captions, contrast / CVD audits, plain-language rewriter, a11y lint, site indexes).
- `front/assets/` — copy-paste templates, Montserrat font files, and a runnable CLI → GUI example (`assets/examples/cli-gui-demo/`).
- `front/scripts/` — Python helpers, each with its own feature-scoped requirements file:
  - **Pre-ship gate** — `validate.py`, `lint_a11y.py`, `audit_contrast.py`, `site_indexes.py` (stdlib only).
  - **Assets & meta** — `favicons.py`, `meta_from_ollama.py`.
  - **A11y & accessibility tooling** — `alt_from_ollama.py`, `install_alt_ai.py`, `simulate_cvd.py`, `plain_language.py`.
  - **Captions / transcripts** — `install_captions.py`, `captions_from_whisper.py`.
- `llms.txt` — index of the project per <https://llmstxt.org/> for LLM consumers.
- `LANDSCAPE.md` — comparison matrices of alternatives in every category the skill touches (frameworks, CSS, components, dataviz, CLI → GUI hosts, MD → site generators, a11y / alt-text / captions tooling, …) so you can decide whether `front` is the right pick.
- `assets/logo.png` — project logo (used at the top of this README).

## What the skill enforces

- Output uses vanilla JS (ES modules, native `<dialog>`, custom elements when justified). No React, Vue, Svelte, Next.js, Nuxt, Angular, Solid.
- Output uses Tailwind utility classes with semantic tokens (`bg-brand-blue`, `text-label-primary`). No raw hex in markup.
- Output uses Montserrat as the sole UI typeface, self-hosted from `assets/fonts/montserrat/`.
- Output sets a `dark:` peer on every styled element, uses `<button>`/`<a>`/`<label>`/`<dialog>`/`<form>` first, exposes a visible focus ring, honors `prefers-reduced-motion`, and meets a 44×44 px hit area.
- Color choices map to the four palettes in `references/color-psychology.md` (source: <https://harchaoui.org/warith/colors/>).

## CLI → GUI

The skill includes a workflow that takes an existing command-line tool and produces a single-page vanilla-JS + Tailwind GUI for it. The workflow reads the CLI's argument parser, categorizes each command (one-shot / form / streaming / list), maps flags to form controls, and wires execution to the project's host (Tauri, Electron, FastAPI, Express, or a browser stub). See `front/SKILL.md` → "CLI → GUI workflow".

## Install

This skill is built to the [Anthropic skill specification](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf), which means it is read natively — frontmatter auto-trigger, progressive disclosure of `references/`, and direct invocation of `scripts/` — by two coding agents: **Claude Code** and **OpenCode**. Pick whichever matches your editor and model preferences.

### Claude Code

```bash
mkdir -p ~/.claude/skills
cp -r front ~/.claude/skills/front
```

Verify:

```bash
ls ~/.claude/skills/front/SKILL.md
```

Claude Code reads the skill's frontmatter description and applies the skill when a user message matches its trigger phrases.

### OpenCode

[OpenCode](https://opencode.ai) is an open-source terminal coding agent that supports Claude, GPT, and local models behind the same UX.

```bash
mkdir -p ~/.opencode/skills
cp -r front ~/.opencode/skills/front
```

OpenCode discovers the skill from the same `SKILL.md` frontmatter description and weaves in the scripts under `front/scripts/` exactly like Claude Code does. Use this when you want the skill's behavior without provider lock-in, or when you're already running OpenCode as your daily driver.

## Repository structure

```
front/                              ← repo root
├── README.md / LISEZMOI.md         ← EN / FR
├── LANDSCAPE.md                    ← comparison matrices vs alternatives
├── LICENSE.md                      ← The Unlicense (OFL carve-out for Montserrat)
├── llms.txt                        ← https://llmstxt.org/ index for LLM consumers
├── assets/logo.png                 ← project logo (used in this README)
├── .gitignore
└── front/                          ← skill folder; drop into ~/.claude/skills/
    ├── SKILL.md
    ├── references/
    │   ├── color-psychology.md
    │   ├── stack-vanilla-js.md
    │   ├── stack-tailwind.md
    │   ├── checklist.md
    │   ├── charts-vega.md / dataviz-*.md / dashboard-ergonomics.md
    │   ├── meta-tags.md / site-indexes.md / i18n.md
    │   ├── alt-text-ai.md / captions-ai.md / plain-language.md
    │   ├── contrast-audit.md / cvd-simulation.md / lint-a11y.md
    │   ├── anti-patterns.md / ergonomics-criteria.md / ux-psychology.md / material-design.md
    │   └── ui-guidelines/
    │       ├── INDEX.md
    │       ├── foundations/        ← color, typography, layout, motion, materials, a11y, …
    │       ├── components/         ← buttons, alerts, sheets, navigation, fields, …
    │       ├── patterns/           ← modality, feedback, loading, settings, …
    │       ├── inputs/             ← keyboard, pointer, touch, focus
    │       └── platforms/          ← mobile, tablet, desktop, wearable, tv, spatial
    ├── scripts/                    ← Python helpers (3.9+, cross-platform)
    │   ├── validate.py / lint_a11y.py / audit_contrast.py / site_indexes.py   (stdlib only)
    │   ├── favicons.py / meta_from_ollama.py
    │   ├── alt_from_ollama.py / install_alt_ai.py / simulate_cvd.py / plain_language.py
    │   ├── install_captions.py / captions_from_whisper.py
    │   └── requirements*.txt        ← one per feature (alt-text, captions, cvd, favicons, …)
    └── assets/
        ├── starter-page.html       ← single-file bootstrap (Tailwind Play CDN)
        ├── components/             ← copy-paste HTML snippets + Vega-Lite chart specs
        ├── examples/cli-gui-demo/  ← runnable CLI → GUI worked example
        └── fonts/montserrat/       ← variable + 4 static WOFF2, OFL.txt, fonts.css
```

## Author

[Warith Harchaoui, Ph.D.](https://www.linkedin.com/in/warith-harchaoui/) 

A Claude **skill** for a single frontend stack: vanilla JavaScript, Tailwind CSS, Montserrat. Built to the [Anthropic skill specification](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf).

Special thanks to **[Audrey Dejoux](https://www.behance.net/dreyadesign/projects)**, **[Laurent Pantanacce](https://www.linkedin.com/in/pantanacce/)**, and **[Jérôme Gombert](https://www.linkedin.com/in/j%C3%A9r%C3%B4me-gombert-84675b1b/)** for fruitful discussions.

Color palettes from <https://harchaoui.org/warith/colors/>.

Montserrat font is bundled in `front/assets/fonts/montserrat/` under the SIL Open Font License — see the bundled `OFL.txt` for the full license and the attached copyright notice.

We also drew on the [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) and [Google Material Design](https://material.io/design).

## License

**The Unlicense** — released into the public domain, no copyright, no restrictions. Use, modify, redistribute, sell — without permission, attribution, or fee. See `LICENSE.md` for the canonical text. The bundled Montserrat font remains under the SIL Open Font License (`front/assets/fonts/montserrat/OFL.txt`); the public-domain dedication doesn't change that.