---
name: front-vision
description: >-
  W3C-compliant alt-text drafting via a local Ollama vision model — per-image
  decision tree for informative / decorative / functional / text / complex /
  group purposes, bilingual output (EN/FR default, configurable), surrounding-
  text and project-vocabulary biasing, deterministic on-disk cache so the same
  image + parameters never hit the model twice. Default model is
  ``gemma3:4b`` (the ``-mlx`` variant is auto-selected on Apple-silicon
  Macs); override with ``OLLAMA_MODEL`` / ``--model``. For solo developers
  and small teams who want accessibility content drafted locally with no
  SaaS cost or data exfiltration. Drafts are starting points — verify before
  committing. Trigger phrases: "alt text", "alt text for this image",
  "describe this image", "draft alt", "image description", "img has no
  alt", "decorative image". Output is plain text / JSON on stdout suitable
  for pre-commit and CI.
license: BSD-3-Clause
compatibility: >-
  Runtime: Claude.ai, Claude Code, OpenCode. Needs Python 3.9+ stdlib +
  Pillow + requests (see ``scripts/requirements-alt-text.txt``) and a
  running local Ollama daemon with a vision-capable model. The
  ``install_alt_ai.py`` script installs Ollama (brew on macOS, official
  installer on Linux, winget on Windows) and pulls the default model on
  first run.
metadata:
  author: Warith Harchaoui
  version: 0.1.0
  lang_pair: "en,fr"  # override per-project; e.g. "en,de" or "en,ja"
---

# front-vision — local AI alt text for accessibility

## Audience and positioning

Solo developers and small teams who:

- Need **W3C-compliant alt text** drafted from images at commit time, not
  at runtime via a hosted service.
- Want **local-first AI** — no SaaS, no data exfiltration, no per-image
  cost. Apple-silicon Macs get the MLX variant automatically.
- Want **bilingual output** (EN/FR by default; pair configurable via
  ``lang_pair``) without spelling out the language flag every time.
- Want **vocabulary biasing** so the model knows your product / brand /
  technical-term spellings before it hallucinates a near-miss.

This skill is **not** a substitute for a human review pass. Each draft is
tagged ``data-alt-source="ai"`` so a reviewer can find it later. Top-tier
hosted vision (Claude vision, GPT-4o vision, Gemini) is more accurate —
use this skill when local-only matters or when the volume makes hosted
costs unattractive.

## Two modes — make and audit

This skill is **make-only** in the front-* duality — by design:

| Mode | Tool | Purpose |
|---|---|---|
| **Make** — draft accessible image text | `scripts/alt_from_ollama.py` + `scripts/install_alt_ai.py` | W3C-compliant alt text via local Ollama vision (default `gemma3:4b`, `-mlx` auto-selected on Apple silicon). Per-purpose decision tree, surrounding-text + vocabulary biasing, on-disk cache. |
| **Audit** — gate the presence of `alt=` | _(see `front-accessibility/scripts/lint_a11y.py`)_ | Static lint catches `<img>` without `alt` and `<img alt="">` on non-decorative images. |

Pair with `front-accessibility` to close the loop: this skill drafts
the text; the a11y lint verifies it lands on every `<img>`.

## Honest framing of what each tool covers

| Tool | Catches | Misses |
|---|---|---|
| `scripts/alt_from_ollama.py` | W3C-compliant alt for informative / decorative / functional / text / complex / group purposes; per-purpose YAML prompt templates; surrounding-text + project-vocabulary biasing; on-disk cache | model-quality drafts — verify each draft before committing. Top-tier hosted vision (Claude vision, GPT-4o vision, Gemini) is more accurate. Decorative images get ``alt=""`` (no model call). |
| `scripts/install_alt_ai.py` | Installs the Ollama daemon on the host (brew / official installer / winget) and pulls the default vision model. Idempotent — safe to re-run. | does not auto-update an already-installed daemon or model; does not enforce GPU drivers; does not start the daemon as a service on Linux. |

## Decision tree

| Trigger | Tool | Run |
|---|---|---|
| "alt text" / `<img>` with no `alt` / "describe this image" | `alt_from_ollama.py` | Match W3C image-purpose decision tree → `python scripts/alt_from_ollama.py [--kind informative\|decorative\|functional\|text\|complex\|group] [--lang fr] [--in DOC] [--vocab-from DIR] <src>`. Tag drafts with `data-alt-source="ai"`. |
| "Ollama not installed" / "first-time setup" | `install_alt_ai.py` | `python scripts/install_alt_ai.py` — installs the daemon, pulls `gemma3:4b` (or `gemma3:4b-mlx` on Apple silicon). |

## W3C image-purpose mapping

| Purpose | What it is | What this skill emits |
|---|---|---|
| **informative** | Conveys content (photos, illustrations carrying meaning) | Short literal description biased by surrounding text. |
| **decorative** | Pure ornament, no information value | ``alt=""`` — no model call, instant. |
| **functional** | Image acts as a control or link | Describes the *action or destination*, not the picture. |
| **text** | Image of text | Verbatim transcription of the text only. |
| **complex** | Charts, diagrams, infographics | Short alt + a long-form Markdown description (separate `<figcaption>` or linked `aria-describedby` target). |
| **group** | Multiple images conveying one idea | One unified description across the set. |

When the caller does not pass ``--kind``, the script falls back to
``informative`` — the safest non-zero default for a random ``<img>``.

## Model defaults and MLX selection

The default base model is **``gemma3:4b``** — a 4B-parameter vision
model with the right size / quality tradeoff for local first-pass alt
drafting. On Apple-silicon Macs (Darwin + arm64), the
``-mlx`` suffix is appended automatically (``gemma3:4b-mlx``); both
tags are visible to Ollama as separate, independently pulled tags.

Override paths, in order of precedence:

1. ``--model <tag>`` on the command line.
2. ``OLLAMA_MODEL=<tag>`` env var (full tag, including any ``-mlx``).
3. ``OLLAMA_MODEL_BASE=<base>`` env var (skill appends the ``-mlx``
   suffix on MLX-capable hardware).
4. The built-in default above.

The endpoint defaults to ``http://localhost:11434`` and can be
overridden with ``OLLAMA_URL``.

## Caching

Successful generations are cached under
``~/.cache/front-skill/alt/`` by default. The cache key includes the
image bytes, the image-purpose kind, the output language, any context
hint, and the resolved model tag — so changing any of those produces a
fresh draft. Override the cache root with ``FRONT_CACHE_DIR``; disable
caching for one call with ``--no-cache``.

## Tool composition

When emitting an ``<img>`` whose source path appears in a Markdown or
HTML doc, pass the doc as context:

```bash
python scripts/alt_from_ollama.py --in <that-doc> <image>
```

— the surrounding text becomes both ``--context`` and the vocabulary
seed.

For a UI deliverable end-to-end:

```bash
python front-accessibility/scripts/lint_a11y.py public/                       # static a11y gate
python front-colors/scripts/audit_contrast.py --palette palette.json # WCAG ratios
python front-vision/scripts/alt_from_ollama.py public/hero.jpg       # AI alt text
```

## Changing the language pair

``front-vision`` inherits **bilingual** defaults (EN/FR by default —
configurable via ``lang_pair``). The pair lives in this file's
frontmatter under ``metadata.lang_pair`` as two comma-separated BCP-47
base tags. It controls the default ``--lang`` for ``alt_from_ollama.py``
and is mirrored in ``front-accessibility/SKILL.md``, ``front-ui/SKILL.md``, and
``front-publish/SKILL.md`` so every skill in the family stays in
lock-step. To switch (Berlin → ``en,de``; Tokyo → ``en,ja``; Madrid →
``en,es``), edit the value in every SKILL.md.

**Runtime override.** Set the ``FRONT_LANG_PAIR`` environment variable
to override the pair from the shell — its first comma-split entry
becomes the default ``--lang`` when no flag is passed:

```bash
export FRONT_LANG_PAIR="en,de"
python front-vision/scripts/alt_from_ollama.py photo.jpg   # → German alt text
```

Precedence (highest first): explicit ``--lang`` flag → ``FRONT_LANG_PAIR``
first entry → langdetect on available text → POSIX locale fallback.

## When NOT to use this skill

- You need **top-quality alt text and don't care about local-only / cost**
  → use Claude vision or GPT-4o vision APIs.
- You need **real-time alt** (live captioning of camera feeds) → not the
  shape of this tool; the cache assumes static inputs.
- You need **multi-modal models that also reason about page layout / DOM
  context** → use a hosted multimodal model that accepts HTML + image
  inputs.

## References

- ``references/alt-text-ai.md`` — W3C-compliant alt text via local Ollama
  + Gemma vision (per-purpose decision tree, prompt templates, cache
  semantics).

## Scripts

| Script | Install | Purpose |
|---|---|---|
| ``scripts/alt_from_ollama.py`` | ``pip install -r scripts/requirements-alt-text.txt`` + Ollama | W3C-compliant alt text via local vision model. |
| ``scripts/install_alt_ai.py`` | stdlib only (shells out to brew / winget / official installer) | Installs Ollama + pulls the default vision model (``gemma3:4b`` / ``gemma3:4b-mlx`` on MLX-capable hardware). |
| ``scripts/prompts/*.yaml`` | (data) | Per-purpose prompt templates (short / long × informative / functional / text / complex / group). |
| ``scripts/_argparse.py``, ``scripts/_click.py``, ``scripts/_lang.py``, ``scripts/_prompts.py``, ``scripts/_vocab.py`` | (internal helpers) | Argparse / Click factory, language detection, YAML prompt loader, project-vocab biasing. Duplicated per-skill so each skill stays self-contained. |

## Companion skills

| You also need… | Install |
|---|---|
| Static HTML a11y lint | ``front-accessibility`` |
| WCAG contrast audit, CVD simulation, curated palette | ``front-colors`` |
| Local WebVTT / SRT captions via whisper.cpp | ``front-audio`` |
| WCAG contrast audit, CVD simulation, curated palette | ``front-colors`` |
| Vanilla-JS + Tailwind UI generation | ``front-ui`` |
| Wrap a CLI in a GUI | ``front-cli-gui`` |
| Markdown → website + meta + favicons + indexes | ``front-publish`` |
