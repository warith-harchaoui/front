# Front

[🇫🇷](LISEZMOI.md) · [🇬🇧](README.md)

<p align="center">
  <img src="assets/logo.png" alt="Front — four Claude / OpenCode skills for vanilla JS + Tailwind frontends" width="240">
</p>

## What this is

`front` is **four small Claude / OpenCode skills** that constrain the agent to
one frontend stack — vanilla JavaScript, Tailwind CSS, Montserrat or Inter —
and a curated design system. Asking the agent to "build a UI", "wrap this
CLI in a GUI", "turn these markdown files into a website" or "audit this for
a11y" routes to the right skill and produces output in the same stack:
semantic HTML, dark-mode peers on every styled element, focus rings,
reduced-motion guards, charts via Vega-Lite, alt text drafted to W3C / WAI
guidance.

The four skills:

| Skill | When to install | Trigger phrases |
|---|---|---|
| **front-ui** | Always — it owns the stack rules and tokens. | "build a UI", "create a component", "design a page", "make a form / modal / button / nav", "dashboard", "audit this UI". |
| **front-cli-gui** | You wrap CLI tools in web UIs. | "wrap this CLI in a GUI", "build a UI for my Python script", "argparse to web UI". |
| **front-publish** | You ship docs sites, landing pages, meta-tags, favicons. | "turn these markdown files into a website", "meta tags", "favicons", "robots.txt", "sitemap", "llms.txt", "Atom feed", "plain language", "rewrite at grade 8". |
| **front-a11y** | You need accessibility audits and content (alt text, captions). | "a11y lint", "WCAG check", "contrast audit", "alt text", "describe this image", "captions", "transcript", "colorblind preview". |

The companion skills inherit the front-ui stack rules. Install only the
ones you need.

## Audience

Solo developers and small teams (≤ 5 people) shipping **internal tools** —
dev dashboards, admin panels, ML / data-science demo apps, CLI wrappers,
research showcases, docs sites for small projects. You don't have a
designer, you don't want to fight a framework, and you want output that
looks deliberate and survives a year without React-version churn.

This is **not** the right pick for:

- Consumer-app brand work that needs a custom visual identity.
- Marketing landing pages where a tool like Webflow or Framer is faster.
- Apps where the team has chosen React / Vue / Svelte — use shadcn / Headless UI / Mantine instead.
- Versioned docs sites with hundreds of pages — pick MkDocs Material, Hugo, or Astro.

For alternatives in every category — and how to decide whether `front` is the right pick — see [LANDSCAPE.md](LANDSCAPE.md).

## What the skills enforce

- Output uses vanilla JS (ES modules, native `<dialog>`, custom elements when justified). No React, Vue, Svelte, Next.js, Nuxt, Angular, Solid.
- Output uses Tailwind utility classes with semantic tokens (`bg-brand-blue`, `text-label-primary`). No raw hex literals in markup.
- Output uses **Montserrat** by default for marketing / prose surfaces, or **Inter** for dense developer / dashboard / data UI. Two choices, no more. Both are self-hosted.
- Output sets a `dark:` peer on every styled element, uses `<button>`/`<a>`/`<label>`/`<dialog>`/`<form>` first, exposes a visible focus ring, honors `prefers-reduced-motion` and meets a 44×44 px hit area.
- Color choices map to the palettes in `front-ui/references/color-psychology.md` (source: <https://harchaoui.org/warith/colors/>).
- Tailwind has a build step. The starter page uses the Play CDN, which is for prototyping only — see `front-ui/references/stack-tailwind.md` for the production swap (Tailwind CLI or Vite).
- Bilingual-ready copy. Default English; switch on the user's language. The language pair is configurable per project (EN/FR, EN/DE, EN/ES, EN/JA, …) — see `front-publish/references/i18n.md`.

## Inputs → outputs

What you give the agent and what comes back. Each row is a self-contained flow — pick one, ignore the rest.

| You provide | Phrase | Skill | Output |
|---|---|---|---|
| A working CLI (`tool --help`, source with `argparse` / `click` / `clap` / `commander` / `cobra`) | "Wrap this CLI in a GUI" + the project path | `front-cli-gui` | One-page `index.html` + `app.js` + Tailwind CSS, sub-commands mapped to forms / streams / tables, wired to your host (Tauri / Electron / FastAPI / Express / browser stub). Self-hosted Inter. |
| A folder of Markdown files (README, `docs/**`, blog posts) | "Turn these markdown files into a website" | `front-publish` | Static site: one HTML page per `.md`, sticky top bar, sidebar TOC for `docs/`, dark-mode peer, favicons, `<meta>` tags, `robots.txt` + `sitemap.xml` + `llms.txt` + Atom feed. |
| A free-form ask ("primary button", "confirm dialog", "settings page") | "Build a `<component>`" | `front-ui` | Semantic HTML + Tailwind + minimal vanilla JS, focus ring, `dark:` peer, 44×44 hit area, `Escape` close on dialogs, reduced-motion guard. |
| A data shape (CSV, JSON, a few rows) | "Chart this" / "Dashboard for X" | `front-ui` | Vega-Lite v5 JSON spec + `<figure>` wrapper. House style, palette from `color-psychology.md`, polarity-tagged axes, `role="img"`. |
| An existing HTML page or screenshot | "Audit this" / "WCAG check" / "Make it look less AI" | `front-ui` (anti-patterns, ergonomics) + `front-a11y` (lint, contrast, CVD) | Findings against the 8 ergonomic criteria + anti-patterns catalogue; concrete diffs; pre-ship checklist run; `lint_a11y` + `audit_contrast` + `simulate_cvd` output. |
| An image file (`*.png`, `*.jpg`, …) | "Alt text for this image" | `front-a11y` | W3C-compliant alt text for the right purpose category (informative / decorative / functional / text / complex / group), in the page's language, tagged `data-alt-source="ai"`. |
| An audio or video file (`.mp4`, `.wav`, `.mp3`, …) | "Captions / transcript" | `front-a11y` | WebVTT / SRT / plain-text captions from local Whisper, with project-vocab biasing. `<video>` + `<track kind="captions">` snippet. |
| A logo (`logo.png` / `.svg`) | "Favicon set" / "PWA icons" | `front-publish` | `favicon.svg` + `.ico` + PNG set + `apple-touch-icon.png` + maskable PWA icon + `site.webmanifest` + a `head.html` snippet. |
| A goal description or an HTML page | "Meta tags" / "SEO" / "OG card" | `front-publish` | Title + description + Open Graph + Twitter Card + Schema.org JSON-LD. JSON on stdout. |
| Draft UI copy | "Plain language" / "Rewrite at grade 8" | `front-publish` | Same meaning, marketing voice stripped, output length ≤ 1.1× original. |
| A palette JSON | "Contrast audit" / "Is my palette accessible?" | `front-a11y` | Every `(label, surface)` pair walked, failures listed with the nearest OKLCH-neighbour fix. Exit 1 on any failure. |
| A finished page / screenshot | "Pre-ship check" | `front-ui` + `front-a11y` | The `checklist.md` gate executed; lint + contrast + CVD passes; copy / motion / performance verified. |

> Not sure which row you're on? Describe the input in plain English. Each skill's `SKILL.md` decision tree maps phrasing → workflow.

## Install

The skills follow the [Anthropic skill specification](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) and are read natively by **Claude Code** and **OpenCode**. Install only the ones you need.

### Claude Code

```bash
git clone https://github.com/warith-harchaoui/front.git
mkdir -p ~/.claude/skills

# Always:
cp -r front/front-ui      ~/.claude/skills/front-ui

# Pick what you need:
cp -r front/front-cli-gui ~/.claude/skills/front-cli-gui
cp -r front/front-publish ~/.claude/skills/front-publish
cp -r front/front-a11y    ~/.claude/skills/front-a11y
```

Verify:

```bash
ls ~/.claude/skills/front-ui/SKILL.md
```

Claude Code reads each skill's frontmatter description and applies it when a user message matches its trigger phrases.

### OpenCode

[OpenCode](https://opencode.ai) is an open-source terminal coding agent that supports Claude, GPT and local models behind the same UX.

```bash
mkdir -p ~/.opencode/skills
cp -r front/front-* ~/.opencode/skills/
```

Use OpenCode when you want skill behavior without provider lock-in, or when you're already running OpenCode as your daily driver.

## CLI → GUI flagship

The `front-cli-gui` skill takes an existing CLI and produces a single-page vanilla-JS + Tailwind GUI for it. It reads the argument parser, categorizes each command (one-shot / form / streaming / list), maps flags to form controls, and wires execution to the project's host (Tauri, Electron, FastAPI, Express, or a stdlib HTTP+SSE proxy).

A runnable worked example ships in `front-cli-gui/assets/examples/cli-gui-demo/`. Launch:

```bash
cd front-cli-gui/assets/examples/cli-gui-demo
python server.py  # stdlib only, opens http://localhost:8787
```

For an honest comparison against Gradio / Streamlit / Tauri / Taipy, see `front-cli-gui/SKILL.md` → "Why this skill, not Gradio / Streamlit / Tauri / Taipy" and [LANDSCAPE.md](LANDSCAPE.md) § 7.

## Repository structure

```text
front/                                  ← repo root
├── README.md / LISEZMOI.md             ← EN / FR
├── LANDSCAPE.md                        ← comparison matrices vs alternatives
├── CHANGELOG.md                        ← release notes
├── CONTRIBUTING.md                     ← how to propose changes
├── LICENSE.md                          ← The Unlicense (OFL carve-out for Montserrat + Inter)
├── llms.txt                            ← https://llmstxt.org/ index for LLM consumers
├── pytest.ini, requirements-dev.txt    ← shared dev tooling
├── tests/                              ← shared pytest suite covers all four skills
├── assets/logo.png                     ← project logo
│
├── front-ui/                           ← UI generation skill
│   ├── SKILL.md
│   ├── references/                     ← color, stack, components, dataviz, design system, checklist
│   ├── scripts/                        ← validate.py (stdlib only)
│   └── assets/                         ← starter-page, components, Montserrat + Inter fonts
│
├── front-cli-gui/                      ← CLI → GUI skill (flagship)
│   ├── SKILL.md
│   ├── references/cli-gui-workflow.md
│   └── assets/examples/cli-gui-demo/   ← runnable worked example
│
├── front-publish/                      ← Markdown → website + meta + favicons + indexes + plain language
│   ├── SKILL.md
│   ├── references/                     ← meta-tags, site-indexes, plain-language, i18n
│   └── scripts/                        ← favicons.py, meta_from_ollama.py, site_indexes.py, plain_language.py
│
└── front-a11y/                         ← Accessibility audits + content tooling
    ├── SKILL.md
    ├── references/                     ← lint-a11y, contrast-audit, cvd-simulation, alt-text-ai, captions-ai
    └── scripts/                        ← lint_a11y.py, audit_contrast.py, simulate_cvd.py, alt_from_ollama.py, install_alt_ai.py, captions_from_whisper.py, install_captions.py
```

## Author

[Warith Harchaoui, Ph.D.](https://www.linkedin.com/in/warith-harchaoui/)

Four small Claude / OpenCode **skills** for a single frontend stack: vanilla JavaScript, Tailwind CSS, Montserrat or Inter. Built to the [Anthropic skill specification](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf).

Special thanks to **[Audrey Dejoux](https://www.behance.net/dreyadesign/projects)**, **[Laurent Pantanacce](https://www.linkedin.com/in/pantanacce/)** and **[Jérôme Gombert](https://www.linkedin.com/in/j%C3%A9r%C3%B4me-gombert-84675b1b/)** for fruitful discussions.

Color palettes from <https://harchaoui.org/warith/colors/>.

The Montserrat font is bundled in `front-ui/assets/fonts/montserrat/` under the SIL Open Font License — see the bundled `OFL.txt`. Inter is referenced from [rsms.me/inter](https://rsms.me/inter/) (OFL); download the WOFF2 file separately for self-host.

We also drew on the [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) and [Google Material Design](https://material.io/design).

## License

**The Unlicense** — released into the public domain, no copyright, no restrictions. Use, modify, redistribute, sell — without permission, attribution, or fee. See `LICENSE.md` for the canonical text. The bundled Montserrat font remains under the SIL Open Font License (`front-ui/assets/fonts/montserrat/OFL.txt`); the public-domain dedication doesn't change that.
