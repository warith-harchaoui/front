# Foundations — Typography

## When to consult this file

- Picking sizes, weights, line heights
- Building a type scale
- Auditing readability

## The font: Montserrat (only)

This skill uses **Montserrat** as the sole typeface family across UI chrome, body, and display. No other faces unless the user explicitly overrides. Monospace is the only allowed sibling, for code blocks.

- License: SIL Open Font License (OFL) — free for commercial use.
- Source: <https://fonts.google.com/specimen/Montserrat>
- Self-host the WOFF2 files (don't load from a third-party CDN) for performance + privacy.

### Self-hosting recipe

1. Download Montserrat from Google Fonts → "Get font" → "Download all".
2. Keep WOFF2 only. Ship four weights max: 400 (regular), 500 (medium), 600 (semibold), 700 (bold). Add 800 only if a marketing display surface needs it.
3. Place under `/fonts/montserrat/`.
4. Declare with `font-display: swap` so the system fallback renders immediately.

```css
@font-face {
  font-family: 'Montserrat';
  font-style: normal;
  font-weight: 400 700;          /* variable-axis range if using the .var file */
  font-display: swap;
  src: url('/fonts/montserrat/Montserrat-Variable.woff2') format('woff2-variations'),
       url('/fonts/montserrat/Montserrat-Regular.woff2') format('woff2');
}
```

If using the variable font, ship a single file and let `font-weight: 400|500|600|700` drive the axis. Otherwise ship four files (`Montserrat-Regular`, `-Medium`, `-SemiBold`, `-Bold`) and four `@font-face` blocks.

### CSS variables

```css
:root {
  --font-sans: 'Montserrat', sans-serif;
  --font-mono: ui-monospace, monospace;
}
html { font-family: var(--font-sans); }
code, pre, kbd, samp { font-family: var(--font-mono); }
```

The fallback stack only renders if Montserrat fails — the FOUT (flash of unstyled text) is intentional and acceptable.

### Tailwind config

```js
// tailwind.config.js
theme: {
  extend: {
    fontFamily: {
      sans: ['Montserrat', 'sans-serif'],
      mono: ['ui-monospace', 'monospace'],
    },
  },
},
```

`font-sans` (Tailwind default) already maps to Montserrat after this override. Authors never need to call out the family explicitly.

### HTML preload (optional but recommended)

```html
<link rel="preload" href="/fonts/montserrat/Montserrat-Variable.woff2" as="font" type="font/woff2" crossorigin>
```

## Core principles

- **One face, focused weights.** 400 / 500 / 600 / 700 cover all of chrome and body. Don't import the full 18-weight family.
- **Define a small set of styles.** Don't ad-hoc sizes. Build a scale with semantic names (`display`, `title`, `headline`, `body`, `subhead`, `footnote`, `caption`).
- **Respect user font-size preferences** — use `rem` and let `html { font-size: 100% }` honor user settings.
- **Body 16–17 px** desktop, 16 px minimum mobile.
- **Line height proportional to size**: tight for display (`1.1–1.2`), generous for body (`1.5–1.6`).
- **Line length** 45–75 characters — `max-w-prose` in Tailwind.
- **Hierarchy through weight and size, not color.** Subtle color shifts are secondary cues.
- **Tracking (letter-spacing)** tightens slightly for large display sizes. Montserrat sits well at `tracking-tight` for titles ≥ 24 px.

## Type scale

Built on `rem`. Authors should use Tailwind utility classes — every step has a name.

| Role | Size (rem / px) | Weight | Line-height | Tailwind |
|---|---|---|---|---|
| Display | 2.75 / 44 | 700 | 1.1 | `text-5xl font-bold tracking-tight` |
| Title 1 | 2 / 32 | 700 | 1.15 | `text-4xl font-bold tracking-tight` |
| Title 2 | 1.5 / 24 | 700 | 1.2 | `text-2xl font-semibold tracking-tight` |
| Title 3 | 1.25 / 20 | 600 | 1.25 | `text-xl font-semibold` |
| Headline | 1.0625 / 17 | 600 | 1.4 | `text-[17px] font-semibold` |
| Body | 1.0625 / 17 | 400 | 1.5 | `text-[17px]` |
| Callout | 1 / 16 | 400 | 1.4 | `text-base` |
| Subhead | 0.9375 / 15 | 400 | 1.4 | `text-[15px]` |
| Footnote | 0.8125 / 13 | 400 | 1.4 | `text-[13px]` |
| Caption 1 | 0.75 / 12 | 400 | 1.3 | `text-xs` |
| Caption 2 | 0.6875 / 11 | 400 | 1.3 | `text-[11px]` |

## Concrete rules

1. **Montserrat only.** No second display face unless the user explicitly overrides.
2. **At most four weights** in use: 400 / 500 / 600 / 700.
3. **Numeric tables** use tabular figures: `font-variant-numeric: tabular-nums` (Tailwind: `tabular-nums`).
4. **Avoid all caps for body**; allow it sparingly for very short labels with letter-spacing.
5. **Italic for true emphasis only**, not for decoration. Montserrat italics are available — use them, don't fake-slant.
6. **Wrap long words** with `overflow-wrap: anywhere` (Tailwind `break-words`) inside narrow containers.

## Pattern — typography component classes (Tailwind `@layer components`)

```css
@layer components {
  .h-display   { @apply text-5xl font-bold tracking-tight; }
  .h-title-1   { @apply text-4xl font-bold tracking-tight; }
  .h-title-2   { @apply text-2xl font-semibold tracking-tight; }
  .h-headline  { @apply text-[17px] font-semibold; }
  .t-body      { @apply text-[17px] leading-relaxed; }
  .t-callout   { @apply text-base; }
  .t-subhead   { @apply text-[15px]; }
  .t-footnote  { @apply text-[13px] text-label-secondary; }
  .t-caption   { @apply text-xs text-label-tertiary; }
}
```

## Checklist

- [ ] Montserrat self-hosted as WOFF2.
- [ ] Only weights 400 / 500 / 600 / 700 shipped.
- [ ] `font-display: swap` on every `@font-face`.
- [ ] Tailwind `font-sans` resolves to Montserrat first.
- [ ] Body text ≥ 16 px.
- [ ] Line length 45–75 ch on long-form pages.
- [ ] No more than ~6 distinct sizes in use across the page.
- [ ] Hierarchy works without color (test in grayscale).
- [ ] Tabular numerals on tables / counters.
- [ ] Headings use real `<h1>`–`<h6>` in order.
