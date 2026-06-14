# Front

[🇫🇷](LISEZMOI.md) · [🇬🇧](README.md)

## What this is

`front` is a Claude skill that constrains Claude to a single, consistent frontend stack — vanilla JavaScript, Tailwind CSS, and Montserrat as the only typeface — and gives it a curated design system to draw from. Asking Claude to "build a UI", "create a component", "design a dashboard", or "wrap this CLI in a GUI" produces output in this exact stack with a repeatable point of view: semantic HTML, dark-mode peers on every styled element, focus rings, reduced-motion guards, color choices traceable to a documented psychology, charts via Vega-Lite, alt text drafted to W3C / WAI guidance.

## What it's for

Most LLM-generated frontends share a generic look — purple gradients, glassmorphic cards, marketing buzzwords, three-card hero grids — because the model defaults to its most-common training patterns. This skill replaces those defaults with one stack, one font, one color philosophy, one set of ergonomic criteria. The result is frontend output that's consistent across sessions, free of "AI-generated" tells, and ready to ship in any project that wants this stack.

The flagship use case is **CLI → GUI**: point Claude at an existing command-line tool's `--help`, and the skill produces the matching vanilla-JS + Tailwind GUI in one session. Other use cases: new components, full pages, ergonomic audits, dashboards and dataviz, migrations away from a framework toward vanilla JS, and accessibility tooling (W3C-grade alt text, meta tags, favicon set, validator).

## Contents

- `front/SKILL.md` — entry point with YAML frontmatter and instructions.
- `front/references/` — progressive-disclosure reference files (color, stack, checklist, UI guidelines, dataviz, meta tags, i18n, anti-patterns, UX psychology, Material Design, alt text).
- `front/assets/` — copy-paste templates and Montserrat font files.
- `front/scripts/` — Python helpers (`validate.py`, `install_alt_ai.py`, `alt_from_ollama.py`, `meta_from_ollama.py`, `favicons.py`) with `requirements.txt`.
- `llms.txt` — index of the project per <https://llmstxt.org/> for LLM consumers.

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
├── .gitignore
└── front/                          ← skill folder; drop into ~/.claude/skills/
    ├── SKILL.md
    ├── references/
    │   ├── color-psychology.md
    │   ├── stack-vanilla-js.md
    │   ├── stack-tailwind.md
    │   ├── checklist.md
    │   └── ui-guidelines/
    │       ├── INDEX.md
    │       ├── foundations/        ← color, typography, layout, motion, materials, a11y, …
    │       ├── components/         ← buttons, alerts, sheets, navigation, fields, …
    │       ├── patterns/           ← modality, feedback, loading, settings, …
    │       ├── inputs/             ← keyboard, pointer, touch, focus
    │       └── platforms/          ← mobile, tablet, desktop, wearable, tv, spatial
    └── assets/
        ├── starter-page.html       ← single-file bootstrap (Tailwind Play CDN)
        ├── components/             ← copy-paste HTML snippets
        └── fonts/montserrat/       ← variable + 4 static WOFF2, OFL.txt, fonts.css
```

## Author

[Warith Harchaoui, Ph.D.](https://www.linkedin.com/in/warith-harchaoui/) 

A Claude **skill** for a single frontend stack: vanilla JavaScript, Tailwind CSS, Montserrat. Built to the [Anthropic skill specification](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf).

Special thanks to **[Audrey Dejoux](https://www.behance.net/dreyadesign/projects)**, **[Laurent Pantanacce](https://www.linkedin.com/in/pantanacce/)**, and **[Jérôme Gombert](https://www.linkedin.com/in/j%C3%A9r%C3%B4me-gombert-84675b1b/)** for fruitful discussions.

Color palettes from <https://harchaoui.org/warith/colors/>.

Montserrat font is bundled in `front/assets/fonts/montserrat/` under the SIL Open Font License — see the bundled `OFL.txt` for the full license and the attached copyright notice.

We also got some knowledge from [Apple  Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) and [Google Material Design](https://material.io/design).

## License

**The Unlicense** — released into the public domain, no copyright, no restrictions. Use, modify, redistribute, sell — without permission, attribution, or fee. See `LICENSE.md` for the canonical text. The bundled Montserrat font remains under the SIL Open Font License (`front/assets/fonts/montserrat/OFL.txt`); the public-domain dedication doesn't change that.