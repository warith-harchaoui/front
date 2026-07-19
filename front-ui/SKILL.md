---
name: front-ui
description: >-
  Generate vanilla JavaScript + Tailwind CSS UI code — components, pages,
  forms, dialogs, dashboards — for solo developers and small teams shipping
  internal tools without a designer. Default typography is the three-Roboto
  rule (Roboto sans + Roboto Serif + Roboto Mono); honors user-specified fonts
  and respects existing typefaces when auditing existing UI. Output is
  semantic HTML + Tailwind utility classes + vanilla ES modules with dark-mode
  peers, focus rings, reduced-motion guards. Use it for "build a UI", "create
  a component", "design a page", "make a form / modal / button / nav",
  "scaffold a landing", "build a web app", "audit this UI", "dark mode
  toggle", "responsive layout", "dashboard / data table", "settings page",
  "empty state / skeleton", "i18n to YAML", "audit i18n". Companion skills:
  front-cli-gui (wrap a CLI in a GUI), front-publish (Markdown → website +
  meta tags + favicons), front-accessibility (a11y lint), front-colors
  (contrast audit, CVD), front-vision (alt text), front-audio (captions).
license: BSD-3-Clause
compatibility: >-
  Runtime: Claude.ai, Claude Code, OpenCode. No Python runtime required to use
  the skill itself (output is HTML + CSS + vanilla JS). Optional validator
  scripts/validate.py needs Python 3.9+ stdlib + PyYAML. Network access not
  required.
metadata:
  author: Warith Harchaoui
  version: 0.25.0
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
| Static HTML a11y lint | `front-accessibility` |
| WCAG contrast audit, CVD simulation, curated palette | `front-colors` |
| W3C alt text via local Ollama vision | `front-vision` |
| WebVTT / SRT captions via local whisper.cpp | `front-audio` |
| Apply / audit the canonical Laws of UX (Hick, Fitts, Miller, Jakob, Peak-End, …) on emitted HTML | `front-ux-laws` |

The companion skills assume the same stack rules below.

## Two modes — make and audit

This skill ships both halves of the front-* loop:

| Mode | Tool | Purpose |
|---|---|---|
| **Make** — generate UI | `references/` + `assets/components/*.html` + `assets/starter-page.html` + `assets/fonts/` + `scripts/i18n_make.py` | Generation playbook: token map, decision tree below, copy-and-adapt component shapes, three-Roboto webfonts. `i18n_make.py` scaffolds + compiles `locales/i18n.yaml` (GUI strings **and** prompts) and emits a vanilla-JS loader. |
| **Audit** — gate before ship | `scripts/validate.py` + `scripts/audit_i18n.py` + `references/checklist.md` + `references/anti-patterns.md` + `references/ergonomics-criteria.md` | Skill-spec validator (stdlib only); pre-ship quality gate; eight-criteria ergonomic review; anti-pattern refusal list. `audit_i18n.py` flags GUI translations embedded in JS/HTML and LLM prompts inlined in Python (they belong in `locales/i18n.yaml`). |

Pair with `front-ux-laws` for canonical-law audits and `front-colors`
for contrast / CVD audits on the emitted output.

### i18n — one `locales/i18n.yaml` for GUI *and* prompts

Translatable strings — GUI labels and LLM prompts — share one concern
(language), so they share one per-project catalog: **`locales/i18n.yaml`**
(`gui:` and `prompts:` namespaces, each `message.id → { en: …, fr: … }`).
Never hardcode a UI string in JavaScript, never inline a prompt in Python.

```bash
# make: scaffold locales/i18n.yaml, compile to locales/i18n.json, emit i18n.js
python scripts/i18n_make.py --dir .
# audit: flag any string/prompt living in code instead of the catalog
python scripts/audit_i18n.py src/          # I18N001 (JS dict) / I18N002 (py prompt)
```

In the browser: `import { initI18n, t } from "./locales/i18n.js"; await
initI18n(); el.textContent = t("action.save");`. In Python, load prompts from
the catalog (as the other skills load `prompts/*.yaml` via `_prompts`).

## Hard rules

1. **No framework imports.** Output never contains `react`, `vue`, `svelte`, `solid-js`, `next`, `nuxt`, `angular`. If asked, refuse and offer the vanilla equivalent.
2. **Tailwind utility classes only**, never inline `style="…"`. The single allowed exception is a one-off CSS custom property whose value references an existing token (e.g. `style="--accent: var(--brand-blue)"`). **Never** put a raw hex literal in markup — even inside `style="--accent: #007AFF"`. If a new accent is needed, add the token to `tailwind.config.js` (`theme.extend.colors.brand`) and reference it via `var(--brand-…)` or a Tailwind class. This keeps rule 7 (no raw hex) and rule 2 in lockstep.
3. **The three-Roboto rule — for generation, not for audits.** **When generating fresh UI / site output and no typeface has been specified by the user**, ship exactly three downloaded webfonts, all from the Roboto super-family: **Roboto** for sans, **Roboto Serif** for serif, **Roboto Mono** for code / monospace. No other downloaded family is allowed by default — not Inter, not Montserrat, not IBM Plex, not JetBrains Mono. Use Roboto for body / UI text by default; lift Roboto Serif when a surface wants editorial weight (longform reading, quote pulls, prose-heavy landings); use Roboto Mono for `<code>`, `<pre>`, kbd / samp, terminal panels. Self-host always (no Google Fonts CDN, no jsDelivr GH proxy in production builds); system-font fallback stacks (`ui-monospace`, `system-ui`, `serif`, `sans-serif`) are fine and expected. **The rule does NOT apply when:** (a) **auditing an existing site / UI** — respect the existing fonts; don't propose a font swap unless the user specifically asks about typography; (b) **the user names a typeface** ("use Inter", "we ship IBM Plex", "stick to system fonts") — use what they ask for; (c) **the user asks for a fourth family explicitly for brand reasons** — carry it out and record the choice in the project README so a future maintainer knows why.
4. **Semantic HTML first.** `<button>`, `<a href>`, `<label for>`, `<dialog>`, `<form>`. ARIA only when no semantic element fits.
5. **Both color schemes.** Every styled element gets a `dark:` peer.
6. **Accessibility is shipping-required.** See `references/ui-guidelines/foundations/accessibility.md`.
7. **No raw hex** in markup — use semantic Tailwind tokens (`bg-brand-blue`, `text-label-primary`). **Curated default — user colors win** (mirror of rule 3, but for palette): when generating fresh output and no palette has been specified, use the 8 saturated brand hues from `front-colors/references/palette.csv` (regenerable with `python front-colors/scripts/palette_to_tailwind.py`). **The default does NOT apply when:** (a) **auditing an existing UI** — respect the project's tokens; do not propose a CSV swap; (b) **the user names colors** ("our brand is #8B5CF6", "use Material's primary") — use those; (c) **the project already has a `tailwind.config.js`** with brand tokens — leave them alone unless asked. Either way, rule 7's "no raw hex in markup" still holds: add the user's color to the config as a token, then reference the token.
8. **Bilingual-ready copy** (EN/FR by default). The output language of the AI-backed scripts is **auto-detected from the input/context text** via `langdetect` — there is no configured default language. For translatable UI strings and prompts, use one `locales/i18n.yaml` catalog (see `front-ui/scripts/i18n_make.py` and `front-publish/references/i18n.md`).
9. **No third-party trademarks** in defaults (logos, product names, OS branding). Use generic, neutral language.

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
| "Laws of UX" / "Hick" / "Fitts" / "Miller" / "Jakob" / "Doherty" / "Tesler" / "Peak-End" / "Postel" / "Paradox of the Active User" | (see `front-ux-laws`) | Canonical Jon Yablonski set (30 laws). Reference: `front-ux-laws/references/laws-of-ux.md`. Auditor: `python front-ux-laws/scripts/audit_laws_of_ux.py <file-or-dir>`. |
| "IBAN field" / "success screen" / "checkout progress" / "loading skeleton" / "primary CTA" / "settings page" / "resume onboarding" / "form fields" | `assets/snippets/INDEX.md` | Law-keyed snippet catalog. Pick the snippet whose trigger phrase matches, copy-and-adapt the strings. Each snippet already carries dark-mode peers + focus rings + reduced-motion guards. |
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

Pair with `front-accessibility` for `lint_a11y.py` and `front-colors` for `audit_contrast.py` / `simulate_cvd.py` runs.

## Examples

Two worked shapes with the hard rules applied together (primary CTA button;
destructive confirm `<dialog>`) live in `references/examples.md`. The generic
per-surface primaries are in `assets/components/*.html`; the law-keyed catalog
is in `assets/snippets/INDEX.md`.

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
- `references/examples.md` — Two worked component shapes (CTA button, confirm dialog).

## Assets

- `assets/starter-page.html` — single-file bootstrap (Tailwind Play CDN — prototype-grade; swap to Tailwind CLI / Vite before shipping a real production site).
- `assets/components/button.html`, `card.html`, `modal.html`, `form-field.html`, `nav.html` — component-shape primaries (one file per generic UI surface).
- `assets/components/chart-bar.json`, `chart-line.json` — Vega-Lite specs.
- `assets/snippets/` — **law-keyed** snippet catalog (one file per mechanically-implementable Law of UX: Miller / Peak-End / Goal-Gradient / Doherty / Von Restorff / Jakob / Chunking / Zeigarnik). See `assets/snippets/INDEX.md` for the law ↔ snippet ↔ trigger-phrase mapping. Every snippet passes both `front-ux-laws` and `front-accessibility` auditors with zero findings — they are the make-side counterpart to `front-ux-laws/scripts/audit_laws_of_ux.py --fix`.
- `assets/fonts/roboto/` — Roboto WOFF2 + OFL + `fonts.css` (sans). The `fonts.css` declares the `@font-face` blocks and also exposes the `--font-sans / --font-serif / --font-mono` custom properties and the base `html { font-family: var(--font-sans) }` / `code, pre, kbd, samp { font-family: var(--font-mono) }` wiring.
- `assets/fonts/roboto-serif/` — Roboto Serif WOFF2 + OFL + `fonts.css` (serif).
- `assets/fonts/roboto-mono/` — Roboto Mono WOFF2 + OFL + `fonts.css` (code / monospace).
- The three-Roboto rule itself + the full wiring recipe (Tailwind config, `@import` ordering, HTML preload, fallback stacks) lives in `references/ui-guidelines/foundations/typography.md` — no per-asset README, per the Anthropic skill spec.

## Scripts

- `scripts/validate.py` — pre-ship quality gate. Stdlib only. Checks SKILL.md frontmatter, forbidden framework imports, marketing phrases, reference path resolution. Exit non-zero on any failure.
