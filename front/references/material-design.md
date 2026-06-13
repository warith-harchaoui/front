# Material Design 3 — distilled

Canonical source: <https://m3.material.io/>. This file captures the principles, tokens, and component behaviours that translate cleanly into the skill's stack (vanilla JS + Tailwind + Montserrat). Where Material's spec disagrees with the rest of the skill (specifically: typeface, branding, color tokens), the skill's choices win.

Read alongside `ui-guidelines/foundations/color.md`, `ui-guidelines/foundations/motion.md`, `ui-guidelines/foundations/elevation.md` (see below), and `charts-vega.md`.

## Principles

1. **Adaptive.** A single interface that responds to size, input modality, and theme. Mobile, tablet, desktop, light, dark — all served by the same components.
2. **Expressive.** Color, shape, and motion carry brand. Avoid the default-grey aesthetic.
3. **Personal.** The user can tune the system (dynamic color, theme, density). Respect the user's preferences over the designer's defaults.

## Color system

Material 3 organizes color into **roles**, not raw hues. The skill maps these to its own tokens (in `color-psychology.md` and `ui-guidelines/foundations/color.md`); the table below shows the mapping.

| Material 3 role | This skill's token | Use |
|---|---|---|
| `primary` | `brand-blue` | Main accent, primary CTAs, focus rings |
| `on-primary` | white text on `brand-blue` | Text/icons on primary surfaces |
| `primary-container` | `brand-blue-light` | Filled containers tied to the primary action |
| `secondary` | `brand-purple` (or another accent) | Less prominent components |
| `tertiary` | `brand-turquoise` | Contrasting accents in dense UI |
| `error` | `brand-red` | Destructive / error |
| `surface` | `surface-primary` | Default surfaces |
| `surface-container` (low / high) | `surface-secondary` / `surface-tertiary` | Elevated containers without shadows |
| `on-surface` | `label-primary` | Body text |
| `on-surface-variant` | `label-secondary` | Secondary text, icons, separators |
| `outline` | `separator` | Borders and dividers |

### Dynamic color
Material 3 generates a full tonal palette from a single source color. The skill does the equivalent statically: each brand hue ships with `DEFAULT`, `dark`, and `light` variants (`color-psychology.md`). The skill does not auto-extract color from user images.

## Typography

Material 3 defines five scales (display / headline / title / body / label) with three sizes each (large / medium / small). The skill collapses to a smaller, named set built on Montserrat (`ui-guidelines/foundations/typography.md`). Mapping:

| Material 3 | This skill | Tailwind |
|---|---|---|
| Display large/medium/small | Display / Title 1 | `text-5xl` / `text-4xl` |
| Headline large/medium/small | Title 2 / Title 3 | `text-2xl` / `text-xl` |
| Title large/medium/small | Headline | `text-[17px] font-semibold` |
| Body large/medium/small | Body / Callout / Subhead | `text-[17px]` / `text-base` / `text-[15px]` |
| Label large/medium/small | Footnote / Caption | `text-[13px]` / `text-xs` |

Material 3's reference type is Roboto (Roboto Flex). The skill uses Montserrat instead — it's the only typeface allowed.

## Shape

Material 3 uses a corner-radius scale. The skill's mapping:

| Material 3 | px | Tailwind |
|---|---|---|
| None | 0 | `rounded-none` |
| Extra small | 4 | `rounded` |
| Small | 8 | `rounded-lg` |
| Medium | 12 | `rounded-xl` |
| Large | 16 | `rounded-2xl` |
| Extra large | 28 | `rounded-3xl` |
| Full | half-height | `rounded-full` |

Skill house defaults: pill buttons (`rounded-full`), cards `rounded-2xl`, inputs `rounded-xl`, chart tiles `rounded-[10px]`. Avoid `rounded-3xl` on small components.

## Elevation (without shadows)

Material 3 moved away from heavy shadows. Surfaces are differentiated by **tonal elevation** (slightly lighter / darker color) plus an optional 1 dp outline. The skill follows the same approach:

| Material 3 elevation | This skill |
|---|---|
| Level 0 | `surface-primary` |
| Level 1 | `surface-secondary` |
| Level 2 | `surface-secondary` + `border border-separator/40` |
| Level 3 | `surface-tertiary` |
| Level 4–5 | `surface-tertiary` + `shadow-sm` (modals, popovers only) |

Solid `shadow-lg` belongs on transient overlays only (popover, menu). Cards stay flat.

## Motion

Material 3's "emphasized" easing is `cubic-bezier(0.2, 0.0, 0, 1.0)`. The skill uses near-equivalents (`ease-native`, `ease-standard`) — see `ui-guidelines/foundations/motion.md`. Duration scale:

| Material 3 token | ms | Skill use |
|---|---|---|
| Short 1 | 50 | Hover tint |
| Short 2 | 100 | Press scale, simple toggles |
| Medium 1 | 250 | Modal reveal |
| Medium 2 | 300 | Sheet rise, page transition |
| Long 1 | 450 | Hero element transitions |
| Long 2 | 500 | Cross-screen container transform |

Anything > 500 ms feels sluggish; the skill caps interactions at 500 ms.

## Components — mapping table

When Claude is asked for a "Material X component", emit the skill's equivalent rather than a Material-branded one. The mapping:

| Material 3 component | Skill equivalent | Reference |
|---|---|---|
| Filled / Tonal / Outlined / Elevated / Text Button | Primary / Secondary / Tertiary Button | `ui-guidelines/components/buttons.md` |
| Floating Action Button (FAB) | Skip in most cases; the skill prefers a bottom-anchored primary button on mobile. If needed, a circular `rounded-full bg-brand-blue` button | `ui-guidelines/components/buttons.md` |
| Top App Bar (small / center-aligned / medium / large) | Sticky `<header>` with `backdrop-blur-ultra` | `ui-guidelines/components/navigation-bars.md` |
| Bottom App Bar / Navigation Bar | Sticky bottom tab bar | `ui-guidelines/components/tab-bars.md` |
| Navigation Drawer | Off-canvas `<dialog>` from the start edge | `ui-guidelines/components/sheets.md` |
| Navigation Rail (tablet/desktop) | Sidebar with icon + label, hidden on mobile | `ui-guidelines/components/navigation-bars.md` + `ui-guidelines/platforms/desktop.md` |
| Text Field (Filled / Outlined) | The skill's outlined input (`form-field.html`) | `ui-guidelines/components/text-fields.md` |
| Card (Filled / Outlined / Elevated) | `rounded-2xl bg-surface-secondary` (filled) or with `border-separator/40` (outlined). No elevated variant. | `assets/components/card.html` |
| Dialog (Basic / Full-screen) | Native `<dialog>` | `ui-guidelines/components/alerts.md` + `sheets.md` |
| Bottom Sheet (Modal / Standard) | `<dialog>` bottom-anchored | `ui-guidelines/components/sheets.md` |
| Snackbar | Toast banner with live region | `ui-guidelines/patterns/feedback.md` |
| Banner | Top inline banner | `ui-guidelines/patterns/feedback.md` |
| Chips (Assist / Filter / Input / Suggestion) | Pill buttons / toggles | `ui-guidelines/components/segmented-controls.md` |
| Menu | `<details>` or native `popover` | `ui-guidelines/components/menus.md` |
| Tabs (Primary / Secondary) | Top tab strip; not the same as bottom tab bar | n/a (deferred — emit a horizontal segmented control) |
| Switch | Toggle with `role="switch"` | `ui-guidelines/components/toggles.md` |
| Slider | Native `<input type="range">` | `ui-guidelines/components/sliders.md` |
| Progress Indicator (Linear / Circular) | `<progress>` or animated spinner | `ui-guidelines/components/progress-indicators.md` |
| Date / Time Picker | Native `<input type="date|time">` | `ui-guidelines/components/pickers.md` |
| Tooltip | Native `title` attribute on icon-only buttons, or anchored popover | `ui-guidelines/components/popovers.md` |
| Badge | `inline-flex items-center rounded-full px-2 py-0.5 text-xs` over a parent with `relative` positioning | n/a |
| Icon Button | `aria-label`'d icon-only button | `ui-guidelines/components/buttons.md` |
| Search | `<input type="search">` with debounce | `ui-guidelines/patterns/searching.md` |

## Accessibility — alignment

Material 3 mandates the same things the skill does:

- Touch target minimum 48 dp ≈ 48 px (skill: 44 px — slightly tighter, still WCAG-compliant; raise to 48 if the project targets Material parity).
- Color contrast WCAG AA minimum (≥ 4.5:1 body, ≥ 3:1 large/UI).
- Focus indicators must be visible at all times via keyboard.
- Respect `prefers-reduced-motion`, dynamic type, and color scheme.

The skill's checklist (`references/checklist.md`) satisfies all of these.

## Writing tone

Material 3's voice rules align with the skill's `ui-guidelines/foundations/writing.md`: concise, clear, helpful; sentence case; verb-first buttons; no "OK" on consequential actions. No conflict.

## When to consult this file

- The user names a Material component ("filled tonal button", "navigation drawer", "FAB").
- The user mentions Material Design or "M3" by name.
- A migration from a Material-built UI to vanilla JS.
- Designers comparing the skill's output against Material conventions.

The skill does not emit Material-branded class names (`mdc-button`, `md-list-item`) or import the Material Web Components. The output is plain HTML + Tailwind that *behaves* like the Material equivalent.

## Checklist

- [ ] Material role → skill token mapped (table above), no raw Material color hex.
- [ ] Montserrat (not Roboto) in the type stack.
- [ ] Corner-radius from the skill's set, not Material's full 7-step scale.
- [ ] Elevation via surface color, not shadow (except transient overlays).
- [ ] Touch target ≥ 44 px (≥ 48 px if Material parity matters).
- [ ] Motion durations within the skill's caps (≤ 500 ms per interaction).
- [ ] No Material Web Components or `mdc-*` classes shipped.
