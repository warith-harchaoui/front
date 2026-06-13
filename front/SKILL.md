---
name: front
description: Generate vanilla JavaScript + Tailwind CSS frontend code, using Montserrat as the only typeface. Use when the user asks to "build a UI", "create a component", "design a page", "make a form / modal / button / nav", "scaffold a landing", or "build a web app" — or any frontend work that must NOT use React, Vue, Svelte, Next.js or another JS framework. Output is semantic HTML + Tailwind classes + vanilla ES modules with dark-mode peers, focus rings, reduced-motion guards, and bilingual (EN/FR) copy.
license: MIT
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
- **"Wrap my CLI in a GUI"** — the user has a working command-line tool and wants a graphical front-end. The skill reads the CLI's flags / sub-commands / I/O contract and emits a single-page vanilla-JS + Tailwind UI that drives it. See the workflow in the next section.

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
| "chart" / "graph" / "dashboard tile" | `charts-vega.md` | Vega-Lite v5 JSON spec, Montserrat, 10 px rounded corners, palette from `color-psychology.md`, no top/right spines, no tick marks |
| "alt text" / `<img>` with no `alt` / "describe this image" | `alt-text-ai.md` | Call `node scripts/alt-from-ollama.mjs <src>` (Ollama + `gemma4:e2b`, `-mlx` on Apple Silicon). `EMPTY` → `alt="" role="presentation" aria-hidden="true"`. Tag drafts with `data-alt-source="ai"`. |

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
- `references/alt-text-ai.md` — AI-drafted `alt` via local Ollama + Gemma vision.
- `references/checklist.md` — pre-ship quality gate.
- `references/ui-guidelines/INDEX.md` — full map of foundations, patterns, components, inputs, platforms.

## Assets (templates)

Copy / adapt from `assets/`:

- `assets/starter-page.html` — bootstrap a full page with Montserrat + Tailwind + tokens.
- `assets/components/button.html`, `card.html`, `modal.html`, `form-field.html`, `nav.html`.
- `assets/components/chart-bar.json`, `chart-line.json` — Vega-Lite specs ready to load via Vega-Embed.
- `assets/fonts/montserrat/` — Montserrat variable + italic + 4 static weights + OFL license + paste-ready `fonts.css`.
