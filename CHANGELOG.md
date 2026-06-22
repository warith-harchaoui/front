# Changelog

All notable changes to `front` will be recorded here. Dates are ISO-8601.

The project follows a loose [SemVer](https://semver.org/) — major version
bumps mean the on-disk skill layout changes (users have to re-copy folders
into `~/.claude/skills/`).

## Releases

Each tagged release publishes five tarballs on GitHub Releases (one per
skill plus a bundle of all four) and a single `SHA256SUMS` covering
every artifact. Users download the bundle (or a per-skill tarball),
run `shasum -a 256 -c SHA256SUMS` to verify it, extract, and copy the
folders they need into `~/.claude/skills/`. The README's *Install*
section walks the full flow. To upgrade, repeat the steps with a newer
`VERSION` — the on-disk folder name is stable so the copy overwrites in
place. If the checksum check fails, do not install the artifact.
Release tarballs are produced by `scripts/release.sh <version>`.

## [0.6.1] — 2026-06-22 — CI + release workflow fixes

Patch release. No skill content changes. Repairs the two GitHub
Actions workflows that broke during the v0.6.0 publish.

### Fixed — `ci` workflow (failing since v0.5.0)

`front-publish/scripts/requirements-narrate-openvoice.txt` pins
`openvoice @ git+https://github.com/myshell-ai/OpenVoice.git@main`,
but upstream renamed the package's `pyproject.toml` metadata name
from `openvoice` to `myshell-openvoice` between v0.5.0 and v0.6.1.
Modern pip rejects the mismatch with `Requested myshell-openvoice
from git+… has inconsistent name: expected 'openvoice', but metadata
has 'myshell-openvoice'`, which broke the install step on every push
to `main` since the audio-narration feature landed.

`narrate_openvoice.py` and `narrate_chatterbox.py` both `importlib`
their backend lazily inside functions, so neither package is needed
for `pytest` collection. `.github/workflows/ci.yml` now skips the two
optional narration-engine requirements files explicitly. As a side
benefit, every matrix job stops pulling ~2 GB of torch + torchaudio
on every push.

### Fixed — `release` workflow (failed on v0.6.0)

When the maintainer publishes a tag manually (running
`scripts/release.sh` + `gh release create` locally before the
tag-push workflow caught up), the Actions workflow tried to create a
release that already existed and exited 1 with `a release with the
same tag name already exists`. The publish step is now idempotent:
it checks `gh release view` and skips with success when the release
already exists, instead of re-uploading and clobbering the
maintainer's locally-built `SHA256SUMS`.

### Documented

- `front-publish/references/audio-narration.md` now carries a
  short "Installation gotcha — OpenVoice package rename" note next
  to the engine matrix so users hit by the same upstream rename know
  the fix without having to read the CHANGELOG.
- `SECURITY.md` "Supply-chain notes" clarifies that
  `release.yml` is now idempotent (manual publish + workflow publish
  don't fight).
- `CONTRIBUTING.md` "Release process" gains a one-paragraph note
  about the local-vs-Actions interplay: pushing the tag triggers the
  workflow; if you want to publish manually first, the workflow now
  no-ops cleanly.

## [0.6.0] — 2026-06-22 — typography overhaul

**The three-Roboto rule.** Replaced the previous Montserrat-default /
Inter-alternate typography stack with a hard-coded three-family rule:
**Roboto** (sans / UI / body), **Roboto Serif** (editorial / longform
/ prose-heavy landings), **Roboto Mono** (`<code>`, `<pre>`, terminal
panels, log output). No other downloaded webfont is allowed.

**Reason.** A single super-family that shares metrics and x-height
across sans / serif / mono keeps prose-heavy and code-heavy surfaces
typographically coherent, makes the "which font do I lift here?"
decision automatic, and trims the WOFF2 payload to ~290 KB total
(latin subset, variable-axis, all three combined) versus ~830 KB for
the prior Montserrat-only bundle. The previous "user can swap to
Inter or any custom family" escape hatch is removed; if a project
genuinely needs a fourth family for brand or accessibility reasons,
that now requires an explicit project-README note rather than an
in-skill swap.

### Changed — bundled fonts

- **Removed** `front-ui/assets/fonts/montserrat/` (Montserrat
  variable + italic-variable + four static weights + OFL) and
  `front-ui/assets/fonts/inter/` (the empty alternate folder).
- **Added** `front-ui/assets/fonts/roboto/`,
  `front-ui/assets/fonts/roboto-serif/`,
  `front-ui/assets/fonts/roboto-mono/` — each shipping a
  variable-axis upright WOFF2 + italic-variable WOFF2 + upstream
  `OFL.txt` (all three families are SIL OFL 1.1).
- **Added** `front-ui/assets/fonts/README.md` codifying the
  three-Roboto rule and wiring instructions.
- **Mirrored** the three folders into
  `front-cli-gui/assets/examples/cli-gui-demo/public/fonts/` (the
  flagship demo). Demo `index.html`, `manifest.json`, `README.md`,
  and `favicon.svg` updated.

### Changed — skill prompts

- `front-ui/SKILL.md` — hard-rule 3 rewritten ("three-Roboto rule"
  replaces "Montserrat by default; Inter as the documented
  alternate"). Frontmatter `description`, chart-spec font name,
  pre-ship checklist, references list, and assets list updated.
- `front-ui/references/stack-tailwind.md` — typography section
  rewritten; Tailwind `fontFamily` block now includes `sans`,
  `serif`, `mono` per the three Roboto families; `app.css` `@import`
  block expanded to all three.
- `front-ui/references/ui-guidelines/foundations/typography.md` —
  rewritten end-to-end; preload, type scale, concrete rules, and
  checklist all updated. Added a `t-prose` editorial component class
  that lifts Roboto Serif.
- `front-ui/references/charts-vega.md` — every Vega-Lite font slot
  (`labelFont`, `titleFont`, header / legend) now uses Roboto.
- `front-ui/references/{checklist.md,material-design.md,ergonomics-criteria.md,stack-vanilla-js.md,ui-guidelines/INDEX.md}`
  — single-line mentions updated.
- `front-publish/SKILL.md` — typography line + emit-step rewritten.
- `front-cli-gui/SKILL.md` — typography rule + step-7 ship list
  rewritten to call out Roboto Mono for the streaming log panel.
- `front-cli/src/front_cli/cli.py` — `publish md-to-html` help text
  now says "three-Roboto + Tailwind shell".

### Changed — emitted code

- `front-publish/scripts/md_to_html.py` — Tailwind `fontFamily`
  block in the page template now ships Roboto / Roboto Serif /
  Roboto Mono with sensible system fallbacks (no JetBrains Mono).
- `front-publish/scripts/site_indexes.py` — `humans.txt`
  "Components" line updated.
- `front-publish/references/i18n.md` — non-latin font-loading
  example reframed around the three-Roboto bundle.
- `front-ui/assets/starter-page.html` — `<link rel="preload">` +
  `<link rel="stylesheet">` + Tailwind `fontFamily` config updated
  to wire all three Roboto families. Hero kicker text updated.
- `front-ui/assets/components/{chart-bar.json,chart-line.json}` —
  Vega `labelFont` / `titleFont` swapped to Roboto.

### Changed — docs + license

- `README.md`, `LISEZMOI.md`, `LANDSCAPE.md` (typography section +
  table reframed), `LICENSE.md` (OFL carve-out now covers the three
  Roboto families), `SECURITY.md`, `CONTRIBUTING.md` (OFL template
  reference) — all updated to the new rule.

### Notes for upgraders

- Any project that previously copied
  `front-ui/assets/fonts/montserrat/` or `…/inter/` into its own
  `public/fonts/` will need to copy the three new `roboto*/` folders
  instead and update its Tailwind `fontFamily` block + `<link>`
  preloads (see the migrated `front-ui/assets/starter-page.html` for
  the canonical pattern).
- Existing pages that hard-coded `font-family: Montserrat` in inline
  CSS (rare — the skill forbids this) will fall through to the
  system sans stack until the family name is updated to `Roboto`.

## [0.5.0] — 2026-06-21

Minor release. New optional editorial feature in `front-publish`:
**audio narration of long-form posts** via two MIT-licensed local TTS
engines (OpenVoice v2 + ChatterboxTTS — both shipping MIT licences
on code AND model weights, no licensing trap). Structural narration
hints derived from the Markdown tree; optional enrichment via the
same local Ollama daemon already used for alt-text and meta tags;
voice cloning from a 6-30 s designer-supplied sample. RSS feed
auto-becomes a podcast feed.

**Honest framing**: pre-recorded audio for long-form text is **not a
WCAG 2.x requirement** (screen readers already cover that case). The
feature targets multitasking audience, podcast positioning, and the
"alternative format" direction of WAI-COGA / WCAG 3.0 drafts. The
narration scripts live in `front-publish`, not `front-a11y`, to keep
this distinction visible.

### Added — narration pipeline

- **`front-publish/scripts/_narrate.py`** — shared helper. Parses a
  Markdown post into a list of `Segment` dicts (one per heading /
  paragraph / list item / blockquote), each carrying narration
  hints derived from Markdown structure: heading-level → pause
  length (H1: 1500 ms, H2: 1000 ms, H3+: 700 ms), list-item
  enumeration cue, blockquote wrapped with "Quote: ... End quote."
  + lower intensity, emoji-driven emotion baseline (30+ common
  emojis mapped), inline `[emotion: cheerful]` / `[emotion: default]`
  author overrides, frontmatter `narration.tone` + `narration.pace`
  baselines. Manifest cache keyed on
  `(source_sha256, engine, voice)` so re-runs short-circuit on
  unchanged posts. Pure-Python — no ML deps in the test path.
- **`front-publish/scripts/narrate_post.py`** — orchestrator. Reads
  the post, extracts segments, applies pronunciation overrides
  (`pronunciation.yaml` per-post or project-root), optionally
  enriches each segment via Ollama (`--ai-hints`, off by default,
  fail-soft when the daemon is down), dispatches to the chosen
  engine wrapper via subprocess, writes audio + manifest entry.
  Engine wrappers are subprocesses so the orchestrator's import
  graph stays light and the deterministic test path never sees
  torch.
- **`front-publish/scripts/narrate_openvoice.py`** — OpenVoice v2
  engine wrapper. Built-in voices (`base-en-default`,
  `base-en-friendly`, `base-en-cheerful`, `base-en-sad`,
  `base-en-whispering`, `base-es-default`, `base-fr-default`) plus
  zero-shot voice cloning from `--voice-sample <wav>`. Strength:
  cross-lingual — an English reference clone speaks French text
  with the cloned voice. Emotion mapped onto OpenVoice's native
  category set.
- **`front-publish/scripts/narrate_chatterbox.py`** — ChatterboxTTS
  engine wrapper. Continuous `exaggeration` (0.0–2.0) and
  `cfg_weight` (0.0–1.0) dials. Project hint mapping:
  emotion + intensity → exaggeration (neutral=0.5, cheerful=0.8,
  enthusiastic=1.0, angry=1.2, whispering=0.2, etc.; clamped to
  the engine's valid range). Strength: more expressive than
  OpenVoice; better for opinion / essay / mood-swing writing.
- **`front-publish/scripts/pick_voice.py`** — voice picker for the
  designer. Lists built-in voices per installed engine, optionally
  generates a one-sentence demo clip per voice
  (`--sample [--text "..."]`) into `out/voice-samples/<engine>/`.
  Designer listens, picks the one that fits, then uses
  `--voice <name>` on `narrate_post.py`.
- **`front-publish/scripts/install_narrate.py`** — install helper
  (mirrors `install_alt_ai.py` / `install_captions.py` from
  front-a11y). Downloads OpenVoice v2 checkpoints into
  `~/.cache/front-skill/openvoice/`; triggers ChatterboxTTS' lazy
  weight pull into `~/.cache/huggingface/` and creates the voices
  library directory. Does not auto-install the heavy Python
  packages — pip is the canonical channel via the per-engine
  requirements files.
- **`requirements-narrate-openvoice.txt`** + **`-chatterbox.txt`**
  — per-engine deps, install one or both. Engine wrappers
  fail-soft via `--check` mode so the orchestrator detects missing
  installs without crashing.

### Added — LLM enrichment hook

- Per-segment classification via Ollama (`--ai-hints`, default off).
  Default model `gemma4:e2b` — same as `alt_from_ollama.py`, so the
  user only needs one model pulled. The model receives the
  segment + adjacent segments + kind + baseline as context and
  returns strict JSON: emotion / intensity / pace /
  pause_before_ms / pause_after_ms / emphasis_word. Output is
  clamped to safe bounds and merged with structural baselines —
  structure is the source of truth, LLM overrides on specifics.
- `--ai-hints-only` flag prints the enriched segment list as JSON
  and exits without invoking the TTS engine. Lets the author
  review the LLM's calls before paying GPU/CPU time.
- Fail-soft: Ollama unreachable → narration continues on
  structural defaults. The deterministic test suite never depends
  on the daemon.

### Added — RSS / Atom audio enclosure

- **`front-publish/scripts/site_indexes.py`** gained an
  `--audio-manifest` flag. When passed, every post that has a
  matching narration manifest entry receives an `<enclosure>` row
  (RSS) or `<link rel="enclosure">` (Atom). The blog feed becomes
  a podcast feed any app can subscribe to with zero extra hosting.
- New `AudioEntry` dataclass + `load_audio_manifest()` helper
  normalise the narration manifest into a feed-ready
  `{post_stem: AudioEntry}` mapping. MIME type derived from the
  audio extension (`.wav` → `audio/wav`, `.mp3` → `audio/mpeg`,
  etc.); `length_bytes` populated from the on-disk file when
  `--audio-root` resolves to the public directory.

### Added — reference doc

- **`front-publish/references/audio-narration.md`** — full
  long-form reference: quick-start, voice-cloning ethics
  (GDPR Article 9 biometric data, BIPA, right-of-publicity in CA
  / NY / TN), engine matrix (with the explicit reason F5-TTS and
  XTTS-v2 are excluded — non-commercial weights), placement rule
  (audio player top-of-article with duration estimate, download
  link, `preload="none"`), RSS enclosure pattern, Schema.org
  `Article.audio` → `AudioObject`, OpenGraph `og:audio` snippet,
  inline `[emotion: X]` author convention, "when to outgrow this
  pipeline" honesty (memoir / streaming TTS / multi-voice dialogue
  → out of scope).

### Added — tests

- **`tests/test_narrate.py`** — 39 deterministic tests.
  Coverage: segment extraction (10 cases — heading levels,
  lists, blockquotes, inline markup, images, HTML tags,
  frontmatter tone, emoji emotion, inline `[emotion: X]` markers,
  heading reset of sticky emotion), pronunciation overrides
  (4 cases — whole-word, longest-token-wins, empty-overrides
  noop, per-post then project-root lookup), `source_sha256`
  + manifest round-trip + corrupt-input soft-failure (4 cases),
  `merge_llm_hint` clamping + key preservation (5 cases),
  ChatterboxTTS emotion → exaggeration mapping (4 cases),
  `site_indexes.load_audio_manifest` + `render_rss` /
  `render_atom` enclosure injection (6 cases), and an end-to-end
  cache short-circuit assertion that exercises the orchestrator
  without installing an engine. Pure stdlib + PyYAML — no torch,
  no Ollama, no network. **Total deterministic suite: 423 tests
  (up from 384).**

### Changed — `front-publish/SKILL.md`

- New row in the "What it does" trigger table for narration
  (clearly marked **optional editorial enhancement**).
- New "Optional editorial step" workflow block in "Tool
  composition" showing `narrate_post.py` → `site_indexes.py
  --audio-manifest` chain.
- Reference list gains `references/audio-narration.md`.
- Scripts table gains `narrate_post.py`, `narrate_openvoice.py`,
  `narrate_chatterbox.py`, `pick_voice.py`, `install_narrate.py`.

### Changed — version bumps

- All four `SKILL.md` files bumped `0.4.1 → 0.5.0` (minor — new
  user-facing feature in `front-publish`).

### Honest gaps deliberately not addressed

- **Engine wrappers not exercised in CI.** Each requires
  ~1 GB of model weights and minutes of CPU/GPU per post.
  The wrappers ship a `--check` mode so the orchestrator can
  detect missing installs; the orchestration logic itself is
  covered by mock-subprocess tests.
- **No automatic audio embedding in HTML output.** The
  reference doc documents the `<audio>` + Schema.org +
  OpenGraph pattern; the `meta_from_ollama.py` script does not
  yet auto-inject these tags from a manifest. Deferred —
  current rendering is editorial.
- **No automatic MP3 transcoding.** Engine wrappers produce
  WAV (lossless). For distribution-size MP3, run `ffmpeg
  -i in.wav -b:a 96k out.mp3` separately. Documented in
  the reference, not yet automated.

## [0.4.1] — 2026-06-21

Hardening release. Closes a critical correctness gap audit found in
the validation layer, plus a doc lie. **All four `SKILL.md`
frontmatters were silently YAML-invalid for every release through
0.4.0** — `yaml.safe_load` rejected them with
`mapping values are not allowed here` because of unquoted `:`
characters in `description` (`Trigger phrases: "..."`). The regex
frontmatter check in `front-ui/scripts/validate.py` saw the
`---...---` delimiters and reported PASS, so CI never noticed.
Claude / OpenCode runtimes call a real YAML parser; depending on the
client this either reduced the skill to a bare slug or rejected it
outright. No behaviour change in any shipped script.

### Fixed — SKILL.md YAML frontmatters

- Rewrote `description:` in every `SKILL.md` as a folded block scalar
  (`>-`) so the `:` characters inside the value are no longer parsed
  as map separators. Verified with `yaml.safe_load` on each. Lengths:
  709 (front-ui), 754 (front-cli-gui), 889 (front-publish), 870
  (front-a11y) — all within the Anthropic 50–1024 char cap. Body
  unchanged.
- Fixed `SECURITY.md` claim "no signed release, no checksum file" —
  releases have shipped `SHA256SUMS` since v0.3.0. New text states
  the integrity-vs-authenticity distinction honestly: checksums yes,
  GPG signature no.

### Added — real validator + negative tests

- **`scripts/validate_skill.py`** — stdlib + PyYAML, parses each
  `SKILL.md` frontmatter with `yaml.safe_load` and checks: name
  present + matches folder, description present + 50–1024 chars, body
  non-empty, no `TODO`/`TBD`/`FIXME`/`XXX` placeholders. Importable
  as `validate_skill(Path) -> list[str]` or callable as a CLI.
- **`scripts/validate_all.py`** — repo-wide orchestrator. Runs the
  strict YAML validator across all four skills, then runs the
  existing `front-ui/scripts/validate.py` content gate (framework
  imports, trademarks, marketing voice, INDEX.md path resolution).
  One exit code; one CI step.
- **`tests/test_validate_skill.py`** — 17 tests:
  - Each shipped skill passes (parametrised, 4 tests).
  - Negative cases under `tmp_path`: missing SKILL.md, invalid YAML
    (the exact bug above), missing/empty name, missing/empty
    description, name ≠ folder, no frontmatter at all, empty body,
    description too short, description too long, placeholder in
    SKILL.md. 10 tests.
  - CLI contract: exit zero on all-pass, non-zero on broken YAML,
    `validate_all.py` exits zero on the shipped repo. 3 tests.
- **`PyYAML>=6.0`** added to `requirements-dev.txt`.

### Added — release packaging smoke test

- **`tests/test_release_packaging.py`** — 19 tests, run end-to-end:
  builds the tarballs via `scripts/release.sh 0.0.0-test` into a
  module-scoped `tmp_path`, then verifies:
  - five tarballs + `SHA256SUMS` (no extras, no missing),
  - every declared SHA-256 matches the artifact on disk,
  - each per-skill tarball extracts to the expected folder,
  - the extracted `SKILL.md` re-passes the strict validator,
  - no banned paths (`__pycache__`, `.DS_Store`, `.git/`,
    `__MACOSX`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`) ride
    along,
  - every `scripts/...` / `references/...` / `assets/...` backticked
    path in `SKILL.md` exists in the archive (caught the
    `assets/fonts/inter/` reference that wasn't a real directory),
  - bundle tarball contains every skill,
  - per-skill tarball ≤ 10 MB (catches accidental model / fixture
    inclusion).

### Added — front-ui `assets/fonts/inter/`

- New folder with a `README.md` documenting the Inter swap recipe
  (same instructions as `references/stack-tailwind.md`, now landed at
  the path the SKILL.md actually points at). Inter WOFF2 files
  remain user-supplied — the folder is the landing pad. Resolves the
  dangling reference caught by the new packaging smoke test.

### Changed — CI gates the YAML validator

- `.github/workflows/ci.yml` now runs `python scripts/validate_all.py`
  in addition to the existing front-ui content gate, on the existing
  Python 3.10 / 3.11 / 3.12 matrix. A PR that breaks any SKILL.md's
  YAML fails CI even if the deterministic test suite somehow doesn't.

### Changed — docs aligned with reality

- **README + LISEZMOI** "Install" section: added an explicit
  `python3 scripts/validate_all.py` verification step after the
  on-disk install, and a new "Install from source" subsection
  walking the clone / pip / pytest / validate / cp flow for
  contributors. New "Trust model" / "Modèle de confiance" subsection
  states the SHA-256-yes / GPG-no posture and points at
  `SECURITY.md`.
- **`SECURITY.md`** Supply-chain notes rewritten: two install paths
  documented honestly (release + git-clone), what we sign vs don't,
  upstream registries named, validators and pytest as the local
  trust-but-verify path.

### Notes

- No version bump for the shipped scripts themselves — behaviour is
  unchanged.
- SKILL.md `metadata.version` bumped `0.4.0 → 0.4.1` in all four
  files to align the on-disk skill version with this release tag.

## [0.4.0] — 2026-06-21

Minor release. Adds the three-state colour-scheme toggle component
(`🌞 Light` / `🌚 Dark` / `🌗 Auto`, Auto-by-default) to the
front-ui assets, ships a reusable headless-screenshot helper, and
opens `GALLERY.md` with the first real-site entry.

### Added — theme toggle component

- **`front-ui/assets/components/theme-toggle.html`** — copy-pasteable
  HTML+JS, three variants in one file:
  - **A. Segmented radio control** (3 buttons, emoji + label,
    `role="radiogroup"` / `role="radio"` / `aria-checked`, arrow-key
    roving focus). Used on ≥ `sm` screens.
  - **B. Icon-only cycle button** (`Auto → Light → Dark → Auto`,
    glyph reflects current mode, next mode announced via
    `aria-label`). Used on narrow viewports.
  - **C. Fixed bottom-right anchor** wrapper for pages with no
    sticky chrome (single-card landings, embedded widgets,
    `cli-gui-demo` log viewer). Uses `safe-area-inset` padding so it
    clears the mobile home indicator.
- **Wiring** depends on the existing `applyTheme(mode)` helper from
  `references/stack-vanilla-js.md` — persists via
  `localStorage["color-scheme"]` and stays in sync with system
  `prefers-color-scheme` changes when the mode is `auto`. Auto is
  the explicit default everywhere — a fresh visitor inherits their
  OS choice and is never surprised by a hard-coded scheme.
- **Canonical placement rule** added to
  `front-ui/references/stack-vanilla-js.md` § "Toggle UI control":
  top-right of sticky header (priority 1) → footer far-right
  (priority 2) → fixed bottom-right anchor (priority 3).
- **`assets/components/nav.html`** updated so the sticky-header
  variant of the toggle ships in the canonical nav block out of
  the box; the icon-only fallback appears below `sm`.

### Added — `GALLERY.md` and screenshot tooling

- **`GALLERY.md`** — Markdown-only showcase of real sites and tools
  shipped on the stack. Two entries at launch:
  - **4ml — A Practical Python Environment for AI**
    (<https://harchaoui.org/warith/4ml>) — long-form single-page
    guide with sticky table of contents, captured headlessly via
    Playwright in both `prefers-color-scheme` variants.
  - **md2star — Markdown → branded `.docx`/`.pptx`/`.pdf`**
    (<https://github.com/warith-harchaoui/md2star>) — the concrete
    CLI → GUI target `front-cli-gui` was designed for; light/dark
    hero screenshots sourced from md2star's own README (`assets/
    screenshots/hero-{light,dark}.png`) so the gallery shows what
    md2star itself shows, not a re-render.
  No CMS, no separate showcase site, no build step — every entry
  is a section in this file with screenshots committed under
  `assets/gallery/<slug>/{light,dark}.png`.
- **`scripts/gallery_screenshot.py`** — headless Chromium via
  Playwright, captures both `prefers-color-scheme` variants in one
  pass (retina 2× device-scale, default 1440×900 viewport,
  `--full-page` for the full vertical extent). Calls `pngquant`
  in-place when it's on `PATH` to trim retina captures from ~8 MB
  to ~2.7 MB at quality 70-90. Fails-soft when `pngquant` is
  missing — the PNG just stays uncompressed.
- **README + LISEZMOI** point to `GALLERY.md` from the "not for
  X" / "alternatives" paragraph, alongside the existing
  `LANDSCAPE.md` link, so discovery flows naturally.

### Changed — version bumps

- All four `SKILL.md` files bumped `0.3.2 → 0.4.0` (minor — new
  user-facing component + new top-level doc).
- README + LISEZMOI install snippets bumped to `VERSION=0.4.0`.
  Status snapshot reference bumped to `v0.4.0`.

## [0.3.2] — 2026-06-21

Cosmetic / hygiene patch release. Closes three of the five roadmap
items from 0.3.1: LISEZMOI parity, `references/` reshape
re-assessment, and `front-cli-gui` production-hardening notes. No
behaviour change for any script.

### Added — `front-cli-gui/references/hardening.md`

- New reference, ~250 lines, eight sections: loopback binding,
  bearer-token auth on `/run`, command + flag allow-list with
  path-traversal guard, subprocess sandbox (`shell=False`, `cwd`,
  scrubbed `env`, `start_new_session=True`, wall-clock timeout via
  `os.killpg`), per-token rate limit (in-memory sliding window), CORS
  posture (single pinned origin, no `*` with credentials), logging
  hygiene (cmd / exit / duration only — no argv, no token, no body),
  TLS terminated at a reverse proxy. Ends with a 10-line
  "before-promotion" checklist and a "when to outgrow the stdlib host"
  trigger list (multi-worker, schema validation, SSE reconnects,
  Tauri sidecar).
- Snippets follow the project's Python style — module imports,
  numpy-style docstrings on the non-trivial helpers (`validate`,
  `run_sandboxed`, `rate_limited`), full typing, dict over class.
- Wired into `front-cli-gui/SKILL.md` § References (the stale link to
  the never-shipped `cli-gui-workflow.md` was removed in the same
  pass).

### Changed — `LISEZMOI.md` brought back to parity

- New section "**État d'avancement**" mirrors the EN README "Status"
  table (eight rows, audio flagged WiP, version reference at 0.3.2).
- Audio row of "Entrées → sorties" flagged **WiP** with a back-link to
  the new section, matching the EN row.
- Install snippet bumped from `VERSION=0.3.0` to `VERSION=0.3.2`.

### Changed — `references/` reshape re-assessed

- The 0.3.1 roadmap item *"split teaching prose from rules
  (`<name>-rules.md` + `<name>-guide.md`)"* is **retired** rather than
  shipped. Audit showed the prose-trim pass on 2026-06-19 already
  addressed `o.md` § 7: `ux-psychology.md` (175 → 87 LOC),
  `material-design.md` (155 → 128 LOC), `color-psychology.md`
  (90 → 84 LOC). Remaining reference files are rule-shaped enough
  that a structural split would add friction without value.
  Documenting the decision here so the next reader doesn't re-litigate
  it.

### Changed — version bumps

- All four `SKILL.md` files bumped `0.3.1 → 0.3.2`. README + LISEZMOI
  install snippets bumped to `VERSION=0.3.2`. Status snapshot
  reference bumped to `v0.3.2`.

### Fixed

- **`front-cli-gui/SKILL.md` referenced a non-existent file**
  (`references/cli-gui-workflow.md`). Replaced with the real
  `references/hardening.md` link.

## Roadmap

Open threads carried into 0.4.0. Both remaining items are paused on
explicit user signal — do not restart without one.

1. **Captions WER baselines + `vocab-biasing-clip.wav`.** User has
   deferred audio fixture work pending dataset acquisition (Common
   Voice 26.0 tarballs are 25–88 GB per language). When they signal:
   run `tests/fixtures/audio/extract_cv_subset.py` per language,
   commit MANIFEST + STATS + transcripts, publish median WER in
   `front-a11y/references/captions-ai.md`.
2. **Real end-to-end application example.** User has deferred. Scope
   pre-decided: wrap `md2star` (user's own CLI) with a Tauri shell
   that invokes it as a sidecar — not another mock SSE proxy. The
   `cli-gui-demo` stays as the scaffold reference; the Tauri example
   becomes the production reference.

Adoption-side milestones (user-driven; not engineering work):

- Real Claude Code session against the four skills to verify trigger
  phrasing fires on "wrap my CLI", "captions for this video", "audit
  my palette". Refine descriptions if under-triggers.
- 5 real users — the only signal that says whether anything else on
  this list is worth doing.

## [0.3.1] — 2026-06-20

Patch release. Documents the current status of each surface, marks
audio captions explicitly **WiP** so users don't expect a finished WER
gate, and ships one defensive fix for Ollama 0.30 MLX vision
quantizations. No behaviour change for the stable scripts.

### Added — status and roadmap

- **`README.md` → "Status" section** spells out where each of the five
  surfaces (`front-ui`, `front-cli`, `front-cli-gui`, `front-publish`,
  `front-a11y`) stands today and isolates the one WiP area (captions /
  audio). Replaces the implicit "everything is stable" reading of the
  previous README.
- **`README.md` → "Inputs → outputs" table** now flags the audio /
  video row as **WiP** and links back to "Status". Users won't be
  surprised by the missing per-language WER baselines or the
  user-supplied `vocab-biasing-clip.wav`.
- **`CHANGELOG.md` → "Roadmap"** section (below) records the four
  outstanding threads we're carrying into 0.4.0: captions baselines,
  LISEZMOI parity, full `references/` reshape, and `front-cli-gui`
  production-hardening notes.

### Changed — `front-a11y/SKILL.md`

- Captions row of the "Honest framing" table and the decision-tree
  entry both flagged *(WiP)* with a one-line pointer to
  `tests/fixtures/audio/README.md` for the current shape of the eval
  fixtures. The script itself is unchanged.

### Changed — version bumps

- All four `SKILL.md` files bumped from `0.2.0` → `0.3.1`. They were
  left at `0.2.0` through 0.3.0 by accident — this aligns the on-disk
  frontmatter with the release tag so skill consumers can tell
  versions apart.

### Fixed

- **`alt_from_ollama.py` MLX vision auto-detection** (commit
  `af010c7`). Ollama 0.30 ships MLX quantizations of Gemma vision
  models (`gemma4:e2b-mlx`) that silently discard the image input on
  some manifest variants. New `_model_has_vision(model)` queries
  `/api/show` and falls back to the non-MLX tag when the manifest
  reports no `vision` capability. Defensive: returns `True` on any
  request error so a flaky daemon doesn't silently downgrade.

## [0.3.0] — 2026-06-20

### Added — unified driver and ergonomics

- **`front-cli/` package** ships a Click-based top-level driver. A single
  `front` executable maps `front <skill> <action> [...]` onto each
  per-skill script via `subprocess`. Shell completion is documented for
  bash/zsh/fish in `front-cli/README.md`. Stdlib-only validators stay
  zero-dep when invoked directly; the driver is additive.
- **Four Ollama-backed scripts migrated from argparse to Click**:
  `alt_from_ollama.py`, `captions_from_whisper.py`, `meta_from_ollama.py`,
  `plain_language.py`. Behaviour preserved (all 323 deterministic tests
  unchanged); `--help` now formatted by Click. `install_alt_ai.py`
  gained `-h/--help` and `--model` flags.
- **Stdlib-only validators** (`lint_a11y.py`, `audit_contrast.py`,
  `simulate_cvd.py`, `site_indexes.py`, `favicons.py`, `validate.py`,
  `lint_markdown.py`, `md_to_html.py`, `install_captions.py`) gained a
  shared `_argparse.make_parser` factory that standardises `prog`,
  `formatter_class`, `epilog`, and the `-V/--version` flag — addressing
  the 13 argparse inconsistencies catalogued in `.private/click.md`.

### Added — runtime language configuration

- **`FRONT_LANG_PAIR` env var** drives the default `--lang` for the four
  Ollama-backed scripts. Precedence: explicit `--lang` flag →
  `FRONT_LANG_PAIR` first comma-split entry → existing detection
  fallback. Lets a user set their pair once (`export FRONT_LANG_PAIR="en,de"`)
  instead of repeating `--lang` on every invocation.
- **`lang_pair` frontmatter token** added to all four `SKILL.md` files
  with a "Changing the language pair" recipe section. EN/FR remains the
  example default; switching to EN/DE / EN/ES / EN/JA / … is now a
  documented per-project edit.
- **Test coverage**: `tests/test_lang.py` gained 6 new cases for
  `lang_pair_default()` (env-unset, whitespace tolerance, empty-string
  handling, precedence).

### Added — eval test suite

- **`tests/eval/`** — opt-in (`pytest -m eval`) quality bench for the
  AI-backed scripts. Four modules: `test_alt_eval.py`,
  `test_plain_language_eval.py`, `test_meta_tags_eval.py`,
  `test_captions_eval.py`. Skip cleanly when Ollama is unreachable, the
  pulled model is missing, or fixtures haven't been populated.
- **Wikipedia image fixtures** for alt-text eval. `tests/fixtures/images/
  fetch_wikipedia.py` downloads 4 hash-pinned upload.wikimedia.org
  images (informative-EN, complex-EN, functional-EN, informative-FR)
  with their human-written alt + caption as ground truth. The
  decorative case keeps a synthetic Pillow image (W3C-decorative has
  no caption to verify). DeepEval `AnswerRelevancyMetric` is the
  primary scorer; a stdlib char-trigram Jaccard fallback (≥ 0.10
  threshold) runs when DeepEval misconfigures.
- **Common Voice extractor** for captions WER bench.
  `tests/fixtures/audio/extract_cv_subset.py` (stdlib + ffmpeg) reads a
  Common Voice 26.0 tarball, stratified-samples N clips per language
  balanced on gender / age / accent (capped at 3 clips per opaque
  speaker hash), transcodes to 16 kHz mono PCM WAV, writes
  per-language `MANIFEST.json` + `STATS.json`. Idempotent via `--seed`.
  Test wires `LANGUAGES = ("en", "fr", "es")` with a parametrised
  per-language median-WER assertion (`≤ 0.10`). Adding a language is
  one line.
- `tests/test_extract_cv_subset.py` — 18 deterministic tests for the
  extractor's pure logic (filter cutoffs, stratified sampling,
  per-speaker cap, determinism with same seed, diversity stats).
- `tests/fixtures/audio/fetch.py` ships as a single-clip LibriVox /
  archive.org fallback for projects without Common Voice headroom.

### Added — release infrastructure

- **`scripts/release.sh`** — bash, no new deps. Takes a version
  argument, builds five tarballs (one per skill + a bundle), generates
  `SHA256SUMS`, and self-verifies. Prefers `shasum -a 256` (macOS) with
  `sha256sum` fallback (Linux). Prints a copy-pasteable `gh release
  create` next-steps message.
- **`.github/workflows/ci.yml`** — pytest + validator + eval-collect
  across Python 3.10 / 3.11 / 3.12 on every push and PR.
- **`.github/workflows/release.yml`** — tag-driven (`v*.*.*`) release
  via `scripts/release.sh` + `gh release create --generate-notes`.

### Added — Wikipedia / Common Voice licensing

- **`LICENSE.md` § "Bundled third-party assets"** gained a "Common
  Voice audio clips" entry documenting the CC0 dedication, voluntary
  attribution, and the platform's no-speaker-identification rule.
  Manifests record opaque CV `client_id` hashes only, never raw
  identifiers.

### Changed — honesty pass on positioning

- README + LISEZMOI gained a structured "**Who this is for**" block
  with four explicit audiences (solo devs, pentesters writing internal
  dashboards, data scientists wrapping CLIs, bilingual docs sites)
  replacing the prior "anyone building a frontend" framing.
- `LANDSCAPE.md` gained a "**Where `front` is genuinely the best
  pick**" section naming three concrete categories (CLI→GUI mock-ups
  in skill form, pre-ship a11y gates without a browser, bilingual
  docs sites with EN/FR/DE/ES/JA pairing) and a "**Where to pick
  something else**" hand-off to shadcn/ui and HTMX + classless CSS.
- `lint-a11y.md` and `contrast-audit.md` reframed: pre-commit gate
  positioning explicit, "**not a replacement for axe-core / Pa11y /
  Lighthouse**" stated up front.

### Fixed

- **`front-cli` driver was intercepting `--help` at the leaf-command
  level** instead of forwarding it to the wrapped script. Users typing
  `front a11y alt --help` saw Click's one-line stub instead of the real
  script options. Fix: `add_help_option=False` on every leaf command;
  groups keep their own help handling via `GROUP_CONTEXT_SETTINGS`.
- **`__MACOSX/` macOS-zip-artefact** added to `.gitignore`; the
  previously-tracked directory removed.
- **`tests/test_lint_markdown.py`** lost its dependence on lucky
  `sys.path` ordering after the new Click migration changed import
  order. Now uses explicit `prompts_dir=` kwarg.

### Deferred to a future release

- **Full reshaping of `references/`**. Teaching prose still mixed with
  rule-shaped content in some reference files. Future pass will split
  into `*-rules.md` + `*-guide.md` where the boundary is clear.
- **`vocab-biasing-clip.wav`** is user-supplied. The glossary contains
  project-brand terms (`pywhispercpp`, `VisionCell`, …) that no Common
  Voice contributor has uttered, so this clip stays a record-it-yourself
  asset.
- **5 real users** and a **live trigger-phrasing session against the
  updated frontmatters** are the two adoption-side milestones that
  determine whether 0.3.0 needs a fast follow-up.

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
  every SKILL.md is updated.
- **User-supplied custom typefaces are supported.** If a project ships
  a folder under `front-ui/assets/fonts/<family>/` with the TTF or
  WOFF2 files and a license file, the skill swaps `fontFamily.sans` to
  that family without touching the rest of the stack. Recipe is in
  `front-ui/references/stack-tailwind.md` → "Typography — default,
  alternate, and custom swap". The previous "two choices, no more"
  framing was too rigid for projects with brand-mismatch or
  language-coverage constraints.

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
