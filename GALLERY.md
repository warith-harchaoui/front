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
document. The CLI (`md2docx`, `md2pptx`, `md2pdf`) does the
non-interactive case; the live editor shown below is the
**Overleaf-style split pane** — Markdown source on the left, PDF
preview on the right, debounced 500 ms after typing with `⌘ Enter` /
`Ctrl Enter` to force. The render pipeline is the same one the CLI
uses: `md2docx` to produce the .docx, then headless LibreOffice
(`soffice --convert-to pdf`) to render the preview.

Why this entry matters for the gallery: md2star is the concrete
**CLI → GUI** target the `front-cli-gui` skill was designed for —
real CLI surface, real local web GUI, dark-mode peer on every panel,
no framework runtime. The split-pane editor is stdlib-only (Python's
`http.server` for the backend, vanilla ES module + Tailwind Play CDN
for the front end) and passes both `front-ux-laws` and
`front-accessibility` audits with zero findings on the emitted HTML.
The Tauri shell that will wrap it as a desktop application is on the
[roadmap](CHANGELOG.md#roadmap); the local-web GUI shown below is
what's live today.

| Light | Dark |
|---|---|
| ![md2star — light](assets/gallery/md2star/light.png) | ![md2star — dark](assets/gallery/md2star/dark.png) |

**Author:** [Warith Harchaoui](https://linkedin.com/in/warith-harchaoui)  ·  **Stack:** Python stdlib HTTP server + vanilla JS + Tailwind + `md2docx` + headless LibreOffice



## Adding to the gallery

The gallery is part of the repo on purpose — entries land via pull request, get reviewed like code, and ship with the next release. There is no separate showcase site or CMS to log into.

### Criteria for inclusion

A new entry has to clear all four:

1. **Real and public.** A reachable URL (or a public source repo for tools that ship as binaries / libraries). No mockups, no Figma exports, no "behind a private VPN" screenshots.
2. **Built on the `front-*` stack.** Vanilla JavaScript + Tailwind CSS, semantic HTML, dark-mode peer on every styled element, focus rings, reduced-motion guards. The typography choice does not have to be the three-Roboto default — per `front-ui/SKILL.md` hard rule 3 (as of 0.6.4), existing sites and projects that name their own typeface are not held to that rule.
3. **Both color schemes captured.** Headless screenshots of the same surface in light and dark mode, so the `dark:` peer rule is visibly enforced. If a site does not implement dark mode, it does not earn a gallery slot — that is the canary the gallery is here to police.
4. **Author named and contactable.** A real human, with a public profile link (LinkedIn / personal site / GitHub) so a reader can verify provenance.

### Submission steps

1. **Pick a slug** in `kebab-case`, ≤ 24 chars, matching the project name (`4ml`, `md2star`, …). The slug is the URL fragment and the folder name under `assets/gallery/`, so it should be stable for the life of the entry.
2. **Capture screenshots** at 1440×900 (desktop) in both color schemes. Headless capture with Playwright / Puppeteer / `pageres` is fine; manual screenshots are fine; the only rule is that the two captures show the same surface. Crop to the meaningful viewport — no browser chrome.
3. **Save them** as `assets/gallery/<slug>/light.png` and `assets/gallery/<slug>/dark.png`. PNG, ≤ 1 MB each (compress with `pngquant` or `oxipng` if you need to). No `.heic`, no `.webp` until both formats render reliably in every Markdown viewer.
4. **Write the entry** in `GALLERY.md` following the template below. Put it in chronological order (newest at the bottom) unless you have a reason to feature it.
5. **Open a PR** with the new entry + the two screenshot files. The PR description should link the live URL and confirm the four criteria above.

### Entry template

Copy this block, replace the bracketed placeholders, and append to the bottom of this file:

```markdown
## [PROJECT TITLE — short tagline](LIVE-URL)

> *One-sentence quote — the project's own tagline, or a single line summarising what it does. Keep it under ~30 words.*

ONE-PARAGRAPH DESCRIPTION (≤ 100 words). What the surface does, who
it serves, what's interesting about how it ships.

Why it earns its place in the gallery: ONE-SENTENCE RATIONALE that
names a specific rule the entry exemplifies (semantic HTML, dark-mode
peer, no framework runtime, CLI → GUI flagship, accessibility-first
copy, …).

| Light | Dark |
|---|---|
| ![SLUG — light](assets/gallery/SLUG/light.png) | ![SLUG — dark](assets/gallery/SLUG/dark.png) |

**Author:** [NAME](PROFILE-URL)  ·  **Stack:** SHORT-STACK-SUMMARY
```

### What gets a PR rejected

- Marketing-voice copy ("revolutionizes", "seamlessly", "production-grade", "non-negotiable") in the description. The skill's anti-patterns reference is the canonical list.
- Screenshots with cookie banners, dev-tools open, or browser chrome cropped in. Capture the surface, not the browser.
- Light/dark captures showing different content (different scroll position, different copy, different time of day). They have to be the same surface.
- Entries for surfaces still on `localhost` or behind auth at the time of the PR. Wait until the site is reachable to a reader who clicks the link.
- Entries for the `front-*` skills themselves. The gallery showcases what people *ship* with the skills, not the skills themselves — those have their own README + LANDSCAPE.

