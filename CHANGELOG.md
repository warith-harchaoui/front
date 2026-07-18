# Changelog

All notable changes to `front` will be recorded here. Dates are ISO-8601.

The project follows a loose [SemVer](https://semver.org/) — major version
bumps mean the on-disk skill layout changes (users have to re-copy folders
into `~/.claude/skills/`).

## Releases

Each tagged release publishes one tarball per skill plus a bundle on
GitHub Releases, and a single `SHA256SUMS` covering every artifact.
Users download the bundle (or a per-skill tarball), run
`shasum -a 256 -c SHA256SUMS` to verify it, extract, and copy the
folders they need into `~/.claude/skills/`. The README's *Install*
section walks the full flow. To upgrade, repeat the steps with a newer
`VERSION` — the on-disk folder name is stable so the copy overwrites in
place. If the checksum check fails, do not install the artifact.
Release tarballs are produced by `scripts/release.sh <version>`.

## Roadmap

Open threads carried through the 0.6.x string. Both remaining
engineering items are paused on explicit user signal — do not restart
without one. None of the recent 0.6.0–0.6.3 releases (typography
overhaul, CI/release workflow fixes, Google SEO + GEO foundations,
Anthropic skill-spec audit) changed their status; they all sit
elsewhere in the codebase.

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

3. **Unified i18n make + audit.** GUI strings and LLM prompts share one
   concern — language — so one per-project catalog, **`locales/i18n.yaml`**
   (message id → per-locale text), serves both. **make**: `cli_to_gui` /
   front-ui scaffolds emit and read `locales/i18n.yaml` instead of hardcoding
   strings. **audit**: a static check flags any GUI string or prompt living
   outside `locales/i18n.yaml` — a translation dict in `.js`/`.html` or a
   prompt inlined in `.py` — with a "move to `locales/i18n.yaml`" finding (same
   JSON + exit-code shape as the other auditors). Prompts already comply; the
   GUI side is the build.

Adoption-side milestones (user-driven; not engineering work):

- Real Claude Code session against the four skills to verify trigger
  phrasing fires on "wrap my CLI", "captions for this video", "audit
  my palette". Refine descriptions if under-triggers.
- 5 real users — the only signal that says whether anything else on
  this list is worth doing.

## [0.21.0] — 2026-07-18 — one authorized LLM: `gemma3:4b` (no MLX), enforced

Fixes the biggest fresh-user onboarding blocker and locks the model policy down.

- **`gemma3:4b` is now the single authorized LLM**, served through Ollama, across
  every Ollama-backed script (alt text, meta tags, plain-language, narration,
  speaker-naming). It is multimodal (vision + text) and in the public registry,
  so `ollama pull gemma3:4b` works on any box.
- **Removed the `-mlx` auto-suffix** — the previous default appended `-mlx` on
  Apple silicon, naming a maintainer-local build (`gemma4:e4b-mlx`) that 404'd on
  a fresh machine. Dropped `OLLAMA_MODEL_BASE` and every alternative-model example
  (gemma4, gemma3:12b, gemma3n, llava, qwen, …) from front's own scripts and docs.
  `OLLAMA_MODEL` remains only as a bare test escape hatch.
- **Enforced by a guard test** (`tests/test_single_llm.py`): every
  `front-*/scripts/*.py` is checked for any non-`gemma3:4b` model tag or `-mlx`
  tag and fails if one appears — machine-checkable, forever.
- Docs swept to gemma3:4b throughout (README + LISEZMOI OpenCode config, SKILL.md,
  references, CONTRIBUTING, llms.txt, front-cli help). External-project mentions in
  `GALLERY.md` and historical `CHANGELOG` entries left as-is (factual / history).
- Trigger phrases in front-audio / front-cli-gui / front-publish were front-loaded
  (earlier in the description) so keywords survive any listing-budget truncation.

## [0.20.0] — 2026-07-18 — unified i18n make + audit (`locales/i18n.yaml`)

New **front-ui** capability, built to the make/audit paradigm: translatable
strings — GUI labels **and** LLM prompts — live in one per-project catalog,
`locales/i18n.yaml`, never in JS or inlined in Python.

- **make** — `front-ui/scripts/i18n_make.py` scaffolds `locales/i18n.yaml`
  (`gui:` + `prompts:` namespaces), compiles it to `locales/i18n.json` (the
  browser can't read YAML), and emits `locales/i18n.js`, a framework-free
  loader with `initI18n()` + `t(id)`.
- **audit** — `front-ui/scripts/audit_i18n.py` flags **I18N001** (a translation
  dict embedded in JS/HTML) and **I18N002** (an LLM prompt inlined in Python),
  JSON + exit codes, wired as the `front-ui-i18n-audit` pre-commit hook.
- **Dogfood** — the repo now passes its own i18n audit: the narration-emotion
  Ollama system prompt moved from an inline `_narrate.py` constant to
  `front-publish/scripts/prompts/narration_emotion.yaml`, loaded via `_prompts`.
- Description triggers gain `i18n to YAML` / `audit i18n`; 14 new tests;
  `TRIGGERS.md` regenerated.

## [0.19.0] — 2026-07-18 — exhaustive trigger phrases + version sync

Improves **skill activation** (Claude Code + OpenCode) and fixes a version drift.
No behavioural change to any script.

- **Trigger-phrase exhaustiveness.** Every skill's `description` gained
  user-language trigger phrases covering capabilities that previously had no
  activation keyword — so a skill is less likely to "go under the rug". E.g.
  front-ui (+`dark mode toggle`, `dashboard`, `data table`, `empty state`),
  front-accessibility (+`missing alt`, `WCAG compliance`, `fix accessibility`),
  front-figures (+`bar / line / scatter chart`, `Vega-Lite`, `visualize data`),
  front-cli-gui (+`Typer / clap / cobra to GUI`, `GUI for my Go or Rust CLI`),
  and similar for colors / ux-laws / publish / vision / audio. All descriptions
  stay within the repo's 1024-char cap; `TRIGGERS.md` regenerated.
- **Version sync.** `metadata.version` in every `SKILL.md` was stale at 0.15.1;
  it now tracks the release (0.19.0) alongside `SKILL_VERSION` and `front-cli`.
- **Deterministic type gate.** Pinned `types-PyYAML` + `types-requests` so the
  `mypy` CI job resolves `yaml`/`requests` identically everywhere (fixes a
  works-locally-fails-in-CI stub mismatch).
- **i18n rule sharpened** — the canonical catalog is named: **`locales/i18n.yaml`**,
  one file for GUI strings AND prompts, on both the make and audit sides.

## [0.18.0] — 2026-07-18 — `ruff` + `mypy` gates, `EXAMPLES.md`, gallery adoption

Documentation + tooling. No on-disk skill layout change — the per-skill tarballs
are unchanged; this release adds repo-root docs, CI gates, and dev config.

- **`EXAMPLES.md`** at the repository root — a runnable cookbook, one recipe
  per skill (deterministic 🟢 vs local-AI 🤖) anchored on `tests/fixtures/`,
  each showing expected output. Linked from `README.md` and `LISEZMOI.md`.
- **`ruff` lint gate** (CODING_ALL.md rule 3, lint half) — a pinned `ruff.toml`
  plus a blocking `ruff check` CI job (`lint`), following the suite's own
  make/audit pattern (audit = `ruff check`; make = `ruff check --fix`). Implicit
  re-exports now use the PEP 484 `name as name` form; ~18 genuinely-unused
  imports removed; 5 undefined-name (F821) typing defects fixed.
- **`mypy` type gate** (CODING_ALL.md rule 3, type half) — `mypy.ini` +
  `scripts/run_mypy.sh` (per-skill-dir, `ignore_missing_imports`), wired into the
  CI `lint` job. Fixed 27 real type defects surfaced by the first run (bad
  `callable` annotations, lazy `numpy`/`pandas` forward refs, `Optional`
  assignments, `Image.Resampling.LANCZOS`, tuple-width casts, a redefinition).
- **`GALLERY.md`** — four real adoption entries (md2star, roitelet, intentions,
  sql), each with a project logo. All are projects the maintainer ships with the
  `front-*` skills. The "Adding to the gallery" submission boilerplate was
  dropped (this is a curated showcase, not an open-submission list).
- **i18n house rule documented** — translatable strings (GUI labels **and** LLM
  prompts) live in a separate YAML catalog, never embedded in JS or inlined in
  Python; GUI and prompts share one language source of truth. Prompts already
  comply (`prompts/*.yaml`). See `README.md` → "What the skills enforce". The
  make/audit *implementation* for GUI i18n is roadmapped below.

## [0.17.0] — 2026-07-07 — `front-audio` captions on `vocal-helper` + pinned helper releases

Minor release. The `front-audio` captions tier now delegates speech-to-text
to the author's `vocal-helper` over-layer instead of driving `pywhispercpp`
directly, and the audio / video extraction path is repaired against the
helpers' latest tagged releases. No on-disk folder layout change — upgrading
is the usual overwrite of `front-audio/`.

### What changed

- **Captions route through `vocal-helper`.** `captions_from_whisper.py`
  now runs STT via `vocal_helper.asr.WhisperStage` (the author's whisper.cpp
  over-layer — owns the model defaults, word-timestamp wiring, the
  `min_segment_ms` hallucination guard and the `initial_prompt`
  vocabulary-biasing lever) instead of instantiating `pywhispercpp.Model`
  directly. The file is driven as a single whole-file segment — no VAD, no
  diarization (that stays in the separate `diarize` tier). The WebVTT / SRT /
  text renderers are unchanged (a seconds→centisecond adapter feeds them),
  and the on-disk cache + `WHISPER_DIR` model cache are preserved.
- **Repaired the audio/video-helper integration.** The helpers' new
  releases renamed `audio_helper.to_wav → sound_converter` and
  `video_helper.extract_audio → extract_audio_track`; the old optional
  imports silently `ImportError`ed and fell back to `ffmpeg` every time.
  `captions_from_whisper.py` and `diarize_from_nemo.py` now call the current
  functions, and decode via `audio_helper.load_audio`.
- **Hard-pinned helper dependencies.** `requirements-captions.txt` pins
  `vocal-helper@v0.3.1`, `audio-helper@v1.5.2`, `video-helper@v1.6.1`;
  `requirements-diarize.txt` pins the two extraction helpers. URLs use the
  `.git@vX` form so they dedupe against `vocal-helper`'s own internal pin of
  `audio-helper` (otherwise pip treats the two direct references as
  conflicting and the resolve fails).
- **Installer.** `install_captions.py` now installs `vocal-helper` (which
  pulls `pywhispercpp`) rather than bare `pywhispercpp`;
  `ensure_pywhispercpp` → `ensure_captions_engine`. The GGML pre-download
  still goes through `pywhispercpp.utils.download_model`.
- **CI.** `requirements-captions.txt` is skipped in the per-skill install
  loop — `vocal-helper` drags in `silero-vad → torch` (~2 GB), the same
  weight class as the diarization / narration backends. `captions_from_whisper`
  defers every heavy import behind the `_pcm_from_wav` / `_run_whisper_stage`
  seams, so it imports cleanly for collection and `test_captions` mocks those
  seams.
- **Docs + tests.** `SKILL.md`, `references/captions-ai.md`,
  `references/diarization.md`, `tests/test_captions.py` and
  `tests/test_install_captions.py` updated for the new engine. Validated
  end-to-end with real whisper.cpp (Metal) on both audio and video inputs.
- **Footprint note.** The captions tier is heavier than before — `torch`
  now arrives transitively via `vocal-helper → silero-vad`, where the old
  tier was `click + pywhispercpp + langdetect`.

### Version

- Shared `SKILL_VERSION` bumped to `0.17.0` across all fourteen
  `_argparse.py` / `_click.py` copies, and `front-cli` to `0.17.0`.

## [0.16.0] — 2026-07-06 — `front-figures` skill + audio diarization tier

Minor, additive release. Two new capabilities ship as their own tiers;
no existing on-disk folder changes, so upgrading is a copy of the new
`front-figures/` folder plus the usual overwrite of `front-audio/`.

### What changed

- **New skill `front-figures`.** Static data-viz auditor
  (`audit_figure.py`, stdlib + PyYAML) for Vega-Lite v5 JSON,
  matplotlib SVG and HTML `<figure>` blocks — flags missing axis
  titles, dual-y-axis, truncated baselines, pie-3d, rainbow palettes,
  CVD-unsafe encodings, missing polarity and chartjunk. Ships
  optional `make_figure.py` (dataviz tier), `causal_estimate.py`
  (DoWhy + EconML) and `explain_model.py` (SHAP / Shapash / TimeSHAP /
  LIME) behind their own `requirements-*.txt`. Wired into
  `.pre-commit-hooks.yaml` (`front-figures-audit`), `validate_all.py`,
  the `front-ui-validate-skill` args and `TRIGGERS.md`.
- **`front-audio` diarization tier.** New optional scripts
  (`caption_diarize.py`, `diarize_from_nemo.py`,
  `identify_from_titanet.py`, `name_from_transcript.py`,
  `install_diarize.py`) plus `references/diarization.md`, gated behind
  `requirements-diarize.txt` (NVIDIA NeMo Sortformer + TitaNet). The
  captions tier is unchanged and still stdlib + pywhispercpp.
- **CI.** The diarization `requirements-diarize.txt` is skipped in the
  per-skill install loop — same rationale as the narration engines:
  it pulls `nemo_toolkit[asr]` (~2 GB, torch) and no default-lane test
  imports the diarize scripts.

### Version

- Shared `SKILL_VERSION` bumped to `0.16.0` across all ten
  `_argparse.py` copies.

## [0.15.1] — 2026-06-29 — restore `gemma3:4b` default

Patch release reverting the model-name swap that briefly landed
in v0.15.0. ``gemma3:4b`` (with the ``-mlx`` variant on Apple
Silicon) is the maintainer's canonical default and was always
available; the v0.15.0 swap to ``gemma3:4b`` was a misread of the
tag's availability.

### What changed

- Restored ``gemma3:4b`` (and the ``-mlx`` Apple-Silicon variant)
  as the default vision tag across 17 files: two ``front-vision``
  scripts, three ``front-publish`` Ollama-backed scripts
  (``_ollama.py``, ``meta_from_ollama.py``, ``narrate_post.py``),
  the ``front a11y alt`` help text in ``front-cli``, four
  SKILL.md / reference files
  (``front-vision/SKILL.md``,
  ``front-vision/references/alt-text-ai.md``,
  ``front-accessibility/SKILL.md``,
  ``front-ui/references/ui-guidelines/foundations/images.md``,
  ``front-publish/references/audio-narration.md``), and the
  top-level docs (``README``, ``LISEZMOI``, ``LANDSCAPE``,
  ``CONTRIBUTING``, ``llms.txt``).
- ``TRIGGERS.md`` regenerated through the build_triggers script
  so the projection matches the restored description text.
- Removed the MLX → base auto-fallback in
  ``front-vision/scripts/install_alt_ai.py``. Silently
  downgrading to the non-MLX variant on a failed pull would change
  perf + accuracy characteristics under the user's nose. The new
  failure message names the exact ``ollama pull <tag>`` command to
  run when the registry hasn't propagated a fresh tag yet — match
  for how the maintainer bootstrapped the tag in the first place.

### Versions

All eight ``SKILL.md`` frontmatter versions, all eight
``_argparse.py`` and three ``_click.py`` ``SKILL_VERSION``
constants, and ``front-cli/pyproject.toml`` bumped to ``0.15.1``.

461 tests pass; spec validator green on all eight skills.

## [0.15.0] — 2026-06-29 — TRIGGERS.md + drift hook

Two coherent moves since v0.14.0: a generated trigger-phrase index
that humans can browse, and an automated drift gate that keeps the
index honest.

### Note on `gemma3:4b` default

An intermediate commit during v0.15.0 development swapped the
``front-vision`` default from ``gemma3:4b`` to ``gemma3:4b`` on
the (mistaken) assumption the former was a forward-looking tag.
The maintainer reverted the swap before the next release —
``gemma3:4b`` (with the ``-mlx`` variant on Apple Silicon) is
the canonical default and was always available. The
``install_alt_ai.py`` script no longer auto-falls-back to the
non-MLX base on a failed pull; it now exits with an actionable
message telling the user to ``ollama pull <tag>`` themselves
when the registry doesn't have a fresh tag yet, rather than
silently downgrading model quality / perf characteristics.

### `TRIGGERS.md` — generated trigger-phrase reference

A repo-root quick-reference table mapping every guaranteed trigger
phrase to the skill it activates and that skill's status. Three
columns: ``Trigger phrase | Activates | Status``. Hand-edit
forbidden by convention; CI enforces it (see the drift hook below).

How it works:

- ``scripts/build_triggers.py`` reads each SKILL.md's
  ``description`` field via YAML frontmatter parsing, extracts the
  quoted trigger phrases by regex, and renders the table.
- ``STATUS`` and ``WHAT_IT_DOES`` constants inside the script are
  the only manual surface. Adding skill #9 forces an explicit
  decision on both via the test parametrisation across
  ``SHIPPED_SKILLS``.
- ``--check`` mode diffs the generated output against the committed
  ``TRIGGERS.md`` and exits 1 on mismatch.

New ``tests/test_triggers_md.py`` (26 tests) asserts existence,
shape, completeness, and exact-match drift. README + LISEZMOI gain
a blockquote at the end of their skill table pointing users at
``TRIGGERS.md`` for "what should I say to invoke X" lookup.

### Drift hook — `front-triggers-sync`

A new entry in ``.pre-commit-hooks.yaml`` that runs
``scripts/build_triggers.py --check`` on every commit touching a
``SKILL.md``, ``TRIGGERS.md``, or the generator itself. Refuses
the commit when the two have diverged, with a one-line stderr
pointing the user at ``python scripts/build_triggers.py`` +
re-stage. Auto-recoverable — never blocks on a human judgement
call.

This is the third drift hook in the repo (``front-ui-validate-skill``
gates SKILL.md ↔ Anthropic spec; ``front-publish-lint-markdown``
gates markdown ↔ housekeeping rules). The shape generalises:
**file pair + generator + ``--check`` flag + pre-commit entry**.

### `audit_contrast --fix` asymmetry — documented as intentional

While auditing today's work, I noticed
``front-colors/scripts/audit_contrast.py``'s ``--fix`` mode is
**suggest-only** while the other three auditors'
``--fix`` modes apply edits in place. That asymmetry is by
design: changing a brand hex is a design decision, not a
mechanical repair. Auto-applying would create silent brand-drift
risk that mechanical fixes (adding ``min-h-11``, stripping
redundant ARIA, chunking digits) do not.

``front-colors/SKILL.md`` "Two modes" table now carries a
"Note on --fix semantics" subsection explaining the design intent
so future contributors don't "harmonise" the inconsistency away.

### Tests + spec

453 tests pass. ``scripts/validate_all.py`` green on all eight
skills. CI green on every push since the v0.14.0 cut.

## [0.14.0] — 2026-06-29 — cli_to_gui shape protocol + BSD-3-Clause

Two coherent moves landed since the v0.13.0 cut.

### cli_to_gui — adapter protocol (argparse + Click + --from-help)

The make-side emitter introduced in v0.12.0 was argparse-only.
v0.14.0 generalises the introspection to a small shape-adapter
protocol — the HTML renderer now consumes a canonical
``ParserTree`` dict (``prog`` / ``description`` / ``actions`` /
``sub_commands``) regardless of the source framework. Three
adapters ship today:

- **argparse** (stdlib, default; ``walk_parser``).
- **Click** (opt-in, imported lazily; ``walk_click``). Typer apps
  work via their underlying Click group. Bumps the deprecated
  ``click.BaseCommand`` to ``click.Command`` for Click 9
  compatibility. Click 8.2's ``Sentinel.UNSET`` default is
  treated as "no default" so the HTML emitter does not stamp the
  sentinel into ``value="…"``.
- **``--from-help``** (subprocess + regex; ``walk_from_help``).
  Runs ``<command> --help`` and parses the standard sections
  (``Usage:`` / ``Options:`` / ``Commands:`` / ``Positional
  arguments:``). Works on **any** CLI that emits a conventional
  help block: argparse, Click, Typer, clap (Rust), cobra (Go),
  commander (Node), hand-rolled shell scripts. Lower fidelity —
  everything maps to ``"text"`` unless a recognised METAVAR
  (``PATH`` / ``INT`` / ``FLOAT``), a ``[default: …]`` hint, or a
  choice list is visible. The prog-name extractor walks past
  common interpreters (``python3``, ``uvx``, ``node``, ``ruby``,
  ``bash``, …) so ``python3 script.py`` resolves to ``script``.

The public ``walk(obj)`` dispatches by type; adding a fourth
adapter is a new function + the same dict — the renderer does not
move.

The emitter is its own customer across all three adapters: the test
suite asserts the HTML emitted from each passes both the
``front-ux-laws`` audit AND the ``front-accessibility`` lint with
zero findings.

Tests
-----

Eleven new tests in tests/test_cli_to_gui.py:

- Click adapter: dispatch, every parameter kind, HTML passes both
  audits, walk() rejects unsupported objects, argparse↔Click tree
  shape parity.
- ``--from-help``: argparse fixture, choice metadata preserved,
  HTML passes both audits, prog wrapper-stripping, the
  ``--from-help`` CLI flag, ``--help`` advertises the flag.

The argparse fixture now ships ``if __name__ == "__main__":
make_parser().parse_args()`` so ``--help`` actually reaches stdout
on the subprocess path.

### License switch — BSD-3-Clause

The repo moves from The Unlicense to **BSD-3-Clause** (same license
as scikit-learn). Permissive (use, modify, redistribute, sell, ship
in commercial products) with three explicit conditions: copyright
notice in source, in binary distribution docs, no
endorsement-without-permission. Stronger fit for users who need a
recognised SPDX identifier — BSD-3-Clause is universally accepted;
Unlicense often trips procurement / code-import audits.

Files touched (17): LICENSE.md, all eight SKILL.md frontmatters,
front-cli/pyproject.toml, README + LISEZMOI license sections,
CONTRIBUTING vendoring policy, SECURITY opening, LANDSCAPE
per-script table cells, llms.txt header + LICENSE.md row.

The Roboto / Roboto Serif / Roboto Mono OFL carve-out and the
Common Voice CC0 fixture carve-out are unchanged — they apply to
the bundled assets themselves regardless of repo license.

### Thanks

The Click adapter that opened this whole shape-protocol direction
came from a conversation with [Auguste
Baum](https://www.linkedin.com/in/auguste-baum/). README + LISEZMOI
"Special thanks" now include the credit.

### Tests + spec

427 tests pass. ``scripts/validate_all.py`` green on all eight
skills. CI green on every push.

## [0.13.0] — 2026-06-29 — make-side completion + user-activation surface

Continues the autonomous overnight build-out that v0.12.0 opened.
Four more moves: the third `--fix` mode, a real-user activation
surface, a safety note for the new local-execution scripts, and the
law-keyed snippet catalog that closes the make-side on front-ui.

### `lint_markdown.py --fix` extended for MD009

The existing `--fix` flag was scoped to Mermaid PNG insertions; it
now also fixes MD009 (trailing whitespace). Preserves the canonical
two-space Markdown `<br>`; idempotent; leaves prose untouched.

This brings the markdown lint into the same audit↔make pattern as
`front-ux-laws --fix` and `front-accessibility --fix`. New
`tests/test_lint_markdown_fix.py` (11 tests) covers every shape
the spec cares about plus a CLI integration test that confirms the
re-lint shows zero MD009 findings after a single `--fix` pass.

### `.pre-commit-hooks.yaml` — first real-user activation surface

External projects can now wire all front-* audit gates with a
single `repos:` block:

```yaml
repos:
  - repo: https://github.com/warith-harchaoui/front
    rev: v0.13.0
    hooks:
      - id: front-accessibility-lint
      - id: front-ux-laws-audit
      - id: front-publish-lint-markdown
      - id: front-ui-validate-skill
      - id: front-colors-contrast
```

`.gitignore` carried a blanket `.*` rule with only two exceptions
(`.github/`, `.gitignore`); added `.pre-commit-hooks.yaml` to the
allow-list so the manifest actually ships. New
`tests/test_pre_commit_hooks.py` (19 tests) guards the manifest
against drift: every entry's `entry` script must exist on disk;
hook ids must be kebab-case + unique; every audit-side skill in
`SKILLS.txt` must be referenced (front-vision / front-audio /
front-cli-gui exempt with justification — make-only or covered
indirectly).

README + LISEZMOI gain a "Pre-commit hooks" section showing the
canonical wiring with the `args: [--fix]` pattern for hooks that
ship a fix mode.

### `SECURITY.md` — local-execution caveats

Two new scripts in this release run code the user names on the
command line: `cli_to_gui.py` imports the target parser module
(top-level side effects run at GUI-generation time); the
Ollama-backed scripts hand content to a local daemon. Both are
intentional design choices but a "should I trust this script"
audit needs the surface called out explicitly.

The new "Local execution caveats" subsection sits between the
existing "Disclosure" and "Supply-chain notes" sections — says:
treat `cli_to_gui`'s spec argument like `python -c '…'`; do not
pipe the Ollama-backed scripts content you would not show to the
local model.

### Snippet catalog at `front-ui/assets/snippets/`

The make-side gap front-ui still had after v0.12.0: references +
component-shape primaries existed
(`assets/components/{button,card,modal,form-field,nav}.html`)
but there was no **law-keyed** catalog — no snippet the agent
could load when the user said "IBAN field", "success screen",
"loading skeleton", "settings page".

Eight snippets, one per mechanically-implementable Law of UX:

| Snippet | Law |
|---|---|
| `miller-iban-input.html` | Miller's Law |
| `peak-end-success.html` | Peak-End Rule |
| `goal-gradient-progress.html` | Goal-Gradient Effect |
| `doherty-skeleton.html` | Doherty Threshold |
| `von-restorff-cta.html` | Von Restorff Effect |
| `jakob-native-controls.html` | Jakob's Law |
| `chunking-settings.html` | Chunking |
| `zeigarnik-resume.html` | Zeigarnik Effect |

Every snippet ships dark-mode peers, focus-visible rings, 44 px
hit areas and `prefers-reduced-motion` guards. The catalog is the
make-side counterpart to `audit_laws_of_ux.py --fix`: the auditor
repairs what the agent emits; the catalog gives the agent shapes
worth emitting in the first place.

New `front-ui/assets/snippets/INDEX.md` maps each file → the law
it embodies → 2-4 trigger phrases for agent lookup. New
`tests/test_snippet_catalog.py` (29 tests) parametrises every
snippet through BOTH `front-ux-laws` audit AND `front-accessibility`
lint, asserting zero findings from each — the catalog is its own
customer. Also enforces INDEX.md ↔ disk symmetry and that every
snippet opens with an explanatory HTML comment.

`front-ui/SKILL.md`'s Assets section + Decision tree updated so
the trigger phrases route to the INDEX.

### Why only eight laws (not all 30)

Of the 30 laws in `front-ux-laws/references/laws-of-ux.md` only
eight have a self-contained HTML embodiment. The rest (Hick,
Cognitive Load, Tesler, Postel, Aesthetic-Usability, Selective
Attention, …) are *meta*-laws that constrain every surface rather
than producing a discrete one. They live as audit rules + decision
hooks in the reference, not as snippets here.

### Tests + spec

405 tests pass. `scripts/validate_all.py` green on all eight
skills. CI green on every post-v0.12.0 push.

## [0.12.0] — 2026-06-29 — make-side build-out + repo plumbing

Investments executed against `.private/ASSESSMENT.md`'s ranked
priorities. Four moves landed in one session.

### CI repair

`fix(ci): repoint per-skill requirements glob to post-rename folders`
— `.github/workflows/ci.yml` still globbed `front-a11y/scripts/
requirements-*.txt`, which has not existed since the 0.9.0 rename.
Bash without `nullglob` expanded the empty glob to the literal
pattern, pip choked, every push since the rename failed. Fix:
`shopt -s nullglob` + a glob across the seven skill folders that
ship requirements. CI is now green.

### `SKILLS.txt` — single source of truth

`refactor(skills): single SKILLS.txt manifest at repo root` — the
shipped skill list lived in seven hand-maintained tuples
(`release.sh`, `validate_all.py`, `conftest.py`,
`test_validate_skill.py`, `test_release_packaging.py`,
`test_two_modes_discipline.py`, `test_cli_help.py`). Adding skill
#9 used to require seven identical edits. Now: one line in
`SKILLS.txt`. New `scripts/skills_manifest.py` exposes
`SHIPPED_SKILLS` to every Python consumer; the bash side reads the
same file via a portable `while read` loop. New
`tests/test_skills_manifest.py` (8 tests) guards against orphan
folders, missing folders, malformed parses, AND a future refactor
that "helpfully" re-introduces a hard-coded tuple.

### `--fix` on two auditors

`feat(front-ux-laws): add --fix mode with four mechanical fixers`

- Fitts                → inserts `min-h-11` into the offending
                         element's class list (44 px hit area).
- Aesthetic-Usability  → inserts the house focus-visible tokens.
- Miller               → replaces a long digit-bearing run with an
                         NBSP-chunked version (4-char groups, right
                         aligned).
- Jakob                → rewrites a clickable `<div>` / `<span>` to
                         a real `<button>`, strips the redundant
                         role attribute, renames the close tag.

`feat(front-accessibility): add --fix mode with five safe mechanical fixers`

- `html-missing-lang`         → injects `lang="en"` (honours
                                `FRONT_LANG_PAIR` for non-EN
                                defaults: "fr,en" → `lang="fr"`).
- `img-redundant-aria`        → strips redundant
                                `role="presentation"` /
                                `aria-hidden="true"` from
                                `<img alt="">`.
- `tabindex-positive`         → demotes `tabindex="N>0"` to `0`.
- `aria-hidden-interactive`   → strips `aria-hidden` from interactive
                                elements.
- `motion-no-reduce-guard`    → appends
                                `motion-reduce:transform-none`.

Both modes are idempotent (fix→audit→fix loop converges in ≤5 passes;
single-quoted attribute regex fix landed mid-session), both ship a
`--dry-run` preview, both report unfixable laws / rules honestly via
the `skipped` counter so users know which findings still need a
human decision.

### `cli_to_gui.py` — closes the last roadmap cell

`feat(front-cli-gui): add cli_to_gui.py — argparse → HTML emitter`

The front-cli-gui skill's roadmap-only make-side cell is now filled.
`scripts/cli_to_gui.py` introspects a Python CLI's
`argparse.ArgumentParser` and emits a single-page vanilla-JS +
Tailwind GUI: one `<details>` per sub-command, form fields mapped
per action kind, "Build command" button assembling the CLI line
client-side. The emitter is its own customer — `tests/test_cli_to_gui.py`
asserts the output passes both `front-ux-laws` and
`front-accessibility` auditors with zero findings.

### Description tightening

Two skills had been creeping toward the Anthropic 1024-char
description cap:

- `front-publish`: 991 → 862 chars (129-char trim, comfortable
  headroom).
- `front-audio`: 930 → 788 chars (142-char trim, biggest headroom
  in the set now).

### Tests + spec

346 tests pass. `scripts/validate_all.py` green on all eight
skills. CI green on the post-fix commits. Every shipped skill
carries a `## Two modes — make and audit` section + an entry in
the README / LISEZMOI matrices; `tests/test_two_modes_discipline.py`
enforces both on every commit.

## [0.11.0] — 2026-06-28 — make ↔ audit discipline + palette emitter

The front-* repo's design principle — every skill belongs to either
the *make* side or the *audit* side of a single loop — is now
codified in three places and enforced by tests.

### New: repo-level make / audit matrix

- `README.md` and `LISEZMOI.md` gain a "Two modes — make and audit"
  table listing every shipped skill against both axes. Empty cells
  are marked `_(roadmap)_` rather than omitted so the gaps are honest.
- Every shipped `SKILL.md` (eight in total) carries a small
  "Two modes — make and audit" subsection mapping its scripts /
  assets / references to the side they live on.

### New: `tests/test_two_modes_discipline.py`

Enforces the convention on every commit:

- Every shipped `SKILL.md` carries the canonical
  `## Two modes — make and audit` header.
- The subsection names both `Make` and `Audit` (case-insensitive).
- `README.md` + `LISEZMOI.md` matrices list every shipped skill
  exactly once.
- Empty cells in the README matrix must be marked `(roadmap)` or
  `(none — ...)`.

### New: `front-colors/scripts/palette_to_tailwind.py`

A make-side script that closes the CSV → Tailwind-config loop so
brand tokens cannot drift between the canonical
`front-colors/references/palette.csv` and the consumer projects:

- `--emit theme` (default): the `colors: { brand: { … } }` block to
  paste into an existing `tailwind.config.js`.
- `--emit config`: a complete `module.exports = { … }` matching
  `front-ui/references/stack-tailwind.md` (Roboto fontFamily, dark
  mode strategy, the label / surface / separator tokens, rounded /
  blur / motion extensions, plugins).
- `--with-dark`: OKLCH-L-bumped dark variants derived in-script
  (delta = 0.03). Honest about the derivation — comments in the
  emitted file mark them as derived, not as exact Apple values.
- `--include-neutrals`: opt-in for Brown / Black / Gray / White
  (they normally live under surface / label, not brand).

New `tests/test_palette_to_tailwind.py` covers all eight saturated
bases, the include-neutrals opt-in, the full-config shape, the
`--out` flag, the `--with-dark` derivation, and the CLI surface.

### Repo color consistency

- `front-colors/references/palette.csv` Purple `LightHex` was
  `#FFDCF8` (CSV) versus `#EFDCF8` in two consumer docs
  (`front-ui/references/stack-tailwind.md` and
  `color-psychology.md`). The CSV was the outlier; aligned to
  `#EFDCF8` so the emitter, the Tailwind reference, and the
  color-psychology doc agree.
- `front-ui/references/color-psychology.md` and
  `front-ui/references/stack-tailwind.md` now both declare
  `palette.csv` as the single source of truth and link to the
  emitter for regeneration.
- New "Curated default — user colors win" rule (mirror of the
  three-Roboto carve-out): the CSV is the default; a user-supplied
  palette wins.

### Fixed: stale `light_variant` test

`tests/test_colors_module.py::test_light_variant_for_neutral_is_none`
expected `None` for `Black` / `Brown`, but the palette CSV now
carries `LightHex` for every row (added in a prior commit).
Renamed to `test_light_variant_for_neutral_returns_curated_hex` and
updated assertions to the curated values.

## [0.10.0] — 2026-06-28 — new skill `front-ux-laws`

A new skill that adds the canonical **Laws of UX** (Jon Yablonski,
[lawsofux.com](https://lawsofux.com/)) to the front-* ecosystem in
both modes the repo already supports: **making** UI and **auditing**
the result.

### New skill: `front-ux-laws`

- `SKILL.md` — frontmatter validates against the Anthropic skill spec
  (kebab-case name, description under 1024 chars with explicit What +
  When, no XML brackets, no reserved name, no `README.md` inside the
  folder).
- `references/laws-of-ux.md` — restates all **30** laws on the
  canonical site (the curated set has grown beyond the original 21
  — Paradox of Active User, Flow, Choice Overload, Complexity Bias
  joined in the 2nd-edition book and the live index). Each entry is
  one row: **trigger → action → Tailwind / HTML hook**. Definitions
  and origins verified by recursive crawl of every `/<slug>/` page.
  Postel's Law carries a "read this caveat first" subsection sourced
  from the [Wikipedia *Robustness Principle* article](https://en.wikipedia.org/wiki/Robustness_principle)
  (the Rose 2001 / Thomson & Schinazi RFC 9413 2023 critique that
  UX writers often omit). The Aesthetic-Usability entry quotes
  [NN/g (Moran & Whitenton, Feb 2024)](https://www.nngroup.com/articles/aesthetic-usability-effect/).
- `scripts/audit_laws_of_ux.py` — Python 3.9+ stdlib-only static
  auditor. Eight checks: Hick, Choice Overload, Miller, Jakob, Fitts,
  Aesthetic-Usability, Selective Attention, Tesler. `--json`,
  `--strict`, `--only LAW1,LAW2`, `--ignore LAW1,LAW2`. Exit codes
  for pre-commit / CI. Heuristics tuned against
  `front-ui/assets/components/`: Hick collapses radiogroups /
  tablists to one logical choice; Miller requires at least one digit
  in the run (so "collaborators" / "implementation" do not fire);
  Tesler accepts a TZ token within a 40-char window.
- `scripts/_argparse.py` — copied per the established per-skill
  autonomy convention; provides `-V` / `--version`.

### Companion-skill updates

- `front-ui/SKILL.md`: companion-skills table + decision-tree row
  added.
- `front-ui/references/ux-psychology.md`: banner cross-link pointing
  to the canonical set; the two files deliberately overlap.

### Tests + tooling

- New `tests/test_audit_laws_of_ux.py` — 24 tests covering the eight
  checks, the false-positive suppressions, and the CLI surface
  (`--version`, `--help`, `--json`, `--strict`, `--only`, `--ignore`,
  unknown-law error).
- `scripts/validate_all.py`, `scripts/release.sh`,
  `tests/conftest.py`, `tests/test_validate_skill.py`,
  `tests/test_release_packaging.py`, `tests/test_cli_help.py` all
  extended for the new skill — the eight-skill repo now lights up
  through every cross-skill validator.

### Sources studied

- lawsofux.com — full recursive crawl: homepage, all 30 law pages,
  `/articles/` index, `/book/`, the *Onboarding for Active Users*
  essay.
- Two outside reads, picked deliberately: NN/g's article on the
  Aesthetic-Usability Effect (because the effect itself warns the
  rest of the auditor cannot be trusted as a substitute for user
  observation); Wikipedia's Robustness Principle article (because
  Postel's Law has a real dark side UX writers tend to skip).
- Anthropic, *The Complete Guide to Building Skills for Claude*
  (PDF, 2026) — the new skill's layout was checked against the
  guide's frontmatter / folder / progressive-disclosure rules.

## [0.9.0] — 2026-06-28 — `front-audio` split + `front-a11y` renamed to `front-accessibility`

After the v0.7.0 (`front-colors`) and v0.8.0 (`front-vision`) splits,
the remaining `front-a11y` skill was unbalanced: an HTML lint script
plus a WIP whisper.cpp captions pipeline that has nothing to do with
HTML. This release ships the final split and a long-overdue rename.

### New skill: `front-audio`

- `scripts/captions_from_whisper.py` — moved from
  `front-a11y/scripts/`. Same CLI, new program name
  `front-audio-captions`. WebVTT / SRT / plain-text captions via local
  whisper.cpp with project-vocab biasing — semantics unchanged.
- `scripts/install_captions.py` — moved from `front-a11y/scripts/`.
  Same CLI, new program name `front-audio-install`. Installs
  `pywhispercpp` and pre-downloads a GGML model.
- `scripts/_argparse.py` / `_click.py` / `_lang.py` / `_vocab.py` —
  copied (per the established per-skill autonomy convention).
- `references/captions-ai.md` — moved from `front-a11y/references/`.

The captions pipeline remains explicitly **WiP** for the same reasons
as before (WER baselines pending, `vocab-biasing-clip.wav` pending),
plus an upcoming improvement to the whisper.cpp integration via
**`pdbms`** that the maintainer is preparing. Trackshape via
`tests/fixtures/audio/README.md`.

### Renamed skill: `front-a11y` → `front-accessibility`

The `a11y` numeronym is community-fluent but trades discoverability
for insiderness — ironic for an accessibility skill. The other front
skills are immediately legible (`front-ui`, `front-publish`,
`front-cli-gui`, `front-colors`, `front-vision`, `front-audio`); the
new name brings `front-accessibility` in line.

- Directory renamed: `front-a11y/` → `front-accessibility/`.
- `SKILL.md` `name:` field updated.
- All scripts' `prog=` strings updated (`front-a11y-lint` →
  `front-accessibility-lint`).
- Every path reference (`front-a11y/scripts/...`,
  `front-a11y/references/...`) rewritten across every doc, every test,
  every other SKILL.md.
- CLI router: group renamed from `a11y` to `accessibility`. Old:
  `front a11y lint`. New: `front accessibility lint`.
- The lint script's filename stays `lint_a11y.py` — the term `a11y`
  remains the right name for the *tool* (the script does an a11y lint
  in the WAI/WCAG sense). The change is to the *skill folder* / *CLI
  group*, where discoverability matters.

`front-accessibility` is now narrowly scoped to one thing: 14-rule
static HTML accessibility lint, stdlib only, no third-party deps, no
browser, no network. `metadata.version` → `0.9.0`.

### CLI

- New group `front audio` with leaf commands `front audio captions`
  and `front audio install`.
- Removed `front a11y captions` and `front a11y install-captions`.
- Renamed group `front a11y …` → `front accessibility …` for the
  remaining `lint` command (and any future `accessibility-*` scripts).

### Repo plumbing (now at 7 skills)

- `scripts/release.sh` SKILLS array += `front-audio` and rewritten for
  the new `front-accessibility` name.
- `scripts/validate_all.py` SKILLS tuple updated.
- `tests/conftest.py` adds `front-audio/scripts` and points to
  `front-accessibility/scripts` (was `front-a11y/scripts`).
- `tests/test_release_packaging.py`, `tests/test_validate_skill.py`,
  `tests/test_cli_help.py` updated for the new skill set and the
  renamed skill. The validator now asserts
  `"PASS — all 7 skill(s)"`.

### `front-accessibility/scripts/` pruning

After moving the captions code out and the alt-text / Ollama code
having been moved out in 0.8.0, several internal helpers
(`_click.py`, `_lang.py`, `_ollama.py`, `_prompts.py`, `_vocab.py`)
were no longer referenced by anything inside the skill. They're
removed; `front-accessibility/scripts/` is now just `lint_a11y.py` +
`_argparse.py`.

### Documentation

- `README.md` + `LISEZMOI.md` skill tables gain a seventh row for
  `front-audio`. The `front-accessibility` row narrows to lint-only
  triggers.
- Every cross-skill mention rewritten (lang_pair lockstep lists,
  decision-tree references, end-to-end deliverable examples, install
  instructions).
- `front-cli/README.md` CLI examples show `front accessibility lint`
  / `front audio captions` / etc.

### Why now

- Three intents lived under one skill: HTML lint (decidable from
  source), AI captions (whisper.cpp, audio→text), AI alt text
  (Ollama, vision). The first is text-shaped, the second audio-shaped,
  the third image-shaped. Sharing a skill folder under the
  `front-a11y` name was historical, not architectural.
- The 0.7.0 and 0.8.0 splits demonstrated the pattern: one skill, one
  intent, autonomy via per-skill duplicated helpers. Finishing the
  pattern by splitting `front-audio` was mechanical.
- The rename to `front-accessibility` was overdue and removes the
  accessibility-tooling-with-an-inaccessible-name irony.

## [0.8.0] — 2026-06-28 — `front-vision` skill split out of `front-a11y`

The AI alt-text path (Ollama vision model, per-purpose YAML prompts,
surrounding-text + vocabulary biasing, on-disk cache) was always a
distinct concern from static HTML accessibility linting and audio
captions. This release ships the split, alongside a default-model bump.

### New skill: `front-vision`

- `scripts/alt_from_ollama.py` — moved from `front-a11y/scripts/`. Same
  CLI, new program name `front-vision-alt`. Per-purpose decision tree
  (informative / decorative / functional / text / complex / group),
  surrounding-text + vocabulary biasing, on-disk cache, EN/FR default
  (configurable via `lang_pair`) — all unchanged.
- `scripts/install_alt_ai.py` — moved from `front-a11y/scripts/`. Same
  CLI, new program name `front-vision-install`. Installs the Ollama
  daemon (brew on macOS, official installer on Linux, winget on
  Windows) and pulls the default vision model.
- `scripts/prompts/*.yaml` — the nine per-purpose alt-text prompt
  templates moved from `front-a11y/scripts/prompts/`.
- `scripts/{_argparse,_click,_lang,_prompts,_vocab}.py` — copied (per the
  established per-skill autonomy convention); the originals stay in
  `front-a11y/scripts/` because `captions_from_whisper.py` still uses
  them.
- `references/alt-text-ai.md` — moved from `front-a11y/references/`.

### Default model bumped: `gemma4:e2b` → `gemma3:4b`

The default vision model is now **`gemma3:4b`** (the larger 4B-parameter
edge variant), with the `-mlx` suffix still auto-appended on
Apple-silicon Macs. Override paths are unchanged:

1. `--model <tag>` on the command line.
2. `OLLAMA_MODEL=<tag>` env var (full tag including any `-mlx`).
3. `OLLAMA_MODEL_BASE=<base>` env var (skill appends `-mlx` on
   MLX-capable hardware).
4. The built-in default above.

`install_alt_ai.py` pulls the new default on first run; existing users
on `gemma4:e2b` keep working until they re-run the installer.

### `front-a11y` further narrowed

After the v0.7.0 split that took colour audits out, this release takes
AI alt text out as well. `front-a11y` is now scoped strictly to:

- `lint_a11y.py` — 14-rule static a11y lint (stdlib only).
- `captions_from_whisper.py` (WiP) + `install_captions.py` — local
  WebVTT / SRT captions via whisper.cpp.

SKILL.md frontmatter (`description`, `compatibility`) updated; the
"Tools" / "Decision tree" / "Tool composition" / "Scripts" / "References"
sections all drop the alt-text rows. Companion-skills row added pointing
to `front-vision`. `metadata.version` → `0.8.0`.

### CLI

- New group `front vision` with leaf commands `front vision alt` and
  `front vision install`.
- Removed `front a11y alt` and `front a11y install-alt-ai` (breaking —
  but the scripts moved, the CLI follows).

### Documentation

- README + LISEZMOI skill tables gain a sixth row for `front-vision`.
  `front-a11y` row narrows to lint + captions triggers.
- `llms.txt` lists the new script paths and the default model.
- Every reference to `front-a11y/scripts/alt_from_ollama.py` or
  `front-a11y/scripts/install_alt_ai.py` across `front-publish/`,
  `front-ui/`, `front-cli/README.md`, `LANDSCAPE.md` rewritten to
  `front-vision/scripts/...`.

### Repo plumbing

- `scripts/release.sh` SKILLS array += `front-vision`.
- `scripts/validate_all.py` SKILLS tuple += `front-vision`.
- `tests/conftest.py` adds `front-vision/scripts` to the test sys.path.
- `tests/test_release_packaging.py`, `tests/test_validate_skill.py`,
  `tests/test_cli_help.py`, `tests/test_prompts.py` updated for the new
  skill (the nine `alt_*` prompt rows now point at `front-vision`).

### Why now

- The trigger phrase set `"alt text"` / `"describe this image"` /
  `"draft alt"` is a distinct user intent from `"a11y lint"` and from
  `"captions"`. Three intents in one skill diluted both the trigger
  match and the skill's description (≤1024 chars limit was getting
  tight).
- The alt-text path is the only place in the family that needs a vision
  model on disk; isolating it makes the install footprint optional for
  users who only want HTML lint.
- The naming `front-vision` is honest about what the skill does (local
  vision-model AI) and leaves room for future vision-only features
  (image OCR, layout reasoning) without re-scoping.

## [0.7.0] — 2026-06-28 — `front-colors` skill split out of `front-a11y`

Color tooling (WCAG contrast audit, OKLCH-neighbour fix suggester, CVD
simulation) was always a separate concern from accessibility lint and AI
content drafting. This release ships the split, plus the curated palette
that previously lived as an external Python library
([`colors-helper`](https://github.com/warith-harchaoui/colors-helper)) —
now archived in favour of the new skill.

### New skill: `front-colors`

- `scripts/audit_contrast.py` — moved from `front-a11y/scripts/`. Same CLI,
  new program name `front-colors-contrast`. The fix suggester (OKLCH L-axis
  walk) is unchanged.
- `scripts/simulate_cvd.py` — moved from `front-a11y/scripts/`. Same CLI,
  new program name `front-colors-cvd`. Machado et al. 2009 matrices
  unchanged.
- `scripts/_colors.py` — new internal helper consolidating sRGB ↔ linear,
  hex parsing, WCAG luminance / contrast (`meets_wcag(fg, bg, level, size)`
  added), OKLab / OKLCH conversions, perceptual `lighten` / `darken` on the
  OKLCH L axis (replaces the naïve `+70` RGB offset from `colors-helper`),
  CVD matrices, palette accessors (`apple_palette`, `name_to_hex`,
  `name_to_rgb`, `light_variant`, `emotion_to_hex`, `concept_search`,
  `psychology_for`), and a small `Color` ergonomic class.
  Used by both `audit_contrast` and `simulate_cvd`, killing the
  `srgb_to_linear` / `linear_to_srgb` duplication between them.
- `references/palette.csv` — unified curated palette. **One row per
  canonical color**, with semantic projections as columns:
  `Hexcode, R, G, B, Base, LightHex, Emotion, Concepts,
  PsychologyPositive, PsychologyNegative`. Twelve rows: the eight
  saturated Apple system colors plus Brown / Black / Gray / White
  (which carry psychology-only semantics). Replaces the four-CSV layout
  on harchaoui.org/warith/colors/ that duplicated the same hex values
  across files; the live page remains the public browseable view.

### `front-a11y` narrowed

- `audit_contrast.py`, `simulate_cvd.py`, `references/contrast-audit.md`
  and `references/cvd-simulation.md` moved to `front-colors`.
- `SKILL.md` description, decision tree, framing table, references list,
  and scripts table all updated. New companion-skills row pointing to
  `front-colors`.
- `metadata.version` → `0.7.0`.

### CLI

- New group `front colors` with leaf commands `front colors contrast` and
  `front colors cvd`.
- Removed `front a11y contrast` and `front a11y cvd` (breaking — but the
  scripts moved, the CLI follows). The new commands take the same flags.

### Documentation

- README + LISEZMOI skill tables get a fifth row for `front-colors`. The
  `front-a11y` row loses its color triggers.
- `llms.txt` lists the new scripts and the palette CSV.
- `front-publish/SKILL.md` and `front-cli/README.md` updated to reference
  the new locations.

### Repo plumbing

- `scripts/release.sh` SKILLS array += `front-colors`.
- `scripts/validate_all.py` SKILLS tuple += `front-colors`.
- `tests/conftest.py` adds `front-colors/scripts` to the test sys.path.
- `tests/test_release_packaging.py`, `tests/test_validate_skill.py`,
  `tests/test_cli_help.py` updated for the new skill.
- `tests/test_colors_module.py` — 64 new tests covering hex parsing,
  WCAG, OKLab/OKLCH round-trips, perceptual `lighten` / `darken` (with
  a direct comparison against the naïve RGB +70 approach the new code
  replaces), CVD matrices, palette accessors, and the `Color` class.

### Why now

- Triggers like `"WCAG check"`, `"contrast audit"`, `"colorblind preview"`
  are distinct user intents from `"a11y lint"` and `"alt text"`. Two skills
  with focused triggers serve those intents better than one umbrella skill.
- Color math was already accumulating: contrast (audit_contrast),
  CVD (simulate_cvd), and now palette curation + perceptual transforms
  (from `colors-helper`). Co-locating them avoids cross-skill imports
  (which skills don't do anyway) and gives the math a single home.
- `front-a11y`'s name is more accurate now that it's HTML accessibility
  lint + AI content drafting (alt text, captions), not "everything
  accessibility-adjacent".

### Acknowledgements

The unified palette draws on:
- Apple Human Interface Guidelines (macOS system colors)
- maketintsandshades.com (curated light counterparts)
- Color psychology associations from the user's published page
  <https://harchaoui.org/warith/colors/>

## [0.6.5] — 2026-06-23 — staleness sweep across SKILL descriptions + README status

Patch release. Doc and frontmatter hygiene only — no script behaviour
changes. Caught while sweeping the repo for decayed claims after the
0.5.x → 0.6.x string.

### Changed — `front-ui/SKILL.md` description

Rewrote the typography sentence to match the 0.6.4 carve-out. Before:
*"Three-Roboto typography rule: Roboto (sans), Roboto Serif (serif),
Roboto Mono (code/monospace); no other downloaded webfont."* — that
last clause is wrong post-0.6.4 (audits respect existing fonts;
user-named typefaces are honored). Now: *"Default typography is the
three-Roboto rule (Roboto sans + Roboto Serif + Roboto Mono); honors
user-specified fonts and respects existing typefaces when auditing
existing UI."*

### Changed — `front-publish/SKILL.md` description

The description had drifted behind the skill's actual scope. Now
mentions:
- **Audio narration** (added in 0.5.0 — was documented in the SKILL
  body but missing from the description, so it didn't surface as a
  trigger).
- **SEO + GEO** (Google's Search Essentials + AI Optimization
  foundations adapted in 0.6.2). Adds the trigger words "SEO",
  "AI Overview", "GEO", "narrate this post", "podcast my blog" so
  those queries actually route the skill.

Total length 1018 / 1024 chars — well under the Anthropic spec cap.

### Changed — README + LISEZMOI Status rows

The `front-publish` row in the Status table claimed *"4 scripts, 18
deterministic tests"*. Actual current state: 11 public scripts (4
core artifacts + Markdown → HTML + Markdown linter + 4 audio-
narration scripts + install helper) and broad deterministic coverage
across `tests/test_favicons.py`, `…site_indexes.py`, `…meta_from_ollama.py`,
`…plain_language.py`, `…lint_markdown.py`, `…narrate.py` (12 + 24 +
21 + 16 + 5 + 39 = 117 tests, plus the eval suite). Numbers like "4
scripts" decay every release; the rewritten row names the surfaces
instead of pinning counts. Same fix mirrored in `LISEZMOI.md`.

## [0.6.4] — 2026-06-22 — three-Roboto rule carve-out for audits

Patch release. Re-scopes the three-Roboto typography rule from "hard
constraint" to "default for generation", so audits and user-specified
fonts no longer get hijacked.

### Changed — hard rule 3 in `front-ui/SKILL.md`

The three-Roboto rule now applies **only** when generating fresh UI /
site output **and the user has not specified a typeface**. It does NOT
apply when:

1. **Auditing an existing site / UI.** A user asking to "audit this",
   "review this", "make it look less AI", or "WCAG check" should get
   feedback on ergonomics, a11y, anti-patterns — **not** an unsolicited
   font-swap recommendation. Respect the typefaces already in use.
2. **The user names a typeface.** "Use Inter", "we ship IBM Plex",
   "stick to system fonts" → use what they ask for.
3. **The user asks for a fourth family explicitly** for brand
   reasons → carry it out and record the choice in the project README
   so a future maintainer knows why.

This is a real behaviour change: before 0.6.4, an "audit this UI" run
could (and arguably should have, per the wording) push back on the
existing typeface as part of the review. Now it stays in its lane.

### Also changed

- **`front-ui/SKILL.md` decision tree** — the "audit / ergonomic
  review / UX review" row now explicitly says "Respect the existing
  typeface stack — do not propose a three-Roboto swap unless the user
  explicitly asks about typography."
- **`front-ui/references/ui-guidelines/foundations/typography.md`** —
  the "The fonts" section opens with the carve-out and renames itself
  to "the three-Roboto rule (generation-only default)".
- **`front-ui/references/stack-tailwind.md`** — same carve-out at the
  top of the typography section.

## [0.6.3] — 2026-06-22 — Anthropic skill-spec compliance audit

Patch release. Audited the four skills against
*The Complete Guide to Building Skills for Claude* (Anthropic) and
brought everything into spec.

### Fixed — README.md inside skill folders (spec violation)

The spec is explicit: "Don't include README.md inside your skill
folder. All documentation goes in SKILL.md or references/. Note: when
distributing via GitHub, you'll still want a repo-level README for
human visitors." The repo-level `README.md` and `LISEZMOI.md` are
fine and required; the nested ones were not.

- **Deleted** `front-ui/assets/fonts/README.md` (introduced in 0.6.0
  during the typography migration). Its content — the three-Roboto
  rule + wiring instructions — was redundant with
  `front-ui/references/ui-guidelines/foundations/typography.md`,
  which already documents Tailwind config, CSS variables, HTML
  preload, and the per-folder `fonts.css` layout. `front-ui/SKILL.md`
  assets list now points readers at the typography reference instead.
- **Renamed** `front-cli-gui/assets/examples/cli-gui-demo/README.md`
  → `RUNBOOK.md`. The cli-gui-demo is a runnable example, so a
  runbook (how to launch, what to read, where things live) earns its
  keep; we just can't call it `README.md` inside a skill folder. A
  leading note in the renamed file explains the rule for any reader
  who came in expecting a README.

### Hardened — validators catch the violation now

Both validators previously checked only the skill root, which is how
the fonts README slipped past CI in 0.6.0.

- `front-ui/scripts/validate.py` — Check 6 now uses `Path.rglob` to
  walk the whole skill tree.
- `scripts/validate_skill.py` — added Check 10 with the same
  rule; the cross-skill validator now reports every nested README
  with its path so the maintainer doesn't have to grep.
- `tests/test_validate_skill.py` — two new regression tests
  (`test_readme_at_skill_root_is_rejected`,
  `test_readme_nested_is_rejected`) lock the rule in. Total
  deterministic suite is now 425 tests.

### Added — `compatibility` frontmatter field

Optional per the spec, but recommended — declares the runtime
environment each skill needs. All four SKILL.md frontmatters now
carry a `compatibility:` block stating: which runtime hosts the skill
targets (Claude.ai / Claude Code / OpenCode), what Python version (if
any) the scripts need, which third-party deps each script needs, and
whether network access is required. Shapes future tool discovery
without expanding the description budget.

### Audited — clean on every other rule

- ✅ Folder names kebab-case (`front-ui`, `front-cli-gui`,
  `front-publish`, `front-a11y`) and match each `name:` field.
- ✅ `SKILL.md` filename exact (case-sensitive) on all four.
- ✅ Description ≤ 1024 chars on all four (770 / 751 / 886 / 867).
- ✅ Descriptions include both "what" and "when" with concrete
  trigger phrases.
- ✅ No XML angle brackets (`<` / `>`) in any description value.
- ✅ No reserved words (`claude` / `anthropic`) in any skill name.
- ✅ Every SKILL.md under 5 000 words (the spec's "large context"
  threshold).
- ✅ Python style (numpy-docstring module headers, full typing,
  authorship line) consistent across every shipped script.

## [0.6.2] — 2026-06-22 — SEO + GEO foundations from Google's official docs

Minor release. New canonical reference adapting Google's
search-foundations guidance to the artifacts `front-publish` already
emits, plus explicit SEO / GEO routing in the SKILL decision tree.

### Added

- **`front-publish/references/seo-essentials.md`** — the canonical
  adaptation of:
  - [Google Search Essentials](https://developers.google.com/search/docs/essentials)
    (technical requirements + spam policies + six key best practices)
  - [Google AI Optimization Guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
    ("Apply foundations" section — same foundations as Search
    Essentials for AI Overview / generative search; no new meta tag
    for AI)
  - [Google "Third-party SEO"](https://developers.google.com/search/docs/fundamentals/third-party-seo)
    (how to recognize legitimate vs. questionable third-party
    advice and tools)

  Each of Google's six key best practices is mapped to the script
  that already enforces it (`meta_from_ollama.py`, `site_indexes.py`,
  `plain_language.py`, `alt_from_ollama.py`, `captions_from_whisper.py`,
  `lint_markdown.py`, `lint_a11y.py`). A pre-ship checklist
  consolidates the rules into a single gate.

- **GEO vocabulary** (Generative Engine Optimization) made explicit.
  `scripts/site_indexes.py` already emits `llms.txt` on every site
  build alongside `robots.txt` + `sitemap.xml`; the new reference
  documents that it is the GEO artifact most agents look for, that
  GEO and SEO share crawlers, and that **no separate "AI" meta tag
  exists** (the skill refuses to emit one and cites the AI
  Optimization Guide).

- **`LANDSCAPE.md` § 14** — new SEO + GEO guidance landscape table
  comparing Google's three official docs, the llmstxt.org community
  convention, Bing's guidelines, Schema.org, SEO-tool blogs, and
  "Google-approved" SaaS badges (refused).

### Changed

- **`front-publish/SKILL.md`** — decision tree gained two routing
  rows: "SEO / AI search / AI Overview / discoverability / is this
  advice true?" → `seo-essentials.md`, and "GEO / llms.txt / make my
  site readable by ChatGPT / Gemini / Perplexity" → same reference
  with the GEO framing. References list updated.

- **`README.md` + `LISEZMOI.md`** — the "Meta tags / SEO / OG card"
  row in Inputs → outputs now explicitly covers SEO **and** GEO,
  notes that `llms.txt` is already emitted by `site_indexes.py`,
  and links the new reference for the full Google-foundations
  rationale.

- **`front-publish/references/meta-tags.md`** and **`site-indexes.md`**
  — cross-linked to `seo-essentials.md` from their authoritative-
  sources lists so the rule and the implementation point at each
  other.

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
