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

## Who this is for

`front` is targeted at four concrete audiences. Each row is a stand-alone
pitch — if any one of them matches you, the matching skill earns its
keep on its own.

1. **Solo devs without a designer.** Opinionated defaults so you stop
   bikeshedding tokens — install `front-ui` and ship a usable UI from
   the first commit. Tailwind tokens, dark-mode peers, focus rings, hit
   areas, the lot.
2. **Pentesters writing internal dashboards.** Single-file HTML output
   that drops onto an internal box with no build chain. The a11y gates
   (`front-a11y`) run in CI without a browser, so even one-off recon
   tooling stays legible to teammates with assistive tech.
3. **Data scientists wrapping CLIs.** Point `front-cli-gui` at your
   `--help` — argparse, Click, Typer, clap, commander, cobra all
   introspect cleanly — and get a working GUI mock-up. No Gradio
   runtime, no React lock-in.
4. **Bilingual docs sites (EN/FR by default; pair is configurable).**
   `front-publish` keeps typography and tone in lock-step across two
   languages, drafts meta tags + favicons + sitemap in one pass. Change
   the pair (EN/DE, EN/JA, EN/ES, …) by editing one config token — see
   each `SKILL.md` → "Changing the language pair".

This is **not** the right pick for:

- Consumer-app brand work that needs a custom visual identity.
- Marketing landing pages where a tool like Webflow or Framer is faster.
- Apps where the team has chosen React / Vue / Svelte — use shadcn / Headless UI / Mantine instead.
- Versioned docs sites with hundreds of pages — pick MkDocs Material, Hugo, or Astro.

For alternatives in every category — and how to decide whether `front`
is the right pick — see [LANDSCAPE.md](LANDSCAPE.md). For real sites
already shipped on the stack, see [GALLERY.md](GALLERY.md).

## What the skills enforce

- Output uses vanilla JS (ES modules, native `<dialog>`, custom elements when justified). No React, Vue, Svelte, Next.js, Nuxt, Angular, Solid.
- Output uses Tailwind utility classes with semantic tokens (`bg-brand-blue`, `text-label-primary`). No raw hex literals in markup.
- Output uses **Montserrat** by default for marketing / prose surfaces, or **Inter** for dense developer / dashboard / data UI. If Montserrat is not the right call for your project (brand mismatch, language coverage, custom identity), drop a self-hosted family under `front-ui/assets/fonts/<family>/` (TTF or WOFF2 + license) and `front-ui` will swap to it. Every family is self-hosted (no Google Fonts CDN in production).
- Output sets a `dark:` peer on every styled element, uses `<button>`/`<a>`/`<label>`/`<dialog>`/`<form>` first, exposes a visible focus ring, honors `prefers-reduced-motion` and meets a 44×44 px hit area.
- Color choices map to the palettes in `front-ui/references/color-psychology.md` (source: <https://harchaoui.org/warith/colors/>).
- Skill output is **prototype-grade single-file HTML** by default — suitable for demos, mockups, internal tools and small landing pages. The starter page uses the Tailwind Play CDN, which Tailwind itself warns is for prototyping only. For production sites at scale, run **Tailwind CLI** or **Vite + Tailwind** over the emitted HTML before shipping; the class names are stable, so the same files survive the swap. See `front-ui/references/stack-tailwind.md`.
- Bilingual-ready copy (EN/FR by default — configurable via `lang_pair`). Default English; switch on the user's language. Set the project-level pair in any skill's `metadata.lang_pair` frontmatter token (EN/FR, EN/DE, EN/ES, EN/JA, …) — see each `SKILL.md` → "Changing the language pair" and `front-publish/references/i18n.md`. For an ad-hoc shell override use the `FRONT_LANG_PAIR` env var (e.g. `export FRONT_LANG_PAIR="en,fr"`); its first comma-split entry becomes the default `--lang` for the Ollama-backed scripts when no flag is passed.

## Status

A snapshot of where each surface stands at `v0.4.0`. The four skill folders are stable; the only WiP area is **audio captions**.

| Area | Status | Notes |
|---|---|---|
| `front-ui` (stack rules, tokens, components, dataviz, checklist) | Stable | All 9 hard rules documented; `validate.py` stdlib-only; covered by `tests/test_validate.py`. |
| `front-cli` (unified `front` driver, shell completion) | Stable | Click-based; leaf-command `--help` forwarding fixed in 0.3.0 (regression test in 0.3.1). |
| `front-cli-gui` (CLI → GUI flagship) | Stable (skill + runnable demo) | `assets/examples/cli-gui-demo/` runs end-to-end. Production hardening (auth, rate-limit, sandbox) deliberately left to the host. |
| `front-publish` (Markdown site, meta tags, favicons, indexes, plain language) | Stable | 4 scripts, 18 deterministic tests, eval suite for meta + plain-language. `FRONT_LANG_PAIR` runtime override wired. |
| `front-a11y` — lint, contrast, CVD, alt text | Stable | 14-rule lint, OKLCH contrast fixer, Machado CVD, Wikipedia-fixture alt-text eval. MLX vision-capability auto-detection added in 0.3.1. |
| `front-a11y` — **captions / transcripts** | **WiP / TODO** | `captions_from_whisper.py` is functional; what's missing is per-language WER baselines (`en` / `fr` / `es` extractor wired but baselines not yet published) and the user-supplied `vocab-biasing-clip.wav`. See [Roadmap](CHANGELOG.md#roadmap). |
| `LISEZMOI.md` (French README) | Stale | Not yet brought to parity with this README after 0.2.0+. Translation pass scheduled — see [Roadmap](CHANGELOG.md#roadmap). |

For the per-release detail (and what's planned next), see [`CHANGELOG.md`](CHANGELOG.md).

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
| An audio or video file (`.mp4`, `.wav`, `.mp3`, …) — **WiP** | "Captions / transcript" | `front-a11y` *(work in progress)* | WebVTT / SRT / plain-text captions from local whisper.cpp, with project-vocab biasing. `<video>` + `<track kind="captions">` snippet. Script + tests ship today; per-language WER baselines and the vocab-biasing reference clip are still being collected — see [Status](#status). |
| A logo (`logo.png` / `.svg`) | "Favicon set" / "PWA icons" | `front-publish` | `favicon.svg` + `.ico` + PNG set + `apple-touch-icon.png` + maskable PWA icon + `site.webmanifest` + a `head.html` snippet. |
| A goal description or an HTML page | "Meta tags" / "SEO" / "OG card" | `front-publish` | Title + description + Open Graph + Twitter Card + Schema.org JSON-LD. JSON on stdout. |
| Draft UI copy | "Plain language" / "Rewrite at grade 8" | `front-publish` | Same meaning, marketing voice stripped, output length ≤ 1.1× original. |
| A palette JSON | "Contrast audit" / "Is my palette accessible?" | `front-a11y` | Every `(label, surface)` pair walked, failures listed with the nearest OKLCH-neighbour fix. Exit 1 on any failure. |
| A finished page / screenshot | "Pre-ship check" | `front-ui` + `front-a11y` | The `checklist.md` gate executed; lint + contrast + CVD passes; copy / motion / performance verified. |

> Not sure which row you're on? Describe the input in plain English. Each skill's `SKILL.md` decision tree maps phrasing → workflow.

## Install

The skills follow the [Anthropic skill specification](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) and are read natively by **Claude Code** and **OpenCode**. Install only the ones you need.

### Claude Code

Install from a tagged GitHub release. This pins a version, verifies the
checksum, and gives you a stable rule-set that won't drift under you
between updates.

```bash
# 1. Download a tagged release
VERSION=0.4.0
curl -L -o front-skills.tar.gz \
    https://github.com/warith-harchaoui/front/releases/download/v${VERSION}/front-skills-${VERSION}.tar.gz
curl -L -o SHA256SUMS \
    https://github.com/warith-harchaoui/front/releases/download/v${VERSION}/SHA256SUMS

# 2. Verify checksum (macOS: shasum; Linux: sha256sum)
shasum -a 256 -c SHA256SUMS    # or: sha256sum -c SHA256SUMS

# 3. Extract and install the ones you need
tar xzf front-skills.tar.gz
mkdir -p ~/.claude/skills
cp -r front-ui      ~/.claude/skills/   # always
cp -r front-cli-gui ~/.claude/skills/   # only if you wrap CLIs
cp -r front-publish ~/.claude/skills/   # only if you ship docs sites
cp -r front-a11y    ~/.claude/skills/   # only if you need a11y gates
```

Verify:

```bash
ls ~/.claude/skills/front-ui/SKILL.md
```

If you only need a single skill, download its per-skill tarball instead
of the bundle (e.g. `front-a11y-${VERSION}.tar.gz`). Each release also
ships per-skill tarballs alongside the bundle and the same `SHA256SUMS`
covers all of them.

Claude Code reads each skill's frontmatter description and applies it
when a user message matches its trigger phrases.

### OpenCode

[OpenCode](https://opencode.ai) is an open-source terminal coding agent
that supports Claude, GPT and local models behind the same UX. The
release-based flow above works the same — extract the bundle, then:

```bash
mkdir -p ~/.opencode/skills
cp -r front-* ~/.opencode/skills/
```

Use OpenCode when you want skill behavior without provider lock-in, or
when you're already running OpenCode as your daily driver.

### Upgrading

To upgrade, repeat the steps with a newer `VERSION`. The on-disk
skill folder name is stable, so `cp -r front-ui ~/.claude/skills/`
overwrites the previous install in place. The `SHA256SUMS` for each
release is the source of truth — if the checksum check fails, do not
install the artifact.

### Shell completion

The `front` driver (and the four Click-migrated per-script CLIs —
`alt_from_ollama.py`, `captions_from_whisper.py`, `meta_from_ollama.py`,
`plain_language.py`) ship `bash` / `zsh` / `fish` completion for free
via Click's `_<TOOL>_COMPLETE=<shell>_source` trick. See
[`front-cli/README.md`](front-cli/README.md#shell-completion) for the
one-line setup per shell. The same env-var pattern works for any of
the per-script CLIs invoked directly (e.g.
`_ALT_FROM_OLLAMA_COMPLETE=zsh_source alt_from_ollama.py`).

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

**License vs. attribution.** Code is released under the Unlicense
(public domain — no permission needed to use, fork, modify, or rebrand).
Author credits in the docs are voluntary acknowledgement, not a license
requirement. You are free to remove or replace them in your fork.
