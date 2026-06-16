---
name: front-ui
description: Generate vanilla JavaScript + Tailwind CSS UI code — components, pages, forms, dialogs, dashboards — for solo developers and small teams shipping internal tools without a designer. Default typeface Montserrat (swap to Inter for dense dev UI). Output is semantic HTML + Tailwind utility classes + vanilla ES modules with dark-mode peers, focus rings, reduced-motion guards. Use it for "build a UI", "create a component", "design a page", "make a form / modal / button / nav", "scaffold a landing", "build a web app", "audit this UI". Companion skills: front-cli-gui (wrap a CLI in a GUI), front-publish (Markdown → website + meta tags + favicons), front-a11y (a11y lint, contrast audit, alt text, captions).
license: Unlicense
metadata:
  author: Warith Harchaoui
  version: 0.2.0
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
2. **Tailwind utility classes only**, never inline `style="…"`. The single allowed exception is a one-off CSS custom property whose value is computed (e.g. `style="--accent: var(--brand-blue)"`). **Never** put a raw hex literal in markup — even inside `style="--accent: #007AFF"`. Define the token in CSS and reference it.
3. **Montserrat by default; Inter as the documented alternate.** Two choices, no more. Use Montserrat for marketing surfaces, prose-heavy pages, landing pages. Use Inter when the surface is dense (dashboards, admin panels, dev tools, data tables, monospace-adjacent UI) — Inter's larger x-height and hinting work better at small sizes. Self-host from `assets/fonts/` (no Google Fonts CDN). Document the choice in the project README.
4. **Semantic HTML first.** `<button>`, `<a href>`, `<label for>`, `<dialog>`, `<form>`. ARIA only when no semantic element fits.
5. **Both color schemes.** Every styled element gets a `dark:` peer.
6. **Accessibility is shipping-required.** See `references/ui-guidelines/foundations/accessibility.md`.
7. **No raw hex** in markup — use semantic Tailwind tokens (`bg-brand-blue`, `text-label-primary`).
8. **Bilingual-ready copy.** Default to English. Switch to the user's language when they write in it. Project-level pair is configurable — see `references/i18n.md` for setting up EN/FR, EN/DE, EN/ES, EN/JA, etc. (the previous EN/FR-only default has been dropped).
9. **No third-party trademarks** in defaults (logos, product names, OS branding). Use generic, neutral language.

## Build vs prototype

Tailwind has a build step. Two paths:

- **Prototype** (single-file demo, internal POC, throwaway): use the Tailwind Play CDN as shipped in `assets/starter-page.html`. Tailwind itself warns this is for prototyping only; do not ship it to production.
- **Production**: swap to **Tailwind CLI** (single command, no JS framework needed) or **Vite + Tailwind** if the project already uses Vite. See `references/stack-tailwind.md`.

The "zero build, drop into Nginx" pitch only holds for the prototype path. State which path you are on in the project README.

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
| "chart" / "graph" / "dashboard tile" | `charts-vega.md` + `dataviz-chart-selection.md` + `dataviz-color-palettes.md` | Vega-Lite v5 JSON spec, Montserrat, 10 px rounded corners, palette from `color-psychology.md`, no top/right spines. State polarity when well-defined (*↑ higher is better* / *↓ lower is better* / *target = N ± k*). |
| "dashboard" / "BI" / "KPI summary" | `dashboard-ergonomics.md` (+ chart references above) | One question per tile, title as a question, polarity tag on every measurable tile, sticky filters, 12-column grid, skeleton tiles while loading. |
| "map" / "choropleth" | `dataviz-maps.md` | Title states the message, ≤ 7 classes, locator inset, accessible text alternative below the map |
| "audit" / "ergonomic review" / "UX review" | `ergonomics-criteria.md` | Walk the 8 criteria: guidance, workload, explicit control, adaptability, error management, consistency, label significance, compatibility |
| "make it look less AI" / "designer review" | `anti-patterns.md` | Refuse gradient text, glassmorphism on body, side-stripe borders, "boost your productivity" copy, three-card grids |
| "psychology" / "conversion" / "flow not working" | `ux-psychology.md` | Pick ONE applicable principle per screen — Hick / Anchoring / Default Bias / Peak-End / Goal Gradient — and apply concretely |
| "material" / "Material 3" / "M3" | `material-design.md` | Map Material roles to skill tokens; emit plain HTML + Tailwind (no `mdc-*` classes) |

## Quality checklist (pre-ship)

Run `references/checklist.md` before returning code. Short version:

- [ ] No framework imports.
- [ ] Montserrat or Inter only; self-hosted.
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
- `references/stack-tailwind.md` — Config tokens, plugins, dark-mode strategy, Inter swap.
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

- `assets/starter-page.html` — single-file bootstrap (Tailwind Play CDN — prototype only).
- `assets/components/button.html`, `card.html`, `modal.html`, `form-field.html`, `nav.html`.
- `assets/components/chart-bar.json`, `chart-line.json` — Vega-Lite specs.
- `assets/fonts/montserrat/` — Montserrat WOFF2 + OFL + `fonts.css`.
- `assets/fonts/inter/` — Inter WOFF2 + OFL + `fonts.css` (alternate font; bundle separately or point at official source).

## Scripts

- `scripts/validate.py` — pre-ship quality gate. Stdlib only. Checks SKILL.md frontmatter, forbidden framework imports, marketing phrases, reference path resolution. Exit non-zero on any failure.
