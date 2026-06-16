# Stack — Tailwind CSS

This skill emits Tailwind utility classes for all styling. Two valid setups:

- **Play CDN** (`assets/starter-page.html` uses this) — zero-config, fine for prototypes.
- **Built CSS via Tailwind CLI or Vite** — recommended for production.

## Typography — default, alternate, and custom swap

The `fontFamily.sans` token defaults to **Montserrat**. Montserrat is
not always the perfect choice — language coverage, brand identity, and
small-size legibility on dense UIs are real reasons to pick something
else. Two supported escape hatches:

1. **Documented alternate — Inter.** Drop the WOFF2 files into
   `assets/fonts/inter/` and set
   `sans: ['Inter Variable', 'Inter', 'sans-serif']` in
   `tailwind.config.js`. Inter has a larger x-height and stronger
   hinting at 12–14 px, which fits dashboards, admin panels, dev tools
   and data-heavy surfaces better than Montserrat.

2. **User-supplied custom family.** Ship a folder under
   `assets/fonts/<family>/` containing the TTF or WOFF2 files plus the
   license (OFL.txt, license.txt, …). Then in three places:

   - `tailwind.config.js` — change `fontFamily.sans` to your family.
   - `src/styles/app.css` — replace `@import` of the Montserrat CSS
     with the equivalent `@font-face` block for your family (variable
     axis preferred when available; otherwise the four static weights
     400 / 500 / 600 / 700 with matching italic if relevant).
   - Project README — record which family is in use and why, so a
     future maintainer does not have to read the CSS to find out.

   Every other rule (semantic tokens, dark-mode peers, focus ring,
   reduced-motion guard, 44 × 44 hit area) stays unchanged.

**Always self-host.** No Google Fonts CDN in production. The jsDelivr
`gh` proxy is acceptable for a prototype with a self-hosted fallback;
production builds should ship the WOFF2 / TTF files alongside the
HTML. Run the validator (`front-ui/scripts/validate.py`) after any
font swap — it does not check the family itself but it catches the
forbidden raw-hex / framework-import regressions a font swap can
accidentally introduce.

## Tailwind config (drop into `tailwind.config.js`)

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js}', './index.html'],
  darkMode: ['class', '[data-color-scheme="dark"]'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Montserrat', 'sans-serif'],
        mono: ['ui-monospace', 'monospace'],
      },
      colors: {
        brand: {
          blue:      { DEFAULT: '#007AFF', dark: '#0A84FF', light: '#CCE4FF' },
          red:       { DEFAULT: '#FF3B30', dark: '#FF453A', light: '#FFD8D6' },
          green:     { DEFAULT: '#28CD41', dark: '#30D158', light: '#D4F5D9' },
          orange:    { DEFAULT: '#FF9500', dark: '#FF9F0A', light: '#FFEACC' },
          yellow:    { DEFAULT: '#FFCC00', dark: '#FFD60A', light: '#FFF5CC' },
          purple:    { DEFAULT: '#AF52DE', dark: '#BF5AF2', light: '#EFDCF8' },
          pink:      { DEFAULT: '#FF2D55', dark: '#FF375F', light: '#FFD5DD' },
          turquoise: { DEFAULT: '#79DBDC', dark: '#64D2FF', light: '#00FFEF' },
        },
        label: {
          primary:        { DEFAULT: '#000000' },
          'primary-dark':   '#FFFFFF',
          secondary:      { DEFAULT: 'rgba(60,60,67,0.6)' },
          'secondary-dark': 'rgba(235,235,245,0.6)',
          tertiary:       { DEFAULT: 'rgba(60,60,67,0.3)' },
          'tertiary-dark':  'rgba(235,235,245,0.3)',
        },
        surface: {
          primary:          { DEFAULT: '#FFFFFF' },
          'primary-dark':     '#000000',
          secondary:        { DEFAULT: '#F2F2F7' },
          'secondary-dark':   '#1C1C1E',
          tertiary:         { DEFAULT: '#FFFFFF' },
          'tertiary-dark':    '#2C2C2E',
        },
        separator: 'rgba(60,60,67,0.36)',
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      backdropBlur: {
        'ultra':   '20px',
        'thin':    '24px',
        'regular': '32px',
        'thick':   '40px',
      },
      transitionTimingFunction: {
        'native':        'cubic-bezier(0.32, 0.72, 0, 1)',
        'native-spring': 'cubic-bezier(0.5, 1.6, 0.4, 0.7)',
        'standard':      'cubic-bezier(0.4, 0, 0.2, 1)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};
```

## Base CSS (`src/styles/app.css`)

```css
@import url('../fonts/montserrat/fonts.css');

@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root { color-scheme: light dark; }
  html, body { @apply bg-surface-primary text-label-primary; }
  html[data-color-scheme="dark"], html[data-color-scheme="dark"] body {
    @apply bg-surface-primary-dark text-label-primary-dark;
  }
  *:focus { outline: none; }
  *:focus-visible {
    @apply ring-2 ring-brand-blue ring-offset-2 ring-offset-surface-primary;
  }
  html[data-color-scheme="dark"] *:focus-visible {
    @apply ring-offset-surface-primary-dark;
  }
}

@layer components {
  .h-display  { @apply text-5xl font-bold tracking-tight; }
  .h-title-1  { @apply text-4xl font-bold tracking-tight; }
  .h-title-2  { @apply text-2xl font-semibold tracking-tight; }
  .h-title-3  { @apply text-xl font-semibold; }
  .h-headline { @apply text-[17px] font-semibold; }
  .t-body     { @apply text-[17px] leading-relaxed; }
  .t-callout  { @apply text-base; }
  .t-subhead  { @apply text-[15px]; }
  .t-footnote { @apply text-[13px] text-label-secondary dark:text-label-secondary-dark; }
  .t-caption  { @apply text-xs text-label-tertiary dark:text-label-tertiary-dark; }
}
```

## Dark mode strategy

`darkMode: ['class', '[data-color-scheme="dark"]']` lets the theme switcher in `references/stack-vanilla-js.md` flip themes via a single attribute on `<html>`. System changes are forwarded by the JS unless the user has set an explicit override.

## Plugins

- **`@tailwindcss/forms`** — sane defaults for form controls (consistent across browsers).
- **`@tailwindcss/typography`** — `prose` classes for long-form content.

## Conventions

1. **Semantic tokens only.** Never `bg-[#007AFF]` — always `bg-brand-blue`.
2. **`dark:` peer for every meaningful color utility** — no orphan light-only classes.
3. **Spacing scale** — `0.5 / 1 / 2 / 3 / 4 / 5 / 6 / 8 / 10 / 12 / 16`. No `gap-7`, no `p-9`.
4. **Order of utilities**: layout → spacing → sizing → typography → color → effects → state. Use Prettier with `prettier-plugin-tailwindcss` to enforce.
5. **No `@apply` outside `@layer components`** — keep one source of truth.
6. **Group rare bespoke styles in `@layer components`** — don't bury 30 utilities on one element.

## Productivity utilities to know

| Utility | Use |
|---|---|
| `sr-only` | Visually hide while leaving accessible |
| `motion-reduce:` | Wrap any translate/scale |
| `backdrop-blur-ultra` | Translucent chrome |
| `tabular-nums` | Numeric columns |
| `prose dark:prose-invert` | Long-form content |
| `aspect-video` / `aspect-square` | Reserve image space |
| `min-h-dvh` | Full viewport, mobile-safe |
| `ps-*` / `pe-*` / `ms-*` / `me-*` | RTL-safe spacing |
