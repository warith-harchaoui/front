# Front

[🇫🇷](LISEZMOI.md) · [🇬🇧](README.md)

<p align="center">
  <img src="assets/logo.png" alt="Front — nine Claude / OpenCode skills for vanilla JS + Tailwind frontends" width="240">
</p>

## What this is

`front` made of several **Claude / OpenCode skills** with a curated design
system for a frontend stack voering a large spectrum from choice of colors to accessibility, UX, audio, vision, CLI to GUI etc.

The skills:

| Skill | When to install | Trigger phrases |
|---|---|---|
| **front-ui** | Always — it owns the stack rules and tokens. | "build a UI", "create a component", "design a page", "make a form / modal / button / nav", "dashboard", "audit this UI". |
| **front-cli-gui** | You wrap CLI tools in web UIs. | "wrap this CLI in a GUI", "build a UI for my Python script", "argparse to web UI". |
| **front-publish** | You ship docs sites, landing pages, meta-tags, favicons. | "turn these markdown files into a website", "meta tags", "favicons", "robots.txt", "sitemap", "llms.txt", "Atom feed", "plain language", "rewrite at grade 8". |
| **front-accessibility** | You need static HTML a11y lint. | "a11y lint", "check this HTML for accessibility", "static a11y check", "WCAG-friendly lint", "a11y pre-commit". |
| **front-colors** | You audit contrast, simulate color blindness, or want a curated palette with perceptual lighten / darken. | "WCAG check", "contrast audit", "is my palette accessible", "colorblind preview", "deuteranope", "CVD", "OKLCH", "lighten this color". |
| **front-vision** | You draft W3C-compliant alt text from images locally (no SaaS). | "alt text", "alt text for this image", "describe this image", "draft alt", "image description", "img has no alt". |
| **front-audio** | You draft WebVTT / SRT captions for `<video>` / `<audio>` locally (no SaaS). | "captions", "transcribe video", "transcribe audio", "WebVTT", "SRT", "subtitle file", "VTT", "caption track". |
| **front-ux-laws** | You want a shared vocabulary for UI decisions AND a pre-commit auditor that fails on detectable Laws-of-UX violations (Hick, Fitts, Miller, Jakob, Tesler, Aesthetic-Usability, Selective Attention, Doherty, Choice Overload). | "Laws of UX", "Hick / Fitts / Miller / Jakob / Tesler / Peak-End / Postel / Paradox of the Active User", "audit my nav / form / pricing page", "is this onboarding fighting the active user". |
| **front-figures** | You emit data-science figures (**Vega-Lite first** — matplotlib only as an escape hatch), model-explainability plots (SHAP / Shapash / TimeSHAP / LIME), causal-effect estimates (DoWhy / EconML), or TikZ / Mermaid diagrams — refined through the **Ralph Eyeball Loop** (render → look → refine the source), with a pre-commit auditor for data-viz sins. | "make a figure", "prefer vega", "render this diagram", "tikz to png", "mermaid diagram", "ralph eyeball loop", "no ascii art", "SHAP plot", "explain this model", "causal inference", "DoWhy", "DAG", "audit this figure". |

The companion skills inherit the front-ui stack rules. Install only the
ones you need.

> **What prompt activates what?** See [`TRIGGERS.md`](TRIGGERS.md) —
> generated from every `SKILL.md` description, lists every guaranteed
> trigger phrase against the skill it invokes.

## Features — what's unusual for a Claude skill

Most Claude skills — including Anthropic's own `document-skills` (docx, pdf,
pptx, xlsx) and `example-skills` (artifacts, GIFs, MCP servers, design) — are
**make-only**: the model produces an artifact. `front` is built differently, and
these traits set it apart:

- **Make *and* audit.** Every skill pairs generation with a **deterministic
  auditor** that exits non-zero on findings — six of them (`lint_a11y`,
  `audit_contrast`, `audit_laws_of_ux`, `audit_figure`, `audit_i18n`,
  `lint_markdown`). No official Anthropic skill ships a static lint gate as its
  purpose; here it's half the design.
- **CI / pre-commit gates, not vibes.** The auditors emit JSON + exit codes and
  ship as a [`.pre-commit-hooks.yaml`](.pre-commit-hooks.yaml) manifest — one
  `repo:` block and they block commits, whoever (or whatever) wrote the code.
- **Local-first AI, zero SaaS egress.** Alt text runs on a local Ollama vision
  model; captions / diarization on a local whisper.cpp build. Nothing leaves the
  machine — the official skills are cloud-Claude-first.
- **Deterministic generators.** palette → Tailwind config, CLI → GUI, favicon /
  PWA-icon sets, sitemaps / feeds, and `locales/i18n.yaml` — reproducible
  artifacts a model would not derive byte-for-byte.
- **Hardened like a product, not a demo.** A real pytest suite + an AI-eval
  layer (DeepEval), CI across Python 3.10–3.12, checksum-verified per-skill
  release tarballs, and a spec-conformance validator — vs demonstration-grade
  examples.
- **Runtime-portable.** One skill folder serves both **Claude Code** and
  **OpenCode**; the AI paths target local models so a smaller OpenCode model
  follows a script instead of inventing one.
- **Unified i18n.** GUI strings *and* LLM prompts live in a single
  `locales/i18n.yaml`, enforced on both the make and audit sides.

## Two modes — make and audit

Every front-* skill belongs to one or both halves of a single loop:
**make** the artifact, **audit** the artifact. The matrix tells you
when to load each skill and what is still on the roadmap.

| Skill | Make (generate) | Audit (gate) |
|---|---|---|
| **front-ui** | `references/` + `assets/components/` — generation playbook for HTML / Tailwind / dataviz | `scripts/validate.py`, `references/checklist.md`, `anti-patterns.md`, `ergonomics-criteria.md` |
| **front-cli-gui** | `scripts/cli_to_gui.py` (CLI → HTML emitter — argparse + Click + `--from-help` adapters) + `assets/examples/cli-gui-demo/` (worked scaffold) | Pair with `front-accessibility` + `front-ux-laws` on the emitted HTML (the emitter is its own customer — its output passes both gates with zero findings). |
| **front-publish** | `favicons.py`, `meta_from_ollama.py`, `site_indexes.py`, `plain_language.py`, `md_to_html.py`, `narrate.py` | `lint_markdown.py` |
| **front-accessibility** | _(none — see `front-ui` templates, `front-vision` for alt text, `front-audio` for captions)_ | `lint_a11y.py` (14 rules, stdlib only) |
| **front-colors** | `palette_to_tailwind.py` (CSV → tailwind.config.js) | `audit_contrast.py`, `simulate_cvd.py` |
| **front-vision** | `alt_from_ollama.py` (W3C alt text via local Ollama) | _(presence of `alt=` checked by `front-accessibility`)_ |
| **front-audio** | `captions_from_whisper.py` (WebVTT / SRT via local whisper.cpp) | _(presence of `<track>` checked by `front-accessibility`)_ |
| **front-ux-laws** | `references/laws-of-ux.md` (30-law Markdown playbook) | `audit_laws_of_ux.py` (Hick / Miller / Fitts / Jakob / Tesler / …) |
| **front-figures** | `make_figure.py` (CSV → Vega / matplotlib), `explain_model.py` (SHAP / Shapash / TimeSHAP / LIME dispatcher), `causal_estimate.py` (DoWhy loop + EconML backends + DAG render), `render_diagram.py` (Vega / TikZ / Mermaid → PNG / SVG / PDF for the Ralph Eyeball Loop), `install_figures.py` (tier installer) | `audit_figure.py` (missing-axis-title, dual-y-axis, truncated-baseline, pie-3d, rainbow-palette, cvd-unsafe, missing-polarity, chartjunk, role-img-missing) |

The matrix is honest about gaps. Empty cells mark genuine roadmap
items, not omissions — see `.private/todo.md` (gitignored) for the
ranking.

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
   (`front-accessibility`) run in CI without a browser, so even one-off recon
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
already shipped on the stack, see [GALLERY.md](GALLERY.md). For copy-paste
recipes per skill (with expected output), see [`EXAMPLES.md`](EXAMPLES.md).

## What the skills enforce

- Output uses vanilla JS (ES modules, native `<dialog>`, custom elements when justified). No React, Vue, Svelte, Next.js, Nuxt, Angular, Solid.
- Output uses Tailwind utility classes with semantic tokens (`bg-brand-blue`, `text-label-primary`). No raw hex literals in markup.
- Output enforces the **three-Roboto rule**: exactly three downloaded webfonts, all from the Roboto super-family — **Roboto** (sans / UI / body), **Roboto Serif** (editorial / longform / prose-heavy landings), **Roboto Mono** (`<code>`, `<pre>`, terminal panels, log output). No other downloaded family is allowed (no Inter, no Montserrat, no IBM Plex, no JetBrains Mono). The three siblings share metrics and x-height by design — prose-heavy and code-heavy surfaces stay typographically coherent. All three are self-hosted (no Google Fonts CDN in production); WOFF2 + OFL live under `front-ui/assets/fonts/roboto/`, `…/roboto-serif/`, `…/roboto-mono/`.
- Output sets a `dark:` peer on every styled element, uses `<button>`/`<a>`/`<label>`/`<dialog>`/`<form>` first, exposes a visible focus ring, honors `prefers-reduced-motion` and meets a 44×44 px hit area.
- Output exposes a **🌞 Light / 🌚 Dark / 🌗 Auto toggle** (canonical placement: top-right of sticky header → footer far-right → fixed bottom-right anchor when there is no header). **Auto is the default** so a fresh visitor inherits their OS choice and is never surprised by a hard-coded scheme. Component: `front-ui/assets/components/theme-toggle.html`. Wiring: `front-ui/references/stack-vanilla-js.md` § "Theme switching".
- Color choices map to the palettes in `front-ui/references/color-psychology.md` (source: <https://harchaoui.org/warith/colors/>).
- Skill output is **prototype-grade single-file HTML** by default — suitable for demos, mockups, internal tools and small landing pages. The starter page uses the Tailwind Play CDN, which Tailwind itself warns is for prototyping only. For production sites at scale, run **Tailwind CLI** or **Vite + Tailwind** over the emitted HTML before shipping; the class names are stable, so the same files survive the swap. See `front-ui/references/stack-tailwind.md`.
- Bilingual-ready copy (EN/FR by default). The output language of the AI-backed scripts is **auto-detected from the input/context text** via `langdetect` — no configured default language; pass `--lang` to force one. For translatable UI strings and prompts, use one `locales/i18n.yaml` catalog (see `front-ui/scripts/i18n_make.py` and `front-publish/references/i18n.md`).
- **i18n lives in YAML, never in JS.** Translatable strings — GUI labels **and** LLM prompts — belong in a single per-project catalog, **`locales/i18n.yaml`** (message id → per-locale text), loaded at runtime; never a translation dict baked into JavaScript, never a prompt inlined in Python. GUI strings and prompts share `locales/i18n.yaml` because they share one concern — *language*. Prompts already ship this way (`prompts/*.yaml`, loaded via `_prompts.load_prompt`); the same rule governs generated GUIs, on both the **make** (scaffold + read `locales/i18n.yaml`) and **audit** (flag any GUI string or prompt living outside it — hardcoded in JS or inlined in Python) sides.

## Status

A snapshot of where each surface stands. The nine skill folders are stable; the only WiP area is **audio captions** (front-audio, video → text). The **audio narration** feature (front-publish, text → audio) is stable and clearly framed as optional editorial enhancement, not WCAG compliance.

| Area | Status | Notes |
|---|---|---|
| `front-ui` (stack rules, tokens, components, dataviz, checklist) | Stable | All 9 hard rules documented; `validate.py` stdlib-only; covered by `tests/test_validate.py`. |
| `front-cli` (unified `front` driver, shell completion) | Stable | Click-based; leaf-command `--help` forwarding fixed in 0.3.0 (regression test in 0.3.1). |
| `front-cli-gui` (CLI → GUI flagship) | Stable (skill + runnable demo) | `assets/examples/cli-gui-demo/` runs end-to-end. Production hardening (auth, rate-limit, sandbox) deliberately left to the host. |
| `front-publish` (Markdown site, meta tags, favicons, indexes, plain language, audio narration) | Stable | 11 public scripts spanning the four core artifacts (favicons, meta, indexes, plain-language) + Markdown → HTML + Markdown linter + the audio-narration pipeline (narrate orchestrator, OpenVoice and Chatterbox engine wrappers, voice picker, install helper). Broad deterministic test coverage (favicons, site-indexes, meta, plain-language, lint, narrate); eval suite for meta + plain-language. |
| `front-accessibility` — lint | Stable (renamed from `front-a11y` in 0.9.0) | 14-rule static a11y lint, stdlib only. Now narrowed to lint after the color / vision / audio splits. |
| `front-colors` — contrast audit, CVD simulation, curated palette, perceptual lighten / darken | Stable (new in 0.7.0) | OKLCH-neighbour contrast fixer, Machado CVD matrices, unified palette CSV (Apple base + emotion / concept / psychology projections), stdlib-only `_colors` module, `Color` class. Split out of `front-accessibility` for clearer scope. |
| `front-vision` — W3C alt text via local Ollama vision | Stable (new in 0.8.0) | Model `gemma3:4b` via Ollama (the one authorized LLM). Per-purpose decision tree, surrounding-text + vocabulary biasing, on-disk cache. Split out of `front-accessibility` for clearer scope. Wikipedia-fixture alt-text eval. |
| `front-audio` — **WebVTT / SRT captions via local whisper.cpp** | **WiP / TODO** (split out in 0.9.0) | `captions_from_whisper.py` is functional; what's missing is per-language WER baselines (`en` / `fr` / `es` extractor wired but baselines not yet published), the user-supplied `vocab-biasing-clip.wav`, and a planned `pdbms`-based revision of the whisper.cpp integration. See [Roadmap](CHANGELOG.md#roadmap). |
| `LISEZMOI.md` (French README) | Stable | At structural parity with this README — same section ordering, content kept in lock-step on every release. |

For the per-release detail (and what's planned next), see [`CHANGELOG.md`](CHANGELOG.md).

## Inputs → outputs

What you give the agent and what comes back. Each row is a self-contained flow — pick one, ignore the rest.

| You provide | Phrase | Skill | Output |
|---|---|---|---|
| A working CLI (`tool --help`, source with `argparse` / `click` / `clap` / `commander` / `cobra`) | "Wrap this CLI in a GUI" + the project path | `front-cli-gui` | One-page `index.html` + `app.js` + Tailwind CSS, sub-commands mapped to forms / streams / tables, wired to your host (Tauri / Electron / FastAPI / Express / browser stub). Self-hosted Roboto / Roboto Mono. |
| A folder of Markdown files (README, `docs/**`, blog posts) | "Turn these markdown files into a website" | `front-publish` | Static site: one HTML page per `.md`, sticky top bar, sidebar TOC for `docs/`, dark-mode peer, favicons, `<meta>` tags, `robots.txt` + `sitemap.xml` + `llms.txt` + Atom feed. |
| A free-form ask ("primary button", "confirm dialog", "settings page") | "Build a `<component>`" | `front-ui` | Semantic HTML + Tailwind + minimal vanilla JS, focus ring, `dark:` peer, 44×44 hit area, `Escape` close on dialogs, reduced-motion guard. |
| A data shape (CSV, JSON, a few rows) | "Chart this" / "Dashboard for X" | `front-ui` | Vega-Lite v5 JSON spec + `<figure>` wrapper. House style, palette from `color-psychology.md`, polarity-tagged axes, `role="img"`. |
| An existing HTML page or screenshot | "Audit this" / "WCAG check" / "Make it look less AI" | `front-ui` (anti-patterns, ergonomics) + `front-accessibility` (lint) + `front-colors` (contrast, CVD) | Findings against the 8 ergonomic criteria + anti-patterns catalogue; concrete diffs; pre-ship checklist run; `lint_a11y` + `audit_contrast` + `simulate_cvd` output. |
| An image file (`*.png`, `*.jpg`, …) | "Alt text for this image" | `front-vision` | W3C-compliant alt text for the right purpose category (informative / decorative / functional / text / complex / group), in the page's language, tagged `data-alt-source="ai"`. |
| An audio or video file (`.mp4`, `.wav`, `.mp3`, …) — **WiP** | "Captions / transcript" | `front-audio` *(work in progress)* | WebVTT / SRT / plain-text captions from local whisper.cpp, with project-vocab biasing. `<video>` + `<track kind="captions">` snippet. Script + tests ship today; per-language WER baselines and the vocab-biasing reference clip are still being collected — see [Status](#status). |
| A logo (`logo.png` / `.svg`) | "Favicon set" / "PWA icons" | `front-publish` | `favicon.svg` + `.ico` + PNG set + `apple-touch-icon.png` + maskable PWA icon + `site.webmanifest` + a `head.html` snippet. |
| A goal description or an HTML page | "Meta tags" / "SEO" / "OG card" / "GEO" / "llms.txt" / "AI Overview" | `front-publish` | **For SEO:** title + description + Open Graph + Twitter Card + Schema.org JSON-LD (JSON on stdout) — see [Google's three Search Essentials pillars](https://developers.google.com/search/docs/essentials) applied in `front-publish/references/seo-essentials.md`. **For GEO** (Generative Engine Optimization — AI Overview / Gemini / ChatGPT answer surfaces): `llms.txt` is emitted by `scripts/site_indexes.py` alongside `robots.txt` + `sitemap.xml` + Atom/RSS, so the site ships an LLM-readable Markdown summary the moment any "turn this into a website" run completes. Same crawlers, same `robots.txt` permissions — no separate "AI" meta tag exists; anything claiming one is wrong. |
| Draft UI copy | "Plain language" / "Rewrite at grade 8" | `front-publish` | Same meaning, marketing voice stripped, output length ≤ 1.1× original. |
| A palette JSON | "Contrast audit" / "Is my palette accessible?" | `front-colors` | Every `(label, surface)` pair walked, failures listed with the nearest OKLCH-neighbour fix. Exit 1 on any failure. |
| A finished page / screenshot | "Pre-ship check" | `front-ui` + `front-accessibility` + `front-colors` | The `checklist.md` gate executed; lint + contrast + CVD passes; copy / motion / performance verified. |

> Not sure which row you're on? Describe the input in plain English. Each skill's `SKILL.md` decision tree maps phrasing → workflow.

## Install

The skills follow the [Anthropic skill specification](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) and are read natively by **Claude Code** and **OpenCode**. Install only the ones you need.

The Claude Code and OpenCode flows are **identical except for the
install directory** — both runtimes read SKILL.md files from a
per-skill folder, and the same tarballs serve both. The instructions
below show one path; the second runtime is a one-line substitution.

> **Shared variables.** Replace `<RUNTIME>` with `claude` or
> `opencode` below. Pin `VERSION` to the latest tag — see
> [releases](https://github.com/warith-harchaoui/front/releases).

### 1. Download a tagged release (checksum-verified)

```bash
VERSION=0.15.1
curl -L -o front-skills.tar.gz \
    https://github.com/warith-harchaoui/front/releases/download/v${VERSION}/front-skills-${VERSION}.tar.gz
curl -L -o SHA256SUMS \
    https://github.com/warith-harchaoui/front/releases/download/v${VERSION}/SHA256SUMS

# macOS: shasum -a 256 -c SHA256SUMS
# Linux: sha256sum -c SHA256SUMS
shasum -a 256 -c SHA256SUMS

tar xzf front-skills.tar.gz
```

If you only need one skill, swap the bundle for a per-skill tarball
(e.g. `front-accessibility-${VERSION}.tar.gz`). The same `SHA256SUMS`
covers every artifact.

### 2. Copy into the runtime's skills directory

Pick **one** runtime block:

```bash
# Claude Code:
RUNTIME=claude   # → ~/.claude/skills/
# OpenCode:
RUNTIME=opencode # → ~/.opencode/skills/

mkdir -p ~/.${RUNTIME}/skills
cp -r front-ui            ~/.${RUNTIME}/skills/   # always
cp -r front-cli-gui       ~/.${RUNTIME}/skills/   # only if you wrap CLIs
cp -r front-publish       ~/.${RUNTIME}/skills/   # only if you ship docs sites
cp -r front-accessibility ~/.${RUNTIME}/skills/   # only if you need static a11y lint
cp -r front-colors        ~/.${RUNTIME}/skills/   # only if you need WCAG contrast / CVD / palette
cp -r front-vision        ~/.${RUNTIME}/skills/   # only if you need AI alt text (local Ollama)
cp -r front-audio         ~/.${RUNTIME}/skills/   # only if you need AI captions (local whisper.cpp)
cp -r front-ux-laws       ~/.${RUNTIME}/skills/   # only if you want the Laws-of-UX audit + reference
cp -r front-figures       ~/.${RUNTIME}/skills/   # only if you emit dataviz / SHAP / DoWhy figures
```

Install in **both** runtimes if you switch between them — the same
folder copied to two paths.

### 3. Verify

```bash
# A skill is installed and its SKILL.md is on disk:
ls ~/.${RUNTIME}/skills/front-ui/SKILL.md

# Optional — if you cloned the repo too, verify every installed skill
# against the Anthropic spec (stdlib + PyYAML, no network):
python3 scripts/validate_all.py
```

The runtime reads each skill's `SKILL.md` frontmatter description at
conversation start; matching prompts auto-trigger the skill. See
[`TRIGGERS.md`](TRIGGERS.md) for the per-phrase index.

### Cleanup — remove stale or renamed skills

If you installed an older version, your `~/.${RUNTIME}/skills/`
folder may carry orphan directories from past renames (e.g.
`front-a11y/` from before the v0.9.0 rename to `front-accessibility`).
Run the helper to detect + remove them:

```bash
# Audit only (lists orphan skill folders; never deletes):
python3 scripts/cleanup_local_skills.py

# Apply: prompts for confirmation per directory before removal.
python3 scripts/cleanup_local_skills.py --apply
```

It checks both `~/.claude/skills/` and `~/.opencode/skills/` against
the canonical `SKILLS.txt` manifest and flags any `front-*` folder
that no longer ships from this repo. Read [`SKILLS.txt`](SKILLS.txt)
for the canonical list.

### Upgrade

Repeat steps 1–3 with the new `VERSION`. The on-disk skill folder
name is stable so each `cp -r` overwrites in place — no manual
removal between versions, except when a skill is **renamed** (use
the cleanup helper above for those). Skill renames are listed in
[`CHANGELOG.md`](CHANGELOG.md).

### Install from source (contributor / developer path)

To iterate on the skills, or pin to a commit that has not been
tagged, clone and copy from the working tree. No checksum step —
you are responsible for verifying you cloned the commit you intended.

```bash
git clone https://github.com/warith-harchaoui/front.git
cd front
python3 -m pip install -r requirements-dev.txt   # PyYAML + pytest
python3 -m pytest                                # full deterministic suite
python3 scripts/validate_all.py                  # all 9 skills, YAML + content

# Mirrors step 2 above:
RUNTIME=claude   # or opencode
mkdir -p ~/.${RUNTIME}/skills
for skill in $(grep -v '^[[:space:]]*#' SKILLS.txt | grep -v '^[[:space:]]*$'); do
    cp -r "$skill" ~/.${RUNTIME}/skills/
done
```

`CONTRIBUTING.md` walks the same flow at the contributor level.

### OpenCode + local Ollama — the zero-token path

[OpenCode](https://opencode.ai) is the second supported runtime —
and the natural fit for an **all-local, no-tokens** workflow.
OpenCode is model-agnostic: point it at a local
[Ollama](https://ollama.com) daemon and you get the same skill
behaviour as Claude Code with two real differences:

- **No API tokens.** Nothing leaves your machine; nothing bills.
- **No usage limits.** Run the loop overnight on a long batch
  without watching a meter.

The trade-off is model quality. A 7-13 B local model is below
Claude / GPT-4 on hard reasoning; the front-* skills compensate
because they front-load the *opinion* (stack rules, audit checks,
trigger phrases) — the model mostly has to follow a script, not
invent it. For UI work, alt text, captions, contrast audits,
Laws-of-UX checks, the local path is genuinely usable today.

The fit with this repo is direct: **three front-* skills already
talk to a local Ollama daemon** for their AI surfaces — `front-vision`
(alt text, `gemma3:4b`), `front-publish/meta_from_ollama.py` (page
meta), `front-publish/plain_language.py` (copy rewrite). When you
run OpenCode against the same Ollama daemon, the whole loop —
agent + skill-driven scripts — uses one local model. Zero
external calls.

```bash
# Quick start. Assumes Ollama + an OpenCode binary on PATH.
ollama serve &         # start the daemon
ollama pull gemma3:4b  # the one model — agent loop AND every skill script
```

One model handles the whole stack: it drives the OpenCode agent
loop AND backs every front-* Ollama-backed script
(`alt_from_ollama`, `meta_from_ollama`, `plain_language`,
`narrate_post`). Same daemon, same tag, same answer for "which
model is in play" — `gemma3:4b`.

#### Wire OpenCode to the local Ollama daemon (one-time config)

OpenCode's bundled `ollama` provider points at Ollama Cloud by
default. To target your **local** daemon, add a `local-ollama`
provider to `~/.config/opencode/opencode.jsonc` (the file already
exists; only the `provider` key is new):

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "local-ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "gemma3:4b": { "name": "gemma3:4b (local)" }
      }
    }
  }
}
```

Ollama exposes an OpenAI-compatible endpoint at
`http://localhost:11434/v1`, which the `@ai-sdk/openai-compatible`
provider speaks natively — no plugin install needed beyond writing
the config. List exactly the model tags you have pulled (run
`ollama list` to see them); OpenCode will not auto-discover.

Then start OpenCode against the local provider:

```bash
opencode run "build me a primary CTA button" \
    -m local-ollama/gemma3:4b

# → ~/.opencode/skills/front-* load automatically per their frontmatter.
# → The front-vision / front-publish Ollama-backed scripts hit the
#   same daemon for their per-script work.
# → Cost: 0 tokens; nothing leaves the machine.
```

One model, `gemma3:4b`, backs both the agent loop and every
skill script — same daemon, same tag. `gemma3:4b` is multimodal, so
the vision script (alt text) works on the same model as the text
scripts. There is nothing else to pick.

#### Configure the skill scripts (same daemon, separate env vars)

OpenCode drives the agent; the skill scripts that *also* talk to
Ollama (alt text, meta tags, plain-language rewrites, audio
narration) read their own env vars. There is **no overlap with
`OPENCODE_MODEL`** — set both, both should agree on the daemon
URL, but the model tag can differ:

| Env var | Read by | What it does | Default |
|---|---|---|---|
| `OLLAMA_URL` | every Ollama-backed script | Daemon endpoint. Must match the URL OpenCode talks to. | `http://localhost:11434` |
| `OLLAMA_MODEL` | every Ollama-backed script | Bare escape hatch (mainly for tests). The one authorized model is `gemma3:4b`. | `gemma3:4b` |
| `OPENCODE_MODEL` | OpenCode itself | Agent-side model tag — set it to `gemma3:4b`. | `gemma3:4b` |

The pattern is deliberately boring: `gemma3:4b` on the same daemon
for both the agent and the scripts. `gemma3:4b` is multimodal, so the
vision script and the text scripts share it — no per-concern model
juggling, no MLX.

```bash
# One daemon, one model, for everything.
export OLLAMA_URL=http://localhost:11434
export OPENCODE_MODEL=gemma3:4b
```

Pick OpenCode when token costs matter, when the work is bulk /
repetitive (alt-text a 500-image library, regenerate meta tags on
every doc commit, audit a 50-page docs site), or when the data
must not leave the box. Pick Claude Code when the work needs
frontier-model judgement (novel design synthesis, ambiguous
refactors, code review of unfamiliar libraries).

### Trust model

Short version: the repo ships text and Python scripts you can read
top-to-bottom in under an hour. **Tagged releases carry SHA-256
checksums** (integrity-against-corruption); they are **not
GPG-signed** or Sigstore-attested today. If you need authenticity
beyond a transport-integrity check, build from a tagged commit you've
reviewed yourself — `scripts/release.sh` is in-tree and reproducible,
and the `release.yml` workflow does nothing the script can't do
locally. See [`SECURITY.md`](SECURITY.md) for the full supply-chain
note.

### Shell completion

The `front` driver (and the four Click-migrated per-script CLIs —
`alt_from_ollama.py`, `captions_from_whisper.py`, `meta_from_ollama.py`,
`plain_language.py`) ship `bash` / `zsh` / `fish` completion for free
via Click's `_<TOOL>_COMPLETE=<shell>_source` trick. See
[`front-cli/README.md`](front-cli/README.md#shell-completion) for the
one-line setup per shell. The same env-var pattern works for any of
the per-script CLIs invoked directly (e.g.
`_ALT_FROM_OLLAMA_COMPLETE=zsh_source alt_from_ollama.py`).

## Pre-commit hooks

The repo ships a `.pre-commit-hooks.yaml` manifest, so any project
can wire the front-* audit gates into [pre-commit](https://pre-commit.com/)
with a single `repo:` block — no manual script paths, no install
beyond `pre-commit install`.

```yaml
# .pre-commit-config.yaml — add the repo as one entry
repos:
  - repo: https://github.com/warith-harchaoui/front
    rev: v0.27.0          # pin a tag — bump with renovate / dependabot
    hooks:
      - id: front-accessibility-lint
      - id: front-ux-laws-audit
      - id: front-publish-lint-markdown
      - id: front-ui-validate-skill   # only if you ship skills yourself
      # Add --fix to any of the above as a hook arg to enable auto-repairs
      # e.g. - id: front-ux-laws-audit
      #        args: [--fix]
```

The hooks are stdlib-only on the Python side (pre-commit installs
each into its own isolated env). The two color hooks declare Pillow
via `additional_dependencies`. Each hook respects the file-type
filter pre-commit hands it (HTML for the a11y + Laws-of-UX hooks;
Markdown for the publish hook).

## CLI → GUI flagship

The `front-cli-gui` skill takes an existing CLI and produces a single-page vanilla-JS + Tailwind GUI for it. It reads the argument parser, categorizes each command (one-shot / form / streaming / list), maps flags to form controls, and wires execution to the project's host (Tauri, Electron, FastAPI, Express, or a stdlib HTTP+SSE proxy).

A runnable worked example ships in `front-cli-gui/assets/examples/cli-gui-demo/`. Launch:

```bash
cd front-cli-gui/assets/examples/cli-gui-demo
python server.py  # stdlib only, opens http://localhost:8787
```

For an honest comparison against Gradio / Streamlit / Tauri / Taipy, see `front-cli-gui/SKILL.md` → "Why this skill, not Gradio / Streamlit / Tauri / Taipy" and [LANDSCAPE.md](LANDSCAPE.md) § 7.

## Author

[Warith Harchaoui, Ph.D.](https://www.linkedin.com/in/warith-harchaoui/)

Nine Claude / OpenCode **skills** for a single frontend stack: vanilla JavaScript, Tailwind CSS, and the three-Roboto typography rule (Roboto / Roboto Serif / Roboto Mono). Built to the [Anthropic skill specification](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf).

Special thanks to [Audrey Dejoux](https://www.behance.net/dreyadesign/projects), [Laurent Pantanacce](https://www.linkedin.com/in/pantanacce/), [Auguste Baum](https://www.linkedin.com/in/auguste-baum/) and [Jérôme Gombert](https://www.linkedin.com/in/j%C3%A9r%C3%B4me-gombert-84675b1b/) for fruitful discussions.

Color palettes from <https://harchaoui.org/warith/colors/>.

The three Roboto families are bundled in `front-ui/assets/fonts/roboto/`, `front-ui/assets/fonts/roboto-serif/`, and `front-ui/assets/fonts/roboto-mono/`, each under the SIL Open Font License — see the bundled `OFL.txt` in each folder.

We also drew on the [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/), [Google Material Design](https://material.io/design) and [Laws of UX](https://lawsofux.com/)

## License

**BSD-3-Clause** — the same license used by **scikit-learn**.
Permissive: use, modify, redistribute, sell, ship in commercial
products. The three conditions are (1) keep the copyright notice in
source redistributions, (2) reproduce it in binary distributions'
documentation, (3) do not use the copyright holder's name to endorse
derived products without permission. See `LICENSE.md` for the canonical
text. The bundled Roboto / Roboto Serif / Roboto Mono fonts remain
under the SIL Open Font License (see the `OFL.txt` bundled in each
`front-ui/assets/fonts/roboto*/` folder); the BSD-3-Clause license
above applies to the source, not to the fonts.

**License vs. attribution.** Author credits in the docs are voluntary
acknowledgement (not part of the license condition #3). You are free
to remove or replace them in your fork; the BSD-3-Clause obligations
above are what travels with the code.
