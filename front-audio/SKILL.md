---
name: front-audio
description: >-
  Local-AI captions and transcripts for video / audio. Generates W3C-compliant
  WebVTT, SRT or plain-text captions from a local `whisper.cpp` build (via
  ``pywhispercpp``) with project-vocabulary biasing so domain spellings are
  not hallucinated. Bilingual output (EN/FR default, configurable via
  ``lang_pair``). Deterministic, runs offline once installed, never sends
  audio to a SaaS. For solo developers and small teams who want accessibility
  captions drafted locally without a hosted transcription bill or data
  exfiltration. **WiP**: per-language WER baselines (EN / FR / ES extractor
  wired) and a vocab-biasing reference clip are still being collected.
  Trigger phrases: "captions", "transcribe video", "transcribe audio",
  "WebVTT", "SRT", "subtitle file", "VTT", "caption track". Output is a
  captions file on disk + a ready-to-paste `<video>` / `<audio>` snippet on
  stdout. Roadmap: improve the whisper.cpp integration via `pdbms`.
license: Unlicense
compatibility: >-
  Runtime: Claude.ai, Claude Code, OpenCode. Needs Python 3.9+ stdlib +
  ``pywhispercpp`` (see ``scripts/requirements-captions.txt``) + a local
  ``whisper.cpp`` build, plus ``ffmpeg`` on PATH for non-WAV inputs. The
  ``install_captions.py`` script installs ``pywhispercpp`` and pre-downloads
  a GGML model on first run. Network access not required at caption time
  after the install completes.
metadata:
  author: Warith Harchaoui
  version: 0.1.0
  lang_pair: "en,fr"  # override per-project; e.g. "en,de" or "en,ja"
---

# front-audio — local AI captions and transcripts

## Audience and positioning

Solo developers and small teams who:

- Need **WebVTT / SRT captions** on every `<video>` and `<audio>` they
  ship, drafted at commit time rather than via a hosted service.
- Want **local-first AI** — no SaaS bill, no audio exfiltration, no
  per-minute pricing. Apple-silicon Macs get Metal acceleration via
  ``whisper.cpp`` automatically.
- Want **vocabulary biasing** so the model knows the project's
  technical terms / product names / people's names before it
  hallucinates a near-miss spelling.
- Want a **bilingual** default (EN/FR; pair configurable via
  ``lang_pair``) without spelling out the language flag every time.

This skill is **not** a substitute for a human review pass. Each draft
should be read and corrected — automatic captions miss proper nouns,
mishear similar words, and drop punctuation. For real-time captions
(live streams, video calls), use **Deepgram** or **AssemblyAI** — this
skill is for static media that gets committed to a repo.

## Status — WiP

The script and tests ship today; what is still being collected:

- Per-language **WER baselines** for EN / FR / ES (the extractor that
  builds them is wired; the baselines themselves are pending). Without
  baselines, you can't know whether a given run's quality is in the
  expected band.
- A user-supplied **``vocab-biasing-clip.wav``** that exercises the
  prompt-biasing path end-to-end. The current tests check the
  prompt-string construction; an audio fixture would let us regress
  on the actual transcription behaviour.

A future revision will integrate **``pdbms``** (per the maintainer) to
improve the whisper.cpp integration. Track shape via
``tests/fixtures/audio/README.md``.

## Honest framing of what the tool covers

| Tool | Catches | Misses |
|---|---|---|
| `scripts/captions_from_whisper.py` | WebVTT / SRT / plain-text captions from a local whisper.cpp build; project-vocab biasing via ``--prompt`` / ``--vocab`` / ``--vocab-from`` / ``--auto-project``; language auto-detection with explicit override; cache on the audio hash | not real-time (hosted services like Deepgram / AssemblyAI are better for live captions); model-quality drafts — proper nouns, similar-sounding words and quiet passages need a review pass. |
| `scripts/install_captions.py` | Installs ``pywhispercpp`` into the active Python env and pre-downloads a GGML model so the captioner runs offline. Idempotent — safe to re-run. | does not install ``ffmpeg`` for you; does not auto-update an already-installed model; does not pin GPU / Metal acceleration. |

## Decision tree

| Trigger | Tool | Run |
|---|---|---|
| "captions" / "transcribe video" / "transcribe audio" / "subtitle file" | `captions_from_whisper.py` | `python scripts/install_captions.py` then `python scripts/captions_from_whisper.py <audio-or-video> [--format vtt\|srt\|text] [--lang fr] [--vocab-from DIR] [--auto-project]`. Always emit `<track kind="captions">` on `<video>` / `<audio>`. |
| "Whisper not installed" / "first-time setup" | `install_captions.py` | `python scripts/install_captions.py` — pip-installs ``pywhispercpp`` and pre-downloads a GGML model so the captioner runs offline. |

## Output contract

For ``--format vtt`` (the default), the script writes a sibling
``<stem>.vtt`` next to the source media and prints a ready-to-paste
HTML snippet on stdout:

```html
<video src="podcast.mp4" controls>
  <track kind="captions" srclang="en" src="podcast.vtt" default>
</video>
```

For ``--format srt`` the file is ``<stem>.srt`` with the same snippet
shape (substitute ``.srt`` for ``.vtt``). For ``--format text`` the
file is ``<stem>.txt`` with one line per detected utterance — the
``<track>`` snippet is skipped.

## Vocabulary biasing

The captioner accepts a prompt-bias string ahead of decoding. Four
ways to supply it, in order of precedence:

1. ``--prompt "<text>"`` — literal prompt prefix.
2. ``--vocab "<term1>,<term2>,..."`` — comma-separated terms.
3. ``--vocab-from <DIR>`` — read every ``.txt`` / ``.md`` under
   ``<DIR>`` and use the surrounding text + extracted terms as bias.
4. ``--auto-project`` — walk the project root (current working
   directory), pull terms from ``package.json``, ``pyproject.toml``,
   ``README.md`` and any glossary / vocab file under
   ``docs/`` / ``content/``.

Biasing helps domain spellings (product names, people, technical
terms) survive transcription. It does not improve general accuracy —
for that, switch model.

## Models

The installer pulls a small GGML model by default (``ggml-base.en``
for English-leaning sets, ``ggml-medium`` when ``lang_pair`` is bigger
than EN). Override paths:

1. ``--model <path>`` on the command line (full path to a ``.bin``).
2. ``WHISPER_MODEL_PATH=<path>`` env var.
3. The pre-downloaded model from ``install_captions.py``.

Larger models (``ggml-large-v3``) give noticeably better WER on noisy
audio at ~1.5 GB on disk and ~3× the CPU time. Pull manually via
``install_captions.py --model large-v3`` when the smaller default is
under-serving you.

## Tool composition

When emitting ``<video>`` or ``<audio>`` in a deliverable:

```bash
python front-audio/scripts/captions_from_whisper.py --auto-project <media>
```

— always emit ``<track kind="captions" srclang="…" default>`` on the
element. Add ``<track kind="subtitles">`` for translations,
``<track kind="descriptions">`` for audio descriptions,
``<track kind="chapters">`` for navigation when chapters exist.

## Changing the language pair

``front-audio`` inherits **bilingual** defaults (EN/FR by default —
configurable via ``lang_pair``). The pair lives in this file's
frontmatter under ``metadata.lang_pair`` as two comma-separated BCP-47
base tags. It controls the default ``--lang`` for
``captions_from_whisper.py`` and is mirrored in
``front-accessibility/SKILL.md``, ``front-vision/SKILL.md``,
``front-ui/SKILL.md`` and ``front-publish/SKILL.md`` so every skill in
the family stays in lock-step. To switch (Berlin → ``en,de``;
Tokyo → ``en,ja``; Madrid → ``en,es``), edit the value in every
SKILL.md.

**Runtime override.** Set the ``FRONT_LANG_PAIR`` environment variable
to override the pair from the shell — its first comma-split entry
becomes the default ``--lang`` when no flag is passed:

```bash
export FRONT_LANG_PAIR="en,de"
python front-audio/scripts/captions_from_whisper.py podcast.mp3   # → German captions
```

Precedence (highest first): explicit ``--lang`` flag → ``FRONT_LANG_PAIR``
first entry → langdetect on available text → POSIX locale fallback.

## When NOT to use this skill

- You need **real-time captions** (live streams, video calls) → use
  **Deepgram** or **AssemblyAI**; the cache and disk-bound shape of
  this skill assume static input.
- You need **top-quality accuracy and don't care about local-only /
  cost** → hosted services (Deepgram, AssemblyAI, Whisper.com) are
  noticeably better on noisy or accented audio.
- You need **translations**, not transcriptions → run a translator
  over the produced ``.vtt`` afterward; this skill writes captions in
  the language detected (or specified) only.

## References

- ``references/captions-ai.md`` — Local pywhispercpp captions /
  transcripts for video and audio, with vocabulary biasing.

## Scripts

| Script | Install | Purpose |
|---|---|---|
| ``scripts/captions_from_whisper.py`` *(WiP)* | ``pip install -r scripts/requirements-captions.txt`` + ``ffmpeg`` on PATH | WebVTT / SRT / plain-text captions via local whisper.cpp. Per-language WER baselines + vocab-biasing reference clip still being collected. |
| ``scripts/install_captions.py`` | subprocess (uses the active Python's ``pip``) | Installs ``pywhispercpp`` and pre-downloads a GGML caption model. |
| ``scripts/_argparse.py``, ``scripts/_click.py``, ``scripts/_lang.py``, ``scripts/_vocab.py`` | (internal helpers) | Argparse / Click factory, language detection, project-vocab biasing. Duplicated per-skill so each skill stays self-contained. |

## Companion skills

| You also need… | Install |
|---|---|
| Static HTML a11y lint | ``front-accessibility`` |
| W3C alt text via local Ollama vision | ``front-vision`` |
| WCAG contrast audit, CVD simulation, curated palette | ``front-colors`` |
| Vanilla-JS + Tailwind UI generation | ``front-ui`` |
| Wrap a CLI in a GUI | ``front-cli-gui`` |
| Markdown → website + meta + favicons + indexes | ``front-publish`` |
