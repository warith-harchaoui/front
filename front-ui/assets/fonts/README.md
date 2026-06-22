# Fonts — the three-Roboto rule

`front-ui` ships **exactly three downloaded web families**, all from the
Roboto super-family:

| Role             | Family         | Folder           |
| ---------------- | -------------- | ---------------- |
| Sans (default)   | Roboto         | `roboto/`        |
| Serif            | Roboto Serif   | `roboto-serif/`  |
| Code / monospace | Roboto Mono    | `roboto-mono/`   |

No other downloaded family is allowed — not Inter, not Montserrat, not
JetBrains Mono, not IBM Plex. If a project needs a display look, render
it with Roboto Serif weight / size changes. System-font fallback stacks
(`ui-monospace`, `system-ui`, etc.) are fine and expected.

## Why one family

The Roboto super-family was designed to share metrics, x-height, and
visual rhythm across sans / serif / mono. Sticking to one designer keeps
prose-heavy and code-heavy surfaces typographically coherent and trims
the WOFF2 payload (~290 KB total for all three latin-subset variables).

## What's in each folder

Each family ships two WOFF2 files:

- `*-Variable.woff2`           — upright, weights 100–900 axis
- `*-Italic-Variable.woff2`    — italic,  weights 100–900 axis

…plus its upstream `OFL.txt` (SIL Open Font License 1.1).

The WOFF2 files are the latin-subset variable build served by Google
Fonts (see `fetch.py` in commit history for the script). For broader
script coverage (Cyrillic, Greek, Vietnamese, …) ship the matching
subset files alongside, scoped by `unicode-range` — see
`front-publish/references/i18n.md`.

## Wiring it in

`fonts.css` in each folder defines the `@font-face` blocks. In
`roboto/fonts.css` the `:root` block also exposes
`--font-sans`, `--font-serif`, `--font-mono` and wires `html` + `code`
selectors. Import the three CSS files from your stylesheet:

```css
@import url('./assets/fonts/roboto/fonts.css');
@import url('./assets/fonts/roboto-serif/fonts.css');
@import url('./assets/fonts/roboto-mono/fonts.css');
```

For Tailwind, set `fontFamily.sans = ['Roboto', 'sans-serif']`,
`fontFamily.serif = ['Roboto Serif', 'serif']`, and
`fontFamily.mono = ['Roboto Mono', 'ui-monospace', 'monospace']`. See
`front-ui/references/stack-tailwind.md` § *"Typography — the three-Roboto rule"*.

## Provenance

| Family       | Upstream                                                     | License           |
| ------------ | ------------------------------------------------------------ | ----------------- |
| Roboto       | <https://github.com/googlefonts/roboto-3-classic>            | SIL OFL 1.1       |
| Roboto Serif | <https://github.com/googlefonts/RobotoSerif>                 | SIL OFL 1.1       |
| Roboto Mono  | <https://github.com/googlefonts/RobotoMono>                  | SIL OFL 1.1       |

Self-host only — do not load from `fonts.googleapis.com` /
`fonts.gstatic.com` in production builds.
