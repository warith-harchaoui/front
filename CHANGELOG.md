# Changelog

All notable changes to `front` will be recorded here. Dates are ISO-8601.

The project follows a loose [SemVer](https://semver.org/) — major version
bumps mean the on-disk skill layout changes (users have to re-copy folders
into `~/.claude/skills/`).

## [0.2.0] — 2026-06-16

### Changed — the big restructure

- **Split the single `front/` skill into four focused skills.** The
  previous `front/SKILL.md` had a description listing twelve trigger
  phrases (build a UI, wrap this CLI, turn markdown into a site, audit,
  alt text, captions, favicons, meta, site indexes, plain language,
  contrast, CVD). Activation was sloppy and maintenance compounded.
  The new layout:
  - `front-ui/` — UI generation core (stack rules, components, design
    system, checklist, dataviz). Always install.
  - `front-cli-gui/` — CLI → GUI flagship.
  - `front-publish/` — Markdown → website + meta + favicons + site
    indexes + plain language.
  - `front-a11y/` — a11y lint + contrast audit + CVD sim + alt text +
    captions.
- **Install path changed.** Users previously copied
  `cp -r front ~/.claude/skills/front`. Now they pick the skills they
  need: `cp -r front-ui ~/.claude/skills/front-ui` plus optional
  companion folders. Existing installs should be removed first.

### Added — audience and positioning

- **Picked a real audience.** Solo developers and small teams (≤ 5)
  shipping internal tools — dev dashboards, admin panels, ML / data
  demos, CLI wrappers, research showcases. Documented "not for X" cases
  (consumer brand, marketing pages, framework-led teams, large versioned
  docs).
- **Honest CLI → GUI positioning.** Added "Why this skill, not Gradio /
  Streamlit / Tauri / Taipy" with concrete tradeoffs. The flagship
  scaffolds the GUI and ships a Python SSE proxy reference; it does not
  replace runtimes like Gradio's auto-form for ML demos.
- **Honest a11y framing.** `lint_a11y.py` is now framed as a fast
  pre-commit gate, not a replacement for axe-core / Pa11y / Lighthouse.
  `audit_contrast.py --fix` is framed as a designer hint, not a final
  decision.

### Added — typography

- **Inter is now an accepted alternate font** (Montserrat default; Inter
  for dense dev / dashboard / admin / data surfaces). Hard rule 3 in
  every SKILL.md is updated. Two choices, no more.

### Added — i18n

- **Bilingual default is now language-pair-configurable.** The previous
  EN/FR-only baking has been dropped from SKILL.md. Projects can declare
  their pair (EN/FR, EN/DE, EN/ES, EN/JA, …) and the skill follows.
  See `front-publish/references/i18n.md` for the configuration recipe.

### Added — hygiene

- `CHANGELOG.md` (this file).
- `CONTRIBUTING.md`.
- `version: 0.2.0` in every SKILL.md.
- Top-level `README.md` rewritten around the four-skill structure and
  the real audience.
- `LANDSCAPE.md` preamble made honest about the comparison bias (see
  also § 1 "Quick pick" prose).

### Fixed — rule contradiction

- The previous SKILL.md hard rule 2 (Tailwind classes only) explicitly
  allowed `style="--accent: #007AFF"`, which violated rule 7 (no raw hex
  in markup). The new rule 2 forbids hex literals even inside CSS
  custom-property exceptions; semantic tokens are required.
- The previous SKILL.md sold "drops into GitHub Pages / Netlify / S3 /
  plain Nginx" without naming the Tailwind build step. New rule 3 in
  every SKILL.md is explicit about the prototype-vs-production path.

### Internal

- `meta_from_ollama.py` was importing from `alt_from_ollama.py`. With
  the split, these now live in different skills. The shared bits
  (`OLLAMA_URL`, `LANG_INSTRUCTIONS`, `detect_lang`,
  `pick_default_model`) were extracted into a small `_ollama.py` helper
  that lives in both `front-a11y/scripts/` and `front-publish/scripts/`.
- `tests/conftest.py` was updated to add all three skill `scripts/`
  directories to `sys.path`.
- `tests/test_validate.py` now invokes `front-ui/scripts/validate.py`.

### Deferred to a future release

- **Public-data tests for the AI-backed scripts.** `alt_from_ollama.py`,
  `meta_from_ollama.py`, `plain_language.py` and
  `captions_from_whisper.py` still have no test coverage. Adding
  cassette-style tests with public-domain fixtures is the next step.
- **Full reshaping of references/.** SKILL.md is now instruction-shaped
  in each skill, but the reference files still mix teaching prose with
  rule-shaped content. A future pass will move the teaching prose into
  clearly-labelled sections (or split files into `*-rules.md` and
  `*-guide.md`).
- **`LISEZMOI.md`.** The French README has not yet been brought into
  parity with the new EN README. Translation pass deferred.
- **Optional Click-based top-level driver.** See `.private/click.md`
  for the analysis. A `front-cli/` package with a unified `front` command
  is the next ergonomic improvement.

## [0.1.0] — 2025

Initial public release: single `front/` skill folder with twelve trigger
phrases, EN/FR bilingual defaults, Montserrat-only typography, ~70
reference files, 14 Python scripts.
