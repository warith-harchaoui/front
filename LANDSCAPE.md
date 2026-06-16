# Landscape — alternatives to `front`

`front` is one opinionated answer to a wide question: *how should an LLM produce frontend code?* This file maps the alternatives in every category the four skills touch as **matrices** — rows are tools, columns are characteristics you actually care about. Use it to choose with eyes open.

## A note on bias

This file is written by the author of `front`. The "Skill alignment" column flags whether each alternative aligns with what `front` emits — it does not claim `front` is better than every alternative. Read it as "does this row fit inside `front`'s emitted output" or "is this row a reasonable companion." Most alternatives are excellent at what they do; if the row gets a ✗ it's usually because `front` made a different design choice (e.g. no React, no framework-tied design system), not because the alternative is worse.

Two categories where `front` is genuinely a strong pick:

1. **CLI → GUI for solo / small-team Python projects** that need a real HTML deliverable (not a Streamlit/Gradio runtime) and want to avoid picking up React. See § 7.
2. **Pre-commit a11y + contrast gates in CI without a browser**. The static gates in `front-a11y` complement (do not replace) runtime audits like axe-core or Pa11y. See § 9, § 10.

Most other categories: there is a better tool if you specialize. The matrices below name it explicitly.

## Legend

- **✓** yes / built-in
- **~** partial / requires config
- **✗** no
- **N/A** doesn't apply to this row's category

Costs are MIT/Apache-permissive unless otherwise noted. Stack column lists the language a developer of the tool writes against — not the underlying engine.

---

## Quick pick

What kind of work are you doing? Find the row and the honest recommendation.

| You want… | `front` skill | When to pick something else |
|---|---|---|
| Vanilla JS + Tailwind UI output, no framework | `front-ui` | If the team has already picked React/Vue/Svelte. `front` refuses to emit framework code; you'd be fighting it. |
| React + design system stack | none | [shadcn/ui](https://ui.shadcn.com), [Mantine](https://mantine.dev), [MUI](https://mui.com). shadcn is closest in philosophy (copy-paste, no runtime lock-in). |
| Material-3 native look | none | [Material Web Components](https://material-web.dev) for first-party Material; `front-ui/references/material-design.md` only maps Material roles into the skill's tokens. |
| Wrap a Python / Node / Go CLI in a web GUI | `front-cli-gui` | If you want auto-form-from-signature with no UI control: [Gradio](https://gradio.app) (ML demos), [Streamlit](https://streamlit.io) (data apps), [Taipy](https://taipy.io). `front-cli-gui` scaffolds plain HTML you edit — those tools give you a runtime UI you cannot easily restyle. |
| Wrap a CLI as a native desktop app binary | `front-cli-gui` (UI) + Tauri (shell) | [Tauri](https://tauri.app) is the desktop shell; `front-cli-gui` emits what goes inside the web view. If you only need the desktop, Tauri's defaults are fine. |
| Build a docs site from a small README + `docs/` | `front-publish` | For 100+ versioned pages or for a docs site with side-by-side per-release views: [MkDocs Material](https://squidfunk.github.io/mkdocs-material/), [Hugo](https://gohugo.io), [Astro](https://astro.build), [Docusaurus](https://docusaurus.io). `front-publish` is for small projects (< 30 pages). |
| Declarative JSON charts with a house style | `front-ui` | For bespoke / 3D / scientific charts: [D3](https://d3js.org), [Plotly](https://plotly.com), [Three.js](https://threejs.org). `front-ui` ships Vega-Lite v5 specs. |
| A11y lint in CI without a browser | `front-a11y` | This is a pre-commit gate. For runtime DOM audits (post-JS, dynamic ARIA, focus order after async): [axe-core](https://github.com/dequelabs/axe-core), [Pa11y](https://pa11y.org), Lighthouse. Pair both. |
| Local-only alt-text drafting | `front-a11y` | For top-quality hosted alt-text: [Claude vision](https://docs.claude.com/en/docs/build-with-claude/vision), [GPT-4o vision](https://platform.openai.com/docs/guides/vision), [Gemini Vision](https://ai.google.dev/gemini-api/docs/vision). Hosted is more accurate; local is free and private. |
| Local CPU-friendly captions | `front-a11y` | For real-time live captions: [Deepgram](https://deepgram.com), [AssemblyAI](https://www.assemblyai.com). `front-a11y` uses whisper.cpp — fast on CPU, not live. |
| Marketing landing page | none | Webflow, Framer, or a design agency. `front` enforces a stack that's optimized for clarity, not brand differentiation. |
| Custom visual identity for a consumer app | none | Hire a designer. `front` uses one palette family and two fonts on purpose. |

---

## 1. JavaScript framework / no-framework

`front` refuses to emit framework code. These are the alternatives if a framework is the right call.

| Alternative | Runtime size (min+gz) | Build step | Component model | SSR | A11y reputation | Skill alignment | Notes |
|---|---|:---:|---|:---:|---|:---:|---|
| **`front` (vanilla JS + Tailwind)** | 0 KB framework + Tailwind CSS | optional | native elements + `customElements` | N/A | strong by default | ✓ | What this skill emits. |
| [React](https://react.dev) | ~45 KB | ✓ | JSX components | ✓ (Next, Remix) | needs Radix / Headless UI | ✗ | Largest ecosystem, biggest payload. |
| [Vue](https://vuejs.org) | ~34 KB | ✓ | SFC `<template>` | ✓ (Nuxt) | good | ✗ | Closer to HTML than JSX. |
| [Svelte / SvelteKit](https://svelte.dev) | ~10 KB | ✓ | `.svelte` SFCs | ✓ | good | ✗ | Smallest runtime among the big three. |
| [Solid](https://www.solidjs.com) | ~7 KB | ✓ | JSX, fine-grained reactivity | ✓ | OK | ✗ | React mental model, smaller payload. |
| [Qwik](https://qwik.dev) | "0 KB" (resumable) | ✓ | JSX components | ✓ | OK | ✗ | Best TTI on cold loads. |
| [Preact](https://preactjs.com) | ~4 KB | ✓ | JSX components | ✓ | OK | ✗ | React API, smaller. |
| [Lit](https://lit.dev) | ~6 KB | optional | Web Components | ✓ | good | ~ | `front` *will* emit `customElements.define` when justified. |
| [HTMX](https://htmx.org) | ~14 KB | ✗ | server-driven HTML swaps | ✓ | good | ~ | Pairs well with `front` — HTMX for nav, `front` for client details. |
| [Alpine.js](https://alpinejs.dev) | ~7 KB | ✗ | attribute-driven sprinkles | N/A | OK | ~ | "jQuery for 2020s". Same spirit, attribute-first instead of module-first. |

---

## 2. CSS approach

| Alternative | Output | Build step | Class style | Design tokens | Dark-mode UX | Skill alignment | Notes |
|---|---|:---:|---|---|---|:---:|---|
| **Tailwind CSS** (used) | atomic utilities | ✓ | `bg-brand-blue text-label-primary` | semantic via config | first-class `dark:` peer | ✓ | What `front` uses. |
| [UnoCSS](https://unocss.dev) | atomic utilities | ✓ | Tailwind-compatible + presets | semantic | first-class | ~ | Drop-in faster alternative. |
| [Bootstrap](https://getbootstrap.com) | component classes | ~ | `btn btn-primary` | named-color | mode classes | ✗ | Quick start; uniform look. |
| [Bulma](https://bulma.io) | component classes | ✗ | `button is-primary` | named-color | toggle CSS | ✗ | Like Bootstrap, smaller surface. |
| [Pico CSS](https://picocss.com) | classless on semantic tags | ✗ | none | none | auto | ✗ | Excellent for prose, weak for apps. |
| [Open Props](https://open-props.style) | CSS vars (tokens only) | ✗ | BYO methodology | named tokens | toggle | ~ | Pairs with plain CSS. |
| [vanilla CSS + BEM](https://getbem.com) | hand-written | ✗ | `.block__elem--mod` | manual | manual | ✗ | Longest-lived; slowest to write. |
| [CSS Modules](https://github.com/css-modules/css-modules) | scoped CSS | ✓ | hash-suffixed | manual | manual | ✗ | Standard in many React monorepos. |
| [Panda CSS](https://panda-css.com) | zero-runtime CSS-in-JS | ✓ | recipes / patterns | typed tokens | first-class | ✗ | Strong in TS apps. |
| [vanilla-extract](https://vanilla-extract.style) | zero-runtime CSS-in-JS | ✓ | typed stylesheets | typed tokens | first-class | ✗ | TS-only friendly. |

---

## 3. Component library / design system

| Alternative | Stack | Distribution | A11y rep | Visual identity | Cost | Skill alignment | Notes |
|---|---|---|---|---|---|:---:|---|
| **`front/assets/components/`** (used) | HTML + Tailwind | copy-paste files | strong | this skill's tokens | free | ✓ | Lives in markup, no dependency. |
| [shadcn/ui](https://ui.shadcn.com) | React + Tailwind + Radix | copy-paste CLI | strong (via Radix) | neutral, themable | free | ~ | Closest philosophy; React-only. |
| [Headless UI](https://headlessui.com) | React / Vue | npm | strong | bring your own | free | ✗ | Behaviour only. |
| [Radix UI](https://www.radix-ui.com) | React | npm | best in class | neutral | free | ✗ | Primitives, not visuals. |
| [Ark UI](https://ark-ui.com) | React / Vue / Solid | npm | strong | none | free | ✗ | Framework-agnostic Radix-like. |
| [DaisyUI](https://daisyui.com) | Tailwind plugin | npm | OK | named themes | free | ✗ | Component classes on top of Tailwind. |
| [Flowbite](https://flowbite.com) | Tailwind + JS | npm | OK | named | freemium | ✗ | Pre-built widgets. |
| [MUI](https://mui.com) | React | npm | strong | Material 3 | free / paid pro | ✗ | Largest React design system. |
| [Mantine](https://mantine.dev) | React | npm | strong | neutral | free | ✗ | Big surface, sensible defaults. |
| [Chakra UI](https://chakra-ui.com) | React | npm | strong | neutral | free | ✗ | Same league as Mantine. |
| [Carbon](https://carbondesignsystem.com) | React / web components | npm | strong | IBM | free | ✗ | Inside the IBM ecosystem. |
| [Fluent UI](https://react.fluentui.dev) | React | npm | strong | Microsoft | free | ✗ | Inside the Microsoft ecosystem. |
| [Primer](https://primer.style) | React / CSS / Rails | npm/gem | strong | GitHub | free | ✗ | Inside GitHub. |
| [Polaris](https://polaris.shopify.com) | React | npm | strong | Shopify | free | ✗ | Inside Shopify. |
| [Lightning](https://www.lightningdesignsystem.com) | LWC / React | npm | strong | Salesforce | free | ✗ | Inside Salesforce. |
| [Shoelace / Web Awesome](https://shoelace.style) | Web Components | npm | strong | neutral | free | ~ | Framework-agnostic; closest if you want `<sl-button>` over hand-rolled. |

---

## 4. Typography (UI typeface)

| Font | Weights | Latin Ext. / Cyrillic | License | Variable | Cost | Skill alignment | Notes |
|---|---|---|---|:---:|---|:---:|---|
| **Montserrat** (used) | 100–900 + italics | both | OFL | ✓ | free | ✓ | Self-hosted in `assets/fonts/montserrat/`. |
| [Inter](https://rsms.me/inter/) | 100–900 + italics | both | OFL | ✓ | free | ~ | Industry default for SaaS UI. |
| [IBM Plex Sans](https://www.ibm.com/plex/) | 100–700 | both | OFL | ~ | free | ~ | Neutral corporate. |
| [Roboto Flex](https://fonts.google.com/specimen/Roboto+Flex) | variable | both | Apache | ✓ | free | ~ | Material default. |
| System UI stack | OS-dependent | OS-dependent | none | depends | free | ~ | Zero bytes, no brand. |
| [Geist](https://vercel.com/font) | 100–900 | Latin | OFL | ✓ | free | ✗ | Newer geometric sans (Vercel). |
| [Satoshi](https://www.fontshare.com/fonts/satoshi) | 300–900 | Latin | proprietary (free) | ✓ | free | ✗ | Fontshare licence specifics differ. |
| [Manrope](https://manrope.org) | 200–800 | Latin | OFL | ✓ | free | ✗ | Modern geometric. |
| [Atkinson Hyperlegible](https://www.brailleinstitute.org/freefont/) | 4 weights | Latin | OFL | ✗ | free | ~ | Best for low-vision readers; pairs as accessibility font. |

---

## 5. Colour system

| Alternative | Shape | A11y workflow | Dark mode | Source | Skill alignment | Notes |
|---|---|---|---|---|:---:|---|
| **`front` palettes** (used) | 4 named palettes + semantic tokens | manual + `audit_contrast.py` | first-class | <https://harchaoui.org/warith/colors/> | ✓ | Choice / Emotion / Concept / Psychology. |
| [Tailwind defaults](https://tailwindcss.com/docs/customizing-colors) | scales (slate, sky, …) | manual | toggle | inhouse | ~ | Strong ecosystem look. |
| [Radix Colors](https://www.radix-ui.com/colors) | 12-step semantic scales | per-step intent (1=bg, 12=text) | mirror dark scale | inhouse | ~ | Best for stateful UIs. |
| [Open Color](https://yeun.github.io/open-color/) | 13-step palette | manual | manual | inhouse | ~ | Minimal. |
| [Material 3 Dynamic](https://m3.material.io/styles/color/system/overview) | algorithmic | enforced roles | first-class | Google | ~ | Seed-derived; native on Android. |
| [Apple system colors](https://developer.apple.com/design/human-interface-guidelines/color) | semantic roles | per-role guidance | first-class | Apple HIG | ~ | Several of `front`'s tokens are direct lifts. |
| [Spectrum (Adobe)](https://spectrum.adobe.com/page/color-system/) | semantic + scales | strong WCAG docs | first-class | Adobe | ✗ | Inside Adobe ecosystem. |
| [Carbon palettes](https://carbondesignsystem.com/elements/color/overview/) | semantic + scales | strong | first-class | IBM | ✗ | Inside Carbon. |
| [OKLCH](https://oklch.com) | colour space, not palette | underpins fix-suggestion | N/A | spec | ✓ | What `audit_contrast.py --fix` uses. |

---

## 6. Dataviz library

| Library | Form | Bundle | Renderer | Declarative | 3D | Skill alignment | Notes |
|---|---|---|---|:---:|:---:|:---:|---|
| **Vega-Lite v5** (used) | JSON grammar | ~200 KB (vega+lite+embed) | Canvas / SVG | ✓ | ✗ | ✓ | What `front` emits. |
| [Vega](https://vega.github.io/vega/) | JSON grammar | ~140 KB | Canvas / SVG | ✓ | ✗ | ~ | Lower-level than Vega-Lite. |
| [Observable Plot](https://observablehq.com/plot/) | JS API | ~70 KB | SVG | ✓ | ✗ | ~ | Grammar-of-graphics, same authors. |
| [D3.js](https://d3js.org) | JS toolkit | ~40 KB (core) | SVG / Canvas | ✗ | ✗ | ✗ | Bespoke charts; high floor. |
| [Chart.js](https://www.chartjs.org) | JS config | ~50 KB | Canvas | ~ | ✗ | ✗ | Quick start, less flexible. |
| [ECharts](https://echarts.apache.org/) | JS config | ~200 KB | Canvas | ~ | ~ | ✗ | Dense BI dashboards. |
| [Plotly.js](https://plotly.com/javascript/) | JS config | ~3 MB | WebGL / Canvas | ✓ | ✓ | ✗ | Scientific + 3D. |
| [ApexCharts](https://apexcharts.com) | JS config | ~120 KB | SVG | ~ | ✗ | ✗ | Polished defaults. |
| [Highcharts](https://www.highcharts.com) | JS config | ~250 KB | SVG | ~ | ✗ | ✗ | Commercial licence. |
| [µPlot](https://github.com/leeoniya/uPlot) | JS config | ~50 KB | Canvas | ~ | ✗ | ✗ | Huge time-series perf. |
| [Recharts](https://recharts.org) | React | npm | SVG | ✓ | ✗ | ✗ | React-only. |
| [Three.js](https://threejs.org), [Babylon.js](https://www.babylonjs.com) | JS API | ~600 KB+ | WebGL | ✗ | ✓ | ✗ | 3D / WebGL. |

---

## 7. CLI → GUI host

| Host | Stack | Binary size | Native IPC | Web layer | Skill alignment | Notes |
|---|---|---|:---:|:---:|:---:|---|
| **HTTP + SSE (FastAPI / Express / Hono)** | Python / Node | server only | N/A | ✓ | ✓ | Pattern in `assets/examples/cli-gui-demo/`. |
| [Tauri](https://tauri.app) | Rust + system webview | ~3–10 MB | ✓ | ✓ | ✓ | Best when shipping the CLI as a desktop app. |
| [Electron](https://www.electronjs.org) | Chromium + Node | ~100 MB+ | ✓ | ✓ | ~ | Biggest ecosystem, heaviest binary. |
| [Wails](https://wails.io) | Go + system webview | ~10 MB | ✓ | ✓ | ✓ | Tauri-equivalent for Go CLIs. |
| [Neutralino](https://neutralino.js.org), [NW.js](https://nwjs.io) | system webview / Chromium | ~2–50 MB | ✓ | ✓ | ~ | Niche but real. |
| [PyWebView](https://pywebview.flowrl.com) | Python desktop webview | small | ✓ | ✓ | ~ | Lightweight Python alternative. |
| [Gradio](https://gradio.app) | Python form-gen | server only | N/A | auto | ✗ | Best for ML demos, weak ergonomic control. |
| [Streamlit](https://streamlit.io) | Python script-first | server only | N/A | auto | ✗ | Same niche as Gradio. |
| [Shiny](https://shiny.posit.co) | R / Python | server only | N/A | auto | ✗ | Statistical apps. |
| [Gooey](https://github.com/chriskiehl/Gooey) | argparse → wxPython | desktop, native | N/A | ✗ | ✗ | Native widgets, no web. |
| [dearpygui](https://dearpygui.readthedocs.io) | Python + Dear ImGui | desktop, native | N/A | ✗ | ✗ | Game-style immediate-mode UI. |
| [Textual](https://textual.textualize.io), [Bubble Tea](https://github.com/charmbracelet/bubbletea) | Python / Go | TUI | N/A | ✗ | ✗ | Pick if a TUI is the right answer. |

---

## 8. Markdown → website (SSG)

| Generator | Language | Theme model | Build speed | Plug-ins | Skill alignment | Notes |
|---|---|---|---|---|:---:|---|
| **`front` Markdown → website workflow** | Pandoc / Node / Python | per-project HTML+Tailwind | depends | — | ✓ | Emits theme assets; not a runtime. |
| [Hugo](https://gohugo.io) | Go | Go templates | fastest in class | ✓ | ~ | `front` can supply the theme. |
| [Jekyll](https://jekyllrb.com) | Ruby | Liquid | slow | ✓ | ~ | GitHub Pages default. |
| [Eleventy](https://www.11ty.dev) | Node | many engines | fast | ✓ | ~ | Most flexible. |
| [Astro](https://astro.build) | Node | components + islands | fast | ✓ | ~ | Bring-your-own-framework. |
| [Docusaurus](https://docusaurus.io) | React | React + MDX | medium | ✓ | ✗ | React-based docs sites. |
| [VitePress](https://vitepress.dev) | Vue | Vue + MD | fast | ✓ | ✗ | Vue-based docs sites. |
| [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) | Python | Material theme | fast | ✓ | ~ | De-facto Python project docs. |
| [mdBook](https://rust-lang.github.io/mdBook/) | Rust | book theme | fast | ~ | ~ | Book-shape sites. |
| [Pandoc](https://pandoc.org) | Haskell | templates | per-file | ~ | ✓ | `front`'s default MD→HTML pipe. |
| [Quarto](https://quarto.org) | Pandoc-based | templates | medium | ✓ | ~ | Scientific publishing. |

---

## 9. Accessibility lint / audit

| Tool | Layer | Browser required | Stack | Rules | License | Skill alignment | Notes |
|---|---|:---:|---|---|---|:---:|---|
| **`scripts/lint_a11y.py`** (used) | static source | ✗ | Python stdlib | 14 | Unlicense | ✓ | Pre-commit gate. |
| [axe-core](https://github.com/dequelabs/axe-core) | runtime DOM | ✓ | JS | 100+ | MPL-2 | ~ | Industry standard. |
| [Pa11y](https://pa11y.org) | runtime + CI | ✓ | Node | wraps axe / HTML_CodeSniffer | LGPL | ~ | Headless runs. |
| [Lighthouse](https://developer.chrome.com/docs/lighthouse) | runtime + perf | ✓ | Node | a11y category + perf | Apache | ~ | DevTools bundled. |
| [WAVE](https://wave.webaim.org/api/) | runtime | ✓ | hosted | curated | proprietary | ✗ | Famous browser extension. |
| [html-validate](https://html-validate.org) | static source | ✗ | Node | HTML semantics | MIT | ~ | Weaker on WCAG. |
| [HTMLHint](https://htmlhint.com) | static source | ✗ | Node | general HTML | MIT | ~ | General HTML, not WCAG-focused. |
| [eslint-plugin-jsx-a11y](https://www.npmjs.com/package/eslint-plugin-jsx-a11y) | static source | ✗ | Node | React | MIT | ✗ | JSX only; `front` doesn't emit JSX. |

Pair `scripts/lint_a11y.py` (static, in CI) with axe-core (runtime, in browser tests).

---

## 10. Contrast / colour-blindness audit

| Tool | Form | Live preview | CI-friendly | License | Skill alignment | Notes |
|---|---|:---:|:---:|---|:---:|---|
| **`scripts/audit_contrast.py`** (used) | CLI + OKLCH fix suggester | ✗ | ✓ | Unlicense | ✓ | Walks every label/surface pair. |
| **`scripts/simulate_cvd.py`** (used) | CLI image transform | ✗ | ✓ | Unlicense | ✓ | Protanopia / deuteranopia / tritanopia. |
| [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/) | hosted page | ✗ | ✗ | free | ~ | Canonical reference. |
| [Stark](https://www.getstark.co) | Figma / Sketch plugin | ✓ | ✗ | freemium | ✗ | Designer workflow. |
| [Sim Daltonism](https://michelf.ca/projects/sim-daltonism/) | macOS overlay | ✓ | ✗ | free | ~ | Live CVD preview. |
| [Polypane](https://polypane.app) | browser | ✓ | ~ | paid | ✗ | Dev browser with a11y panels. |
| [TPGi Colour Contrast Analyser](https://www.tpgi.com/color-contrast-checker/) | desktop app | ✓ | ✗ | free | ~ | Picker-based. |
| [axe DevTools color contrast](https://www.deque.com/axe/) | DOM panel | ✓ | ~ | freemium | ~ | Pairs with axe-core. |

---

## 11. Alt-text helper

| Helper | Run location | Model | Lang control | Cost / call | License | Skill alignment | Notes |
|---|---|---|---|---|---|:---:|---|
| **`scripts/alt_from_ollama.py`** (used) | local CPU/GPU | Gemma 4 vision (~e2b) via Ollama | `--lang` + project doc | $0 | Unlicense | ✓ | Offline, predictable. |
| [Claude vision API](https://docs.claude.com/en/docs/build-with-claude/vision) | hosted | Claude | prompt | paid | proprietary | ~ | Top quality, hosted. |
| [GPT-4o vision](https://platform.openai.com/docs/guides/vision) | hosted | OpenAI | prompt | paid | proprietary | ✗ | Top quality, hosted. |
| [Gemini Vision](https://ai.google.dev/gemini-api/docs/vision) | hosted | Google | prompt | paid | proprietary | ✗ | Top quality, hosted. |
| [Azure AI Vision](https://learn.microsoft.com/azure/ai-services/computer-vision/) | hosted | proprietary | prompt | paid | proprietary | ✗ | Mature, polished output. |
| [Google Cloud Vision](https://cloud.google.com/vision) | hosted | proprietary | prompt | paid | proprietary | ✗ | Mature, polished output. |
| [AWS Rekognition](https://aws.amazon.com/rekognition/) | hosted | proprietary | prompt | paid | proprietary | ✗ | AWS-aligned. |
| [BLIP / LLaVA / MiniCPM-V](https://huggingface.co/docs/transformers/model_doc/llava) | local GPU | open weights | prompt | $0 | varied | ~ | Self-host alternatives. |
| [CapAlt](https://capalt.com), [AltGen](https://github.com/Mateo-Wallace/AltGen) | hosted / FE plug-in | depends | depends | varies | varies | ✗ | Purpose-built tools. |

---

## 12. Captions / transcripts

| Tool | Run location | Model | Speed (CPU, p95) | Live | Vocabulary biasing | License | Skill alignment | Notes |
|---|---|---|---|:---:|:---:|---|:---:|---|
| **`scripts/captions_from_whisper.py`** (used) | local | `large-v3-turbo` via pywhispercpp | fast | ✗ | ✓ | Unlicense | ✓ | Auto-picks vocab from project. |
| [OpenAI Whisper](https://github.com/openai/whisper) | local | many sizes | slow on CPU | ✗ | ~ | MIT | ~ | Reference impl. |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | local | CTranslate2 | 4–8× faster | ✗ | ~ | MIT | ~ | Same models, faster engine. |
| [whisper.cpp](https://github.com/ggml-org/whisper.cpp) | local | GGML | fastest C++ | ✗ | ~ | MIT | ~ | Engine under pywhispercpp. |
| [insanely-fast-whisper](https://github.com/Vaibhavs10/insanely-fast-whisper) | local GPU | `transformers` + Flash Attention | very fast on GPU | ✗ | ~ | Apache | ✗ | GPU-only. |
| [Deepgram](https://deepgram.com) | hosted | proprietary | real-time | ✓ | ✓ | proprietary | ✗ | Polished, paid. |
| [AssemblyAI](https://www.assemblyai.com) | hosted | proprietary | real-time | ✓ | ✓ | proprietary | ✗ | Same league. |
| [Rev.ai](https://www.rev.ai) | hosted | proprietary | near real-time | ~ | ✓ | proprietary | ✗ | Strong English. |
| [Otter](https://otter.ai) | hosted | proprietary | real-time | ✓ | ~ | proprietary | ✗ | Consumer-focused. |
| [Aeneas](https://github.com/readbeyond/aeneas) | local | force-aligner | fast | ✗ | N/A | AGPL | ~ | Aligns *existing* transcripts — different problem. |

---

## 13. Static-site indexes (sitemap / feed / llms.txt)

| Tool | Outputs | Stack | Build step | SSG-agnostic | License | Skill alignment | Notes |
|---|---|---|:---:|:---:|---|:---:|---|
| **`scripts/site_indexes.py`** (used) | robots.txt, sitemap.xml, llms.txt, Atom/RSS, humans.txt | Python stdlib | ✗ | ✓ | Unlicense | ✓ | One-shot, no deps. |
| [sitemap npm](https://www.npmjs.com/package/sitemap) | sitemap | Node | ✓ | ✓ | MIT | ~ | One-purpose. |
| [python-sitemap](https://github.com/c4software/python-sitemap) | sitemap | Python | ✗ | ✓ | MIT | ~ | One-purpose. |
| [feedgen](https://feedgen.kiesow.be/) | Atom/RSS | Python | ✗ | ✓ | LGPL | ~ | Feeds only. |
| [feed npm](https://www.npmjs.com/package/feed) | Atom/RSS/JSON Feed | Node | ✓ | ✓ | MIT | ~ | Feeds only. |
| SSG built-ins (Hugo, Jekyll, Astro, Eleventy) | sitemap + feed | varies | ✓ | ✗ | varied | ~ | Tied to the SSG. |
| [llmstxt.org spec](https://llmstxt.org) | the format itself | — | — | ✓ | spec | ✓ | Format spec, no generator by design. |

---

## 14. Anthropic skill / agent ecosystem

| Slot | What it does | Skill alignment | Notes |
|---|---|:---:|---|
| **`front`** | Frontend (this skill) | ✓ | Vanilla JS + Tailwind + Montserrat + dataviz + a11y. |
| Claude Code built-in commands | `/init`, `/review`, `/security-review`, ultrareview | ✓ | Active alongside `front`; no conflict. |
| Other Claude skills (marketplace) | Domain-specific tools | ~ | Layer with `front` when the domain is non-frontend. |
| [OpenCode](https://opencode.ai) | Alternative runtime for the same skill format | ✓ | Named in `README.md` install path. |
| Hand-prompting (no skill) | Whatever you write | ~ | Works for one-shots, drifts across sessions. |

---

## Further reading

- [The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — the spec `front` is built to.
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) — the source for several of `front`'s ergonomics.
- [Material Design 3](https://m3.material.io) — distilled in `front/references/material-design.md`.
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) — the accessibility baseline the skill targets.
- [WAI Image Tutorial](https://www.w3.org/WAI/tutorials/images/) — the alt-text decision tree behind `alt_from_ollama.py`.
- [llmstxt.org](https://llmstxt.org) — the spec the `llms.txt` at the repo root follows.
