---
name: front-ui
description: >-
  Generate vanilla JavaScript + Tailwind CSS UI code — components, pages,
  forms, dialogs, dashboards — for solo developers and small teams shipping
  internal tools without a designer. Three-Roboto typography rule: Roboto
  (sans), Roboto Serif (serif), Roboto Mono (code/monospace); no other
  downloaded webfont. Output is semantic HTML + Tailwind utility classes +
  vanilla ES modules with dark-mode peers, focus rings, reduced-motion
  guards. Use it for "build a UI", "create a component", "design a page",
  "make a form / modal / button / nav", "scaffold a landing", "build a web
  app", "audit this UI". Companion skills: front-cli-gui (wrap a CLI in a
  GUI), front-publish (Markdown → website + meta tags + favicons), front-a11y
  (a11y lint, contrast audit, alt text, captions).
license: Unlicense
compatibility: >-
  Runtime: Claude.ai, Claude Code, OpenCode. No Python runtime required to use
  the skill itself (output is HTML + CSS + vanilla JS). Optional validator
  scripts/validate.py needs Python 3.9+ stdlib + PyYAML. Network access not
  required.
metadata:
  author: Warith Harchaoui
  version: 0.6.4
  lang_pair: "en,fr"  # override per-project; e.g. "en,de" or "en,ja"
---

# front-ui — vanilla JS + Tailwind UI generation

## Audience

Solo developers and small teams (≤ 5 people) shipping **internal tools**: dev dashboards, admin panels, ML / data-science demo apps, settings screens, prototypes, docs landing pages. You don't have a designer on the team and don't want to fight a framework. You want output that looks deliberate, ships immediately, and survives a year without React-version churn.

This skill is **not** the right pick for:
- Consumer-app brand work that needs a custom visual identity.
- Marketing landing pages where a tool like Webflow or Framer is faster.
- Apps where the team has chosen React / Vue / Svelte — use shadcn / Headless UI instead.

## When to use this skill

Trigger phrases:

- A new component (button, card, modal, form, nav, tab bar, sheet, alert, popover, …).
- A new page, landing surface, or admin screen.
- A redesign or ergonomic audit of an existing piece of UI.
- A design system token set or starter template.
- A dashboard, KPI summary, or dataviz tile.
- A migration **away** from a framework toward vanilla JS.

For other work, use the companion skills:

| Task | Skill |
|---|---|
| Wrap an existing CLI in a web GUI | `front-cli-gui` |
| Turn a folder of Markdown into a website + meta tags + favicons + site indexes | `front-publish` |
| Alt text, captions, contrast audit, CVD simulation, a11y lint | `front-a11y` |

The companion skills assume the same stack rules below.

## Hard rules

1. **No framework imports.** Output never contains `react`, `vue`, `svelte`, `solid-js`, `next`, `nuxt`, `angular`. If asked, refuse and offer the vanilla equivalent.
2. **Tailwind utility classes only**, never inline `style="…"`. The single allowed exception is a one-off CSS custom property whose value references an existing token (e.g. `style="--accent: var(--brand-blue)"`). **Never** put a raw hex literal in markup — even inside `style="--accent: #007AFF"`. If a new accent is needed, add the token to `tailwind.config.js` (`theme.extend.colors.brand`) and reference it via `var(--brand-…)` or a Tailwind class. This keeps rule 7 (no raw hex) and rule 2 in lockstep.
3. **The three-Roboto rule — for generation, not for audits.** **When generating fresh UI / site output and no typeface has been specified by the user**, ship exactly three downloaded webfonts, all from the Roboto super-family: **Roboto** for sans, **Roboto Serif** for serif, **Roboto Mono** for code / monospace. No other downloaded family is allowed by default — not Inter, not Montserrat, not IBM Plex, not JetBrains Mono. Use Roboto for body / UI text by default; lift Roboto Serif when a surface wants editorial weight (longform reading, quote pulls, prose-heavy landings); use Roboto Mono for `<code>`, `<pre>`, kbd / samp, terminal panels. Self-host always (no Google Fonts CDN, no jsDelivr GH proxy in production builds); system-font fallback stacks (`ui-monospace`, `system-ui`, `serif`, `sans-serif`) are fine and expected. **The rule does NOT apply when:** (a) **auditing an existing site / UI** — respect the existing fonts; don't propose a font swap unless the user specifically asks about typography; (b) **the user names a typeface** ("use Inter", "we ship IBM Plex", "stick to system fonts") — use what they ask for; (c) **the user asks for a fourth family explicitly for brand reasons** — carry it out and record the choice in the project README so a future maintainer knows why.
4. **Semantic HTML first.** `<button>`, `<a href>`, `<label for>`, `<dialog>`, `<form>`. ARIA only when no semantic element fits.
5. **Both color schemes.** Every styled element gets a `dark:` peer.
6. **Accessibility is shipping-required.** See `references/ui-guidelines/foundations/accessibility.md`.
7. **No raw hex** in markup — use semantic Tailwind tokens (`bg-brand-blue`, `text-label-primary`).
8. **Bilingual-ready copy** (EN/FR by default — configurable via `lang_pair`). Default to English. Switch to the user's language when they write in it. The project-level pair is set in this SKILL.md's frontmatter `metadata.lang_pair` token and is consumed by every place the skill currently talks about EN/FR — see **Changing the language pair** below and `front-publish/references/i18n.md` for the full configuration recipe.
9. **No third-party trademarks** in defaults (logos, product names, OS branding). Use generic, neutral language.

## Changing the language pair

`front-ui` is **bilingual** (EN/FR by default — configurable via
`lang_pair`). The pair lives in this file's frontmatter, under
`metadata.lang_pair`, as two comma-separated BCP-47 base tags. To use a
different pair (Berlin → `en,de`; Tokyo → `en,ja`; Madrid → `en,es`):

1. Edit `metadata.lang_pair` in `SKILL.md` (this file).
2. Mirror the same value in any companion skill you install
   (`front-publish/SKILL.md`, `front-a11y/SKILL.md`).
3. The skill uses the pair everywhere it currently uses EN/FR — the
   alt-text language line (`alt_from_ollama.py --lang`), the captions
   language hint (`captions_from_whisper.py --lang`), the meta-tag
   `og:locale_alternate`, the docs site's `<link rel="alternate"
   hreflang>` pairs.

**Runtime override.** For ad-hoc shells, set the `FRONT_LANG_PAIR`
environment variable instead of editing the frontmatter — the four
Ollama-backed scripts (`alt_from_ollama.py`, `captions_from_whisper.py`,
`meta_from_ollama.py`, `plain_language.py`) read its first comma-split
entry as the default `--lang` when none is passed on the command line:

```bash
export FRONT_LANG_PAIR="en,de"
python front-a11y/scripts/alt_from_ollama.py photo.jpg   # → German alt text
```

Precedence (highest first): explicit `--lang` flag → `FRONT_LANG_PAIR`
first entry → langdetect on available text → POSIX locale fallback.

The wider i18n model (URL strategy, `Intl.*`, plurals, RTL,
non-Latin fonts) is in `front-publish/references/i18n.md`. The
`lang_pair` token is a project-level default for the **two main
languages** the skill maintains in lock-step; it is not the full
supported-locale list. Sites that ship in three or more languages
should keep `lang_pair` as the two anchored languages and use the
i18n reference's `supported` list for the rest.

## Build vs prototype

Tailwind has a build step. The skill emits **prototype-grade single-file deliverables** by default — fine for demos, mockups, internal tools and small landing pages, **not** for production sites at scale. Two paths:

- **Prototype** (single-file demo, internal POC, throwaway, small landing): use the Tailwind Play CDN as shipped in `assets/starter-page.html`. Tailwind itself warns this is for prototyping only. The class names emitted by the skill are stable, so the same HTML works under the production path below.
- **Production**: run **Tailwind CLI** (single command, no JS framework needed) or **Vite + Tailwind** over the emitted HTML before shipping. See `references/stack-tailwind.md`.

The "zero build, drop into Nginx / S3 / Pages" pitch only holds for the prototype path. A real production site needs the build step. State which path you are on in the project README so the next maintainer knows whether the CDN tag is intentional or a leftover.

## Workflow — every task

```text
1. Identify the surface (page / component / token / audit).
2. Read ONLY the relevant reference files (do not preload all).
3. Pick colors via color-psychology.md → semantic intent first.
4. Map to Tailwind tokens (see stack-tailwind.md).
5. Write semantic HTML with Tailwind classes.
6. Add vanilla JS only where needed (form state, dialog open/close, theme).
7. Run the pre-ship checklist in references/checklist.md.
8. Return code + a one-paragraph rationale.
```

## Decision tree — picking the right component

| User says… | Read | Emit |
|---|---|---|
| "primary button" | `ui-guidelines/components/buttons.md` | `<button>` with `bg-brand-blue rounded-full px-5 py-3 text-white font-medium` |
| "destructive button" | `ui-guidelines/components/buttons.md` | `<button>` with `bg-brand-red text-white` (or text-only red for low-emphasis) |
| "modal" / "dialog" | `ui-guidelines/components/sheets.md` + `ui-guidelines/patterns/modality.md` | `<dialog>` element + open/close JS, `Escape` key, focus restore |
| "bottom sheet" | `ui-guidelines/components/sheets.md` | `<dialog>` bottom-anchored, slide-up animation, swipe-down handle |
| "alert" | `ui-guidelines/components/alerts.md` | `<dialog>` centered, 1–2 buttons, no scroll inside |
| "popover" / "tooltip" | `ui-guidelines/components/popovers.md` | `popover` attribute (modern), anchor positioning |
| "menu" | `ui-guidelines/components/menus.md` | `<details>` or `<dialog>` with menuitems |
| "tab bar" | `ui-guidelines/components/tab-bars.md` | Bottom nav with icons + labels, max 5 items |
| "navigation bar" | `ui-guidelines/components/navigation-bars.md` | Sticky top, translucent material, back/title/action layout |
| "form" / "input" | `ui-guidelines/components/text-fields.md` + `ui-guidelines/foundations/inclusion.md` | `<label>` + `<input>` with `autocomplete`, error pattern |
| "toggle" | `ui-guidelines/components/toggles.md` | `<input type="checkbox" role="switch">` styled as pill |
| "settings page" | `ui-guidelines/patterns/settings.md` | List sections with separators, no card chrome |
| "loading" | `ui-guidelines/patterns/loading.md` | Skeleton if > 300 ms, spinner only if unknown duration |
| "search" | `ui-guidelines/patterns/searching.md` | `<input type="search">` with debounced JS, results live region |
| "onboarding" | `ui-guidelines/patterns/onboarding.md` | One idea per screen, ≤ 8-word headline, skippable |
| "theme switch" | `ui-guidelines/foundations/dark-mode.md` | `data-color-scheme` attribute + persisted choice |
| "chart" / "graph" / "dashboard tile" | `charts-vega.md` + `dataviz-chart-selection.md` + `dataviz-color-palettes.md` | Vega-Lite v5 JSON spec, Roboto, 10 px rounded corners, palette from `color-psychology.md`, no top/right spines. State polarity when well-defined (*↑ higher is better* / *↓ lower is better* / *target = N ± k*). |
| "dashboard" / "BI" / "KPI summary" | `dashboard-ergonomics.md` (+ chart references above) | One question per tile, title as a question, polarity tag on every measurable tile, sticky filters, 12-column grid, skeleton tiles while loading. |
| "map" / "choropleth" | `dataviz-maps.md` | Title states the message, ≤ 7 classes, locator inset, accessible text alternative below the map |
| "audit" / "ergonomic review" / "UX review" | `ergonomics-criteria.md` | Walk the 8 criteria: guidance, workload, explicit control, adaptability, error management, consistency, label significance, compatibility. **Respect the existing typeface stack** — do not propose a three-Roboto swap unless the user explicitly asks about typography. |
| "make it look less AI" / "designer review" | `anti-patterns.md` | Refuse gradient text, glassmorphism on body, side-stripe borders, "boost your productivity" copy, three-card grids |
| "psychology" / "conversion" / "flow not working" | `ux-psychology.md` | Pick ONE applicable principle per screen — Hick / Anchoring / Default Bias / Peak-End / Goal Gradient — and apply concretely |
| "material" / "Material 3" / "M3" | `material-design.md` | Map Material roles to skill tokens; emit plain HTML + Tailwind (no `mdc-*` classes) |

## Quality checklist (pre-ship)

Run `references/checklist.md` before returning code. Short version:

- [ ] No framework imports.
- [ ] Three-Roboto rule: only Roboto / Roboto Serif / Roboto Mono, all self-hosted.
- [ ] Semantic HTML; ARIA only where no semantic fits.
- [ ] Visible focus ring everywhere; `Escape` closes dialogs.
- [ ] `dark:` peer set for every styled element.
- [ ] Min hit area 44×44 for any interactive control.
- [ ] Body ≥ 16 px; line length ≤ 75 ch on long-form.
- [ ] `prefers-reduced-motion` honored — no translate/scale under reduce.
- [ ] Color choice traceable to `color-psychology.md`.
- [ ] No raw hex in markup.
- [ ] Copy is sentence case, verb-first on buttons, no "OK"/"please".

Pair with `front-a11y` for `lint_a11y.py`, `audit_contrast.py`, `simulate_cvd.py` runs.

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

## References

Load these only when needed.

**Stack & tokens**
- `references/color-psychology.md` — Choice / Emotion / Concept / Psychology palettes.
- `references/stack-vanilla-js.md` — Vanilla JS patterns.
- `references/stack-tailwind.md` — Config tokens, plugins, dark-mode strategy, the three-Roboto typography rule.
- `references/checklist.md` — Pre-ship quality gate.

**Dataviz**
- `references/charts-vega.md` — Vega-Lite house style.
- `references/dataviz-chart-selection.md` — Picking the right chart shape.
- `references/dataviz-color-palettes.md` — Sequential / divergent / categorical.
- `references/dataviz-maps.md` — Choropleth and map ergonomics.
- `references/dashboard-ergonomics.md` — Tile-by-tile dashboard layout.

**Design system**
- `references/ui-guidelines/INDEX.md` — Full map (foundations, patterns, components, inputs, platforms).
- `references/material-design.md` — Material 3 → skill-token mapping.
- `references/anti-patterns.md` — Visual + copy tells to refuse.
- `references/ux-psychology.md` — Applied cognitive principles.
- `references/ergonomics-criteria.md` — Eight ergonomic criteria for UX review.

## Assets

- `assets/starter-page.html` — single-file bootstrap (Tailwind Play CDN — prototype-grade; swap to Tailwind CLI / Vite before shipping a real production site).
- `assets/components/button.html`, `card.html`, `modal.html`, `form-field.html`, `nav.html`.
- `assets/components/chart-bar.json`, `chart-line.json` — Vega-Lite specs.
- `assets/fonts/roboto/` — Roboto WOFF2 + OFL + `fonts.css` (sans). The `fonts.css` declares the `@font-face` blocks and also exposes the `--font-sans / --font-serif / --font-mono` custom properties and the base `html { font-family: var(--font-sans) }` / `code, pre, kbd, samp { font-family: var(--font-mono) }` wiring.
- `assets/fonts/roboto-serif/` — Roboto Serif WOFF2 + OFL + `fonts.css` (serif).
- `assets/fonts/roboto-mono/` — Roboto Mono WOFF2 + OFL + `fonts.css` (code / monospace).
- The three-Roboto rule itself + the full wiring recipe (Tailwind config, `@import` ordering, HTML preload, fallback stacks) lives in `references/ui-guidelines/foundations/typography.md` — no per-asset README, per the Anthropic skill spec.

## Scripts

- `scripts/validate.py` — pre-ship quality gate. Stdlib only. Checks SKILL.md frontmatter, forbidden framework imports, marketing phrases, reference path resolution. Exit non-zero on any failure.
