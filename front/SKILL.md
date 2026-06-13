---
name: front
description: Generate vanilla JavaScript + Tailwind CSS frontend code, using Montserrat as the only typeface. Modular — use it to "build a UI", "create a component", "design a page", "make a form / modal / button / nav", "scaffold a landing", "build a web app", "wrap this CLI in a GUI", or "turn these markdown files into a website" — or any frontend work that must NOT use React, Vue, Svelte, Next.js or another JS framework. Output is semantic HTML + Tailwind classes + vanilla ES modules with dark-mode peers, focus rings, reduced-motion guards, and bilingual (EN/FR) copy.
license: Unlicense
metadata:
  author: Warith Harchaoui
  version: 0.1.0
---

# Front — Vanilla JS + Tailwind frontend skill

This skill produces frontend code that:

- Uses **vanilla JavaScript** (ES modules, custom elements when justified) — no React, Vue, Svelte, or other framework.
- Uses **Tailwind CSS** for all styling — no separate CSS files except a tiny base layer and the font face declaration.
- Uses **Montserrat** as the sole typeface family.
- Follows the curated UI guidelines in `references/ui-guidelines/`.
- Picks colors from the palettes in `references/color-psychology.md` (Choice / Emotion / Concept / Psychology).
- Honors accessibility, dark mode, reduced motion, RTL, and bilingual (EN/FR) copy by default.

## When to use this skill

Activate when the user is asking for any of:

- A new component (button, card, modal, form, nav, tab bar, sheet, alert, popover, …).
- A new page or landing surface.
- A redesign or audit of an existing piece of UI.
- A design system token set or starter template.
- A migration AWAY from a framework toward vanilla JS.
- **"Wrap my CLI in a GUI"** — the user has a working command-line tool and wants a graphical front-end. See `## CLI → GUI workflow` below.
- **"Turn these markdown files into a website"** — the user has a documentation tree, a README, a blog folder, or any Markdown-only project and wants a static site. See `## Markdown → website workflow` below.

## Modular use

The skill is modular, not a mono-block. Workflows are independent — picking one does not require buying the rest.

| User starts from | Workflow to pull | Other workflows skipped |
|---|---|---|
| A working CLI, no UI | `## CLI → GUI workflow` | MD → website, audit |
| Markdown docs, no site | `## Markdown → website workflow` | CLI → GUI, audit |
| Blank page, building components | `## Workflow — every task` + component templates in `assets/` | CLI → GUI, MD → site |
| Existing UI, needs a review | `references/ergonomics-criteria.md`, `references/ux-psychology.md`, `references/anti-patterns.md`, `references/checklist.md` | CLI → GUI, MD → site, full-build |

Reference files in `references/**` are independently consumable too — load only the ones the current task touches.

## CLI → GUI workflow (flagship use case)

When the user points to an existing CLI project and asks for a GUI:

1. **Inventory the CLI.** Read the help output (`tool --help`, `tool sub --help`), the README, the source's argument parser (`argparse`, `clap`, `commander`, `cobra`, …). Build a map of: sub-commands → flags → input types → output shape.
2. **Categorize each command** by surface:
   - One-shot action (single button + result panel).
   - Form-driven (multiple inputs → run).
   - Long-running (streaming output → progress + log panel).
   - List-producing (table view with filters).
3. **Pick a layout**:
   - 2–4 commands → tab bar at the bottom (mobile) or sidebar (desktop).
   - 5–8 → sidebar with grouped sections.
   - 9+ → command palette (`⌘K`) + categorized sidebar.
4. **Map flags to form controls**:
   - boolean flag → toggle.
   - enum flag → segmented control (≤4 options) or select.
   - path → file input + drag-drop zone.
   - string → text field.
   - number → stepper or slider.
   - repeated flag → tag list.
5. **Wire execution.** Choose ONE of these depending on the project:
   - **Local-only**, packaged as Tauri / Electron / web view: invoke via the host's `invoke()` / IPC.
   - **HTTP-served**: emit a tiny `fetch` wrapper assuming the CLI is wrapped by `python -m http.server`, `express`, `fastapi`, etc.
   - **Browser-only demo**: stub execution with `console.log` and clearly mark TODOs.
6. **Stream output** to a monospace `<pre>` panel; convert ANSI to HTML if needed.
7. **Emit a single `index.html` + `app.js` + Tailwind** that runs out of the box. Ship the Montserrat fonts in `./fonts/`.
8. **Document** in the project's README how to launch the GUI alongside the CLI.

Do **not** use this skill when:

- The user explicitly asks for React / Vue / Svelte / Next.js / Nuxt / Angular / SolidJS.
- The task is backend-only (no UI surface).
- The user explicitly asks for a non-Tailwind CSS approach (BEM, CSS Modules, vanilla CSS by hand).

## Markdown → website workflow

When the user points to a Markdown-only project (README + docs folder, a blog directory, a knowledge base) and asks for a website:

1. **Inventory the Markdown.** Walk the tree. Group files by purpose: landing (`README.md`), documentation (`docs/**/*.md`), blog posts (`posts/**`, `blog/**`), references (`api/**`), changelogs. Note frontmatter conventions if present (YAML at the top of each file).
2. **Pick a site shape**:
   - One README → single landing page with anchored sections from the headings.
   - README + a `docs/` tree → two-pane docs site (sidebar TOC + content).
   - Blog directory → home with post list + per-post pages + tag pages.
   - Multiple shapes → start with the landing; offer the others as additional pages.
3. **Build a route map**. Each Markdown file becomes one HTML page; preserve the directory shape under the output root. The landing lives at `/index.html`.
4. **Generate navigation**:
   - Sticky top bar with the project name on the start, theme switcher on the end (per `ui-guidelines/components/navigation-bars.md`).
   - Sidebar (lg:) with the section tree on `docs/**` pages.
   - Bottom tab bar (mobile) when ≤ 5 top-level destinations.
5. **Convert Markdown to HTML**. Prefer a build-step tool (Pandoc, `markdown-it`, `python-markdown`) so the output is plain HTML; do not import a Markdown runtime into the browser. Apply the typography component classes from `references/stack-tailwind.md` (`h-display`, `t-body`, `t-callout`, `t-footnote`). Code blocks get a server-side syntax highlighter (Pygments, `highlight.js` build step) — never load a runtime highlighter.
6. **Wire meta tags per page** using `references/meta-tags.md` and (optional) `python scripts/meta_from_ollama.py path/to/page.html` for the title, description, OG, JSON-LD.
7. **Generate the favicon set** from the project's logo with `python scripts/favicons.py logo.png --out public --name "Project name"`; drop the produced `head.html` snippet into the layout template.
8. **Emit pages + assets**. One `index.html` per page, one shared `app.js` (theme switcher, search if needed), one `styles.css` (Tailwind directives + Montserrat). Include the favicon set under `public/`. Add a small `README.md` to the output root explaining the build steps.

The output is a static site that drops into any host (GitHub Pages, Netlify, S3, plain Nginx) without a runtime build.

## Workflow — every task

```
1. Identify the surface (page / component / token / audit).
2. Read ONLY the relevant reference files (do not preload all).
3. Pick colors via color-psychology.md → semantic intent first.
4. Map to Tailwind tokens (see stack-tailwind.md).
5. Write semantic HTML with Tailwind classes.
6. Add vanilla JS only where needed (form state, dialog open/close, theme).
7. Run the pre-ship checklist in references/checklist.md.
8. Return code + a one-paragraph rationale.
```

## Hard rules

1. **No framework imports.** Output never contains `react`, `vue`, `svelte`, `solid-js`, `next`, `nuxt`, `angular`. The skill REFUSES to emit framework code; if asked, it explains why and offers the vanilla equivalent.
2. **Tailwind classes only**, never inline `style="…"` except for one-off CSS custom-property values that have no utility (e.g. `style="--accent: #007AFF"`).
3. **Montserrat only.** No other type families. Self-host from `assets/fonts/montserrat/`.
4. **Semantic HTML first.** `<button>`, `<a href>`, `<label for>`, `<dialog>`, `<form>`. ARIA only when no semantic element fits.
5. **Both color schemes.** Every styled element gets a `dark:` peer.
6. **Accessibility is shipping-required.** See `references/ui-guidelines/foundations/accessibility.md`.
7. **No raw hex** in markup — use semantic Tailwind tokens (`bg-brand-blue`, `text-label-primary`).
8. **Bilingual-ready copy.** Default to English; if the user types in French OR asks for French, switch and provide BOTH where it matters.
9. **No third-party trademarks** in defaults (logos, product names, OS branding). Use generic, neutral language.

## Decision tree — picking the right component

| User says… | Read | Emit |
|---|---|---|
| "primary button" | `components/buttons.md` | `<button>` with `bg-brand-blue rounded-full px-5 py-3 text-white font-medium` |
| "destructive button" | `components/buttons.md` | `<button>` with `bg-brand-red text-white` (or text-only red for low-emphasis) |
| "modal" / "dialog" | `components/sheets.md` + `patterns/modality.md` | `<dialog>` element + open/close JS, `Escape` key, focus restore |
| "bottom sheet" | `components/sheets.md` | `<dialog>` bottom-anchored, slide-up animation, swipe-down handle |
| "alert" | `components/alerts.md` | `<dialog>` centered, 1–2 buttons, no scroll inside |
| "popover" / "tooltip" | `components/popovers.md` | `popover` attribute (modern), anchor positioning |
| "menu" | `components/menus.md` | `<details>` or `<dialog>` with menuitems |
| "tab bar" | `components/tab-bars.md` | Bottom nav with icons + labels, max 5 items |
| "navigation bar" | `components/navigation-bars.md` | Sticky top, translucent material, back/title/action layout |
| "form" / "input" | `components/text-fields.md` + `foundations/inclusion.md` | `<label>` + `<input>` with `autocomplete`, error pattern |
| "toggle" | `components/toggles.md` | `<input type="checkbox" role="switch">` styled as pill |
| "settings page" | `patterns/settings.md` | List sections with separators, no card chrome |
| "loading" | `patterns/loading.md` | Skeleton if > 300 ms, spinner only if unknown duration |
| "search" | `patterns/searching.md` | `<input type="search">` with debounced JS, results live region |
| "onboarding" | `patterns/onboarding.md` | One idea per screen, ≤ 8-word headline, skippable |
| "theme switch" | `foundations/dark-mode.md` | `data-color-scheme` attribute + persisted choice |
| "chart" / "graph" / "dashboard tile" | `charts-vega.md` + `dataviz-chart-selection.md` + `dataviz-color-palettes.md` | Vega-Lite v5 JSON spec, Montserrat, 10 px rounded corners, palette from `color-psychology.md`, no top/right spines, no tick marks |
| "dashboard" / "BI" / "KPI summary" | `dashboard-ergonomics.md` (+ chart references above) | One question per tile, title as a question, sticky filters, grid layout (12 cols), skeleton tiles while loading |
| "map" / "choropleth" / "cartography" | `dataviz-maps.md` | Title states the message, ≤ 7 classes, locator inset for unfamiliar audiences, accessible text alternative below the map |
| "audit" / "ergonomic review" / "UX review" | `ergonomics-criteria.md` | Walk the 8 criteria: guidance, workload, explicit control, adaptability, error management, consistency, label significance, compatibility |
| "a11y lint" / "check this HTML for accessibility" / "WCAG check" | `lint-a11y.md` | Run `python scripts/lint_a11y.py <file-or-dir>`; 14 rules cover the bulk of WCAG / WAI-ARIA failures decidable from source. Exit 1 on any finding. |
| "plain language" / "simplify this copy" / "rewrite at grade N" | `plain-language.md` | `cat copy.md \| python scripts/plain_language.py --target-grade 8 --lang en` — keeps meaning, strips marketing voice, output length ≤ 1.1×. |
| "color blind preview" / "CVD check" / "how does this look to a deuteranope" | `cvd-simulation.md` | `python scripts/simulate_cvd.py <image> [--grid]` → renders the image as protanopia / deuteranopia / tritanopia viewers see it. Catches red/green pairing before it ships. |
| "contrast audit" / "WCAG ratio" / "is my palette accessible" | `contrast-audit.md` | `python scripts/audit_contrast.py [--palette p.json] [--target 4.5\|7\|3] [--fix]` → walks every (label, surface) pair, suggests the nearest OKLCH-neighbour fix for failures. Exit 1 on any failure. |
| "i18n" / "multilingual" / "translate" / "localize" | `i18n.md` | One URL strategy, `<html lang>` always set, `Intl.*` for formatting + plurals, logical CSS for RTL, persisted user choice wins over auto-detect |
| "material" / "Material 3" / "M3" / named Material component | `material-design.md` | Map Material roles to skill tokens; emit plain HTML + Tailwind (no `mdc-*` classes, no Material Web Components) |
| "make it look less AI" / "designer review" / "anti-patterns" | `anti-patterns.md` | Refuse gradient text, glassmorphism on body, side-stripe borders, "boost your productivity" copy, three-card grids, marketing buzzwords |
| "psychology" / "conversion" / "cognitive bias" / "flow not working" | `ux-psychology.md` | Pick ONE applicable principle per screen — Hick / Anchoring / Default Bias / Peak-End / Goal Gradient — and apply concretely |
| "alt text" / `<img>` with no `alt` / "describe this image" | `alt-text-ai.md` | Match W3C image-purpose decision tree → `python scripts/alt_from_ollama.py [--kind informative\|decorative\|functional\|text\|complex\|group] [--lang fr] <src>`. Decorative → `alt=""` alone. Tag AI drafts with `data-alt-source="ai"`. |
| "favicon" / "app icon" / "PWA icons" / "touch icon" | `ui-guidelines/foundations/app-icons.md` + `meta-tags.md` | `python scripts/favicons.py <logo> --out public --name "…" --bg "#…"` → produces favicon.svg/.ico, PNG set, apple-touch-icon, maskable PWA icon, site.webmanifest, head.html snippet. |
| "meta tags" / "SEO" / "Open Graph" / "Twitter card" / "JSON-LD" | `meta-tags.md` | Base + canonical + OG + Twitter card + JSON-LD `@type`; `python scripts/meta_from_ollama.py [--goal …] [--lang fr] [<page.html\|url>]` drafts the per-page title/description/og_image_alt. |

## Stack basics

- **Vanilla JS**: ES modules (`<script type="module">`), event delegation on a root element, `<template>` for repeating fragments, native `<dialog>` for modals, `customElements.define` only for genuinely reusable widgets. See `references/stack-vanilla-js.md`.
- **Tailwind**: utility-first; semantic tokens defined in `references/stack-tailwind.md`; dark mode via `[data-color-scheme="dark"]`; recommended plugins: `@tailwindcss/forms`, `@tailwindcss/typography`.
- **Build**: prefer Tailwind CLI or Vite for setup. The starter page in `assets/starter-page.html` uses the Tailwind CDN (Play CDN) to stay zero-config; production output should swap to a built CSS.
- **Font**: Montserrat self-hosted, served from `assets/fonts/montserrat/`. CSS in `assets/fonts/montserrat/fonts.css` is paste-ready.

## Bilingual (EN / FR) defaults

Default output language is English. Switch to French when the user writes in French or asks for it. For repos that ship both languages, the convention is:

- `README.md` (English) and `LISEZMOI.md` (French) — each starts with a switcher: `[🇫🇷](LISEZMOI.md) · [🇬🇧](README.md)`.
- For runtime copy, use a small `i18n` object keyed by `lang`; default to `navigator.language.startsWith('fr') ? 'fr' : 'en'`.
- Set `<html lang="…">` correctly.

## Examples

### Example 1 — primary CTA button

User: "Give me a primary button labeled 'Get started'."

```html
<button class="inline-flex min-h-11 items-center justify-center gap-2 rounded-full
               bg-brand-blue px-5 py-3 text-[17px] font-semibold text-white
               transition-transform duration-100 ease-out
               hover:opacity-90 active:scale-[0.97]
               focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-blue
               focus-visible:ring-offset-2 focus-visible:ring-offset-surface-primary
               motion-reduce:active:scale-100
               disabled:opacity-50 disabled:pointer-events-none">
  Get started
</button>
```

### Example 2 — confirm dialog (destructive)

User: "Confirm-delete dialog."

```html
<button id="open-del" class="text-brand-red">Delete project</button>

<dialog id="del" class="w-full max-w-sm rounded-2xl bg-surface-primary p-5 text-center
                         backdrop:bg-black/40 dark:bg-surface-primary-dark">
  <h2 class="text-[17px] font-semibold text-label-primary dark:text-label-primary-dark">
    Delete this project?
  </h2>
  <p class="mt-1 text-[15px] text-label-secondary dark:text-label-secondary-dark">
    This action can't be undone.
  </p>
  <div class="mt-5 flex gap-2">
    <button value="cancel" class="flex-1 min-h-11 rounded-xl bg-surface-secondary px-4 font-medium text-label-primary dark:bg-surface-secondary-dark dark:text-label-primary-dark">Cancel</button>
    <button value="delete" class="flex-1 min-h-11 rounded-xl bg-brand-red px-4 font-semibold text-white">Delete</button>
  </div>
</dialog>

<script type="module">
  const dlg = document.getElementById('del');
  document.getElementById('open-del').addEventListener('click', () => dlg.showModal());
  dlg.addEventListener('click', (e) => { if (e.target === dlg) dlg.close('cancel'); });
  dlg.addEventListener('close', () => {
    if (dlg.returnValue === 'delete') { /* perform deletion */ }
  });
</script>
```

### Example 3 — translucent sticky header

User: "App header with logo, nav, sign-in."

```html
<header class="sticky top-0 z-30 border-b border-separator/40
               bg-surface-primary/70 backdrop-blur-ultra
               dark:bg-surface-primary-dark/70">
  <div class="mx-auto flex w-full max-w-6xl items-center gap-3 px-4 py-3">
    <a href="/" class="flex items-center gap-2 font-semibold text-label-primary dark:text-label-primary-dark">
      <img src="/logo.svg" alt="" width="24" height="24" class="rounded">
      <span>Front</span>
    </a>
    <nav class="ml-auto flex items-center gap-1">
      <a href="/docs" class="rounded-lg px-3 py-2 text-[15px] text-label-secondary hover:bg-surface-secondary dark:text-label-secondary-dark dark:hover:bg-surface-secondary-dark">Docs</a>
      <a href="/login" class="rounded-full bg-brand-blue px-4 py-2 text-[15px] font-medium text-white hover:opacity-90">Sign in</a>
    </nav>
  </div>
</header>
```

## Quality checklist (pre-ship)

Run `references/checklist.md` before returning code. The short version:

- [ ] No framework imports.
- [ ] Montserrat only; self-hosted.
- [ ] Semantic HTML; ARIA only where no semantic fits.
- [ ] Visible focus ring everywhere; `Escape` closes dialogs.
- [ ] `dark:` peer set for every styled element.
- [ ] Min hit area 44×44 for any interactive control.
- [ ] Body ≥ 16 px; line length ≤ 75 ch on long-form.
- [ ] `prefers-reduced-motion` honored — no translate/scale under reduce.
- [ ] Color choice traceable to `color-psychology.md`.
- [ ] No raw hex in markup.
- [ ] Copy is sentence case, verb-first on buttons, no "OK"/"please".

## Error handling

| Symptom | Cause | Fix |
|---|---|---|
| Skill emits React/JSX | Misread prompt | Hard-refuse, emit vanilla HTML + JS instead, explain why. |
| Font shows fallback briefly | `font-display: swap` is intentional | Document the FOUT; do NOT switch to `block` (worse UX). |
| Colors look "off" in dark mode | Missing `dark:` peer | Add `dark:` variant for every meaningful surface and text token. |
| Dialog doesn't close on backdrop | Missing click-outside handler | Add the `e.target === dlg` listener pattern (see Example 2). |
| Animations jank under reduced motion | Animating `width/height/top/left` | Switch to `transform` and `opacity`; add `motion-reduce:` guards. |
| Contrast fails | Used label-secondary on accent surface | Switch to label-primary; verify ≥ 4.5:1. |

## References (progressive disclosure)

Load these only when needed.

**Path convention:** every reference path in this file is relative to the skill root. Component, pattern, input, and platform paths shown earlier as `components/buttons.md`, `patterns/loading.md`, etc. resolve to `references/ui-guidelines/components/buttons.md`, `references/ui-guidelines/patterns/loading.md`, and so on.

- `references/color-psychology.md` — Choice / Emotion / Concept / Psychology palettes (Warith Harchaoui).
- `references/stack-vanilla-js.md` — patterns: modules, custom elements, events, a11y, state, i18n.
- `references/stack-tailwind.md` — config tokens, plugins, dark mode strategy.
- `references/charts-vega.md` — Vega-Lite house style (Montserrat, 10 px rounded corners, palette, matplotlib → Vega-Lite axis cleanup map).
- `references/dataviz-chart-selection.md` — picking the right chart shape (comparison / composition / relationship / distribution).
- `references/dataviz-color-palettes.md` — accessible color palettes for dataviz (sequential / divergent / categorical).
- `references/dataviz-maps.md` — choropleth and map-specific ergonomics.
- `references/dashboard-ergonomics.md` — laying out a dashboard tile-by-tile.
- `references/ergonomics-criteria.md` — eight ergonomic criteria for UX review.
- `references/i18n.md` — multilingual frontend (URL strategy, `Intl.*`, plurals, RTL, persisted choice).
- `references/anti-patterns.md` — visual and copy tells to refuse (gradients, glassmorphism, marketing buzzwords).
- `references/ux-psychology.md` — applied cognitive principles for ergonomic review and conversion audits.
- `references/material-design.md` — Material 3 distilled and mapped to the skill's tokens.
- `references/meta-tags.md` — `<meta>` tags (W3C / WHATWG + Open Graph + Twitter Cards + Schema.org JSON-LD).
- `references/lint-a11y.md` — static a11y linter rule catalogue and CI integration.
- `references/plain-language.md` — rewriter that simplifies copy at a target reading level.
- `references/cvd-simulation.md` — color-blindness simulator (protanopia / deuteranopia / tritanopia).
- `references/contrast-audit.md` — WCAG contrast audit and OKLCH-neighbour fix suggester.
- `references/alt-text-ai.md` — W3C-compliant alt text via local Ollama + Gemma vision (per-purpose: informative / decorative / functional / text / complex / group).
- `references/checklist.md` — pre-ship quality gate.
- `references/ui-guidelines/INDEX.md` — full map of foundations, patterns, components, inputs, platforms.

## Assets (templates)

Copy / adapt from `assets/`:

- `assets/starter-page.html` — bootstrap a full page with Montserrat + Tailwind + tokens.
- `assets/components/button.html`, `card.html`, `modal.html`, `form-field.html`, `nav.html`.
- `assets/components/chart-bar.json`, `chart-line.json` — Vega-Lite specs ready to load via Vega-Embed.
- `assets/fonts/montserrat/` — Montserrat variable + italic + 4 static weights + OFL license + paste-ready `fonts.css`.
- `assets/examples/cli-gui-demo/` — runnable CLI → GUI worked example. Mock CLI (`cli/imgconvert.py`), Python SSE proxy (`server.py`), and a single-page GUI under `public/`. Launch with `python server.py` and open <http://localhost:8787>. See `assets/examples/cli-gui-demo/README.md` for the 8-step CLI → GUI mapping.

## Scripts

All scripts are Python 3.9+, cross-platform. Install deps once: `pip install -r scripts/requirements.txt`.

- `scripts/validate.py` — pre-ship quality gate. Resolves the skill root from its own location, exits non-zero on any failure. Checks: frontmatter shape, description length, forbidden framework imports, trademarked UI-platform terms in user-facing docs, LLM-marketing phrases, absence of `README.md` inside the skill folder, and that every reference path declared by `references/ui-guidelines/INDEX.md` resolves.
- `scripts/install_alt_ai.py` — installs Ollama if missing (Homebrew / official installer / `winget`), starts the daemon, pulls the vision model (`gemma4:e2b`; `-mlx` variant on MLX-capable hardware).
- `scripts/alt_from_ollama.py` — generates W3C-compliant alt text via the local model. Handles informative / decorative / functional / text / complex / group per the WAI decision tree. See `references/alt-text-ai.md`.
- `scripts/lint_a11y.py` — static a11y linter for emitted HTML; 14 rules covering the WCAG / WAI-ARIA violations decidable from source. See `references/lint-a11y.md`.
- `scripts/plain_language.py` — rewrite UI copy at a target reading level via the local model; preserves meaning, strips marketing voice. See `references/plain-language.md`.
- `scripts/simulate_cvd.py` — render an image as protanopia / deuteranopia / tritanopia viewers see it. Pillow + Machado et al. matrices, no model. See `references/cvd-simulation.md`.
- `scripts/audit_contrast.py` — WCAG contrast audit + OKLCH-neighbour fix suggester for a palette. No dependencies. See `references/contrast-audit.md`.
- `scripts/favicons.py` — generates the full favicon / app-icon set from a single logo (Pillow): `favicon.svg`/`.ico`, PNG variants, `apple-touch-icon.png`, maskable PWA icon, `site.webmanifest`, and a `head.html` snippet to paste into `<head>`.
- `scripts/meta_from_ollama.py` — drafts page meta tags (title, description, Open Graph, Twitter, Schema.org `@type`) from a goal description or an HTML page. JSON on stdout. See `references/meta-tags.md`.
