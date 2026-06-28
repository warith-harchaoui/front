# Contributing to `front`

The project is released into the public domain under
[The Unlicense](LICENSE.md) — you can use, modify, redistribute and sell
without permission, attribution or fee. Contributions are welcome on the
same terms.

## Before you start

Pick the skill your change belongs to:

| Change touches… | Skill |
|---|---|
| UI generation, components, design tokens, color, dataviz, design system, anti-patterns, ergonomic criteria, ux psychology, Apple HIG references | `front-ui/` |
| CLI → GUI workflow, the runnable demo, host adapters (Tauri / FastAPI / Express / stdlib SSE) | `front-cli-gui/` |
| Markdown → website workflow, meta tags, favicons, site indexes, plain-language rewriter, i18n | `front-publish/` |
| `lint_a11y.py` (static HTML a11y lint) | `front-accessibility/` |
| WCAG contrast audit, CVD simulation, curated palette, perceptual lighten / darken | `front-colors/` |
| W3C alt text via local Ollama vision (`gemma4:e4b` / `-mlx` on Apple silicon) | `front-vision/` |
| Local WebVTT / SRT captions via whisper.cpp | `front-audio/` |

Cross-skill changes (e.g. a stack rule that affects every skill) start in
`front-ui/` since it is the source of truth for the shared rules, then
the companion skills reference it.

## Local setup

```bash
git clone https://github.com/warith-harchaoui/front.git
cd front
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

The deterministic gates (`validate.py`, `lint_a11y.py`,
`audit_contrast.py`, `site_indexes.py`) are stdlib only. The
Ollama-backed scripts need a running Ollama daemon and the relevant
model — see each skill's `SKILL.md` for the install path.

## Running tests

```bash
pytest                  # default — fast, deterministic
pytest -m eval          # opt-in deepeval LLM-quality tests (need Ollama)
```

The default invocation skips the `eval` marker. Tests must pass before a
PR is merged.

## Conventions

- **No emojis in shipped files** (SKILL.md, references, scripts). The
  README header may use flag emojis for the language switcher only.
- **No marketing-voice phrases** in SKILL.md or references. The
  validator (`front-ui/scripts/validate.py`) catches the worst
  offenders.
- **Hard rules are hard.** If a change weakens rule 1–9 in any
  SKILL.md, document the reason in the PR description and update
  `CHANGELOG.md`.
- **Public-domain.** New files are released into the public domain. Do
  not include code copied from a license-restricted source without
  documenting the carve-out (see the Roboto / Roboto Serif / Roboto
  Mono OFL bundle as the template).

## What we ship

- Reproducible: stdlib-only validators run in any CI container.
- Honest: scope and limitations are stated, not hidden.
- Composable: each skill works on its own; companions are additive.
- Bilingual-ready: text content is written so a future translator can
  add a second language without touching markup.

## What we will not ship

- React / Vue / Svelte / Solid / Angular code. The skill refuses to
  emit framework code by design.
- Marketing voice ("seamlessly", "production-grade", "non-negotiable",
  "boost your productivity"). The validator gates on this.
- Auto-fix suggestions presented as final decisions for things that
  need a designer's eye (palette choices, typography pairings).

## Release process (maintainer)

Two equivalent paths; pick one per release and don't mix them.

- **Tag-only** (recommended). Bump the version in the four
  `SKILL.md` frontmatters + `README.md` / `LISEZMOI.md` install
  snippets + a new `CHANGELOG.md` section, commit, then
  `git tag -a v<version> -m "release v<version>" && git push origin
  main v<version>`. The `release.yml` workflow runs
  `scripts/release.sh` on the runner, publishes the GitHub release,
  attaches the five tarballs + `SHA256SUMS`, and generates notes
  from commits since the previous tag.

- **Local-build, then tag-push**. Run `scripts/release.sh <version>`
  to build into `dist/`, verify locally, then optionally publish
  manually with `gh release create v<version> dist/*.tar.gz
  dist/SHA256SUMS …`. The workflow still triggers on the tag push;
  since v0.6.1 the publish step is idempotent — it detects the
  existing release and skips with success rather than re-uploading
  and rewriting `SHA256SUMS`. (Before v0.6.1, the workflow exited 1
  with `a release with the same tag name already exists` whenever
  the maintainer published locally first.)

The artifacts the workflow uploads and the artifacts a local
`scripts/release.sh` produces are **not byte-identical** (gzip /
tar versions differ between macOS and the ubuntu-latest runner), so
the SHA256SUMS the user fetches depends on which path produced the
release. Either path is fine; pick one consciously.

## Reporting issues

GitHub issues at <https://github.com/warith-harchaoui/front/issues>.
For things that involve the Anthropic skill spec itself, also see
<https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf>.

## Maintainer

[Warith Harchaoui](https://www.linkedin.com/in/warith-harchaoui/).
