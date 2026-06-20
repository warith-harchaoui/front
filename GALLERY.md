# Gallery

Sites and tools shipped with the `front-*` skill suite. Each entry is
a real, public surface — not a mock or a screenshot of the demo
component library. Light and dark variants are captured headlessly so
the dark-mode peer rule is visibly enforced.

Markdown-based by design: every entry lives in this file, every
screenshot lives under `assets/gallery/<slug>/`, every link points to
the live URL. No CMS, no separate showcase site, no build step.

To submit a new entry, see [Adding to the gallery](#adding-to-the-gallery)
at the bottom of this file.



## [A Practical Python Environment for Artificial Intelligence](https://harchaoui.org/warith/4ml)

> *A practical webpage for Python environment in AI, ML, CV and NLP — install, tooling and conventions for AI, ML, CV and NLP, written for AI scientists, students and lab teams.*

A long-form, single-page guide aimed at AI scientists, students and
small lab teams setting up a Python environment for ML / CV / NLP
work. It walks through the "what should I install today?" question
with concrete defaults (CUDA vs Apple Silicon, environment managers,
core stack, training vs inference tooling) and a contents-driven
table-of-contents navigation pattern instead of a sidebar.

Why it earns its place as the first gallery entry: dense long-form
content with a sticky table of contents, multi-section structure,
strict semantic HTML, dark-mode peer on every block, and the same
Tailwind token system the skill emits — built and shipped without a
framework runtime.

| Light | Dark |
|---|---|
| ![4ml — light](assets/gallery/4ml/light.png) | ![4ml — dark](assets/gallery/4ml/dark.png) |

**Author:** [Warith Harchaoui](https://linkedin.com/in/warith-harchaoui)  ·  **Stack:** vanilla JS + Tailwind 



## [md2star — Markdown → branded `.docx` / `.pptx` / `.pdf`](https://github.com/warith-harchaoui/md2star)

> *Convert Markdown into branded `.docx`, `.pptx`, and `.pdf`, end to end.*

A cross-platform CLI + local web GUI that wraps **Pandoc** with a
curated styling layer: a single `.md` file becomes a polished Office
document. The CLI (`md2docx`, `md2pptx`, `md2star`) does the
non-interactive case; `md2star gui` launches the local editor —
folder browser on the left, CodeMirror Markdown editor in the middle,
live PDF.js preview on the right, auto-render 2.5 s after typing pause
with `⌘↵` / `Ctrl ↵` to force.

Why this entry matters for the gallery: md2star is the concrete
**CLI → GUI** target the `front-cli-gui` skill was designed for —
real CLI surface, real local web GUI, dark-mode peer on every panel,
no framework runtime. The Tauri shell that will wrap it as a desktop
applicatif is on the [roadmap](CHANGELOG.md#roadmap); the local-web
GUI shown below is what's live today.

| Light | Dark |
|---|---|
| ![md2star — light](assets/gallery/md2star/light.png) | ![md2star — dark](assets/gallery/md2star/dark.png) |

**Author:** [Warith Harchaoui](https://linkedin.com/in/warith-harchaoui)  ·  **Stack:** Python CLI + vanilla JS / CodeMirror / PDF.js GUI  

