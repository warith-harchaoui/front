# Captions / transcripts — `captions_from_whisper.py`

Generate WebVTT captions, SRT subtitles, or plain transcripts from any audio or video file using **[pywhispercpp](https://github.com/absadiki/pywhispercpp)** — the Python binding for whisper.cpp. The default model is **`large-v3-turbo`** — small enough to run on a laptop and accurate enough for production captions.

The script handles both video (caption track for a `<video>`) and audio-only files (transcript for a podcast or interview).

## Why it matters

WCAG SC 1.2.2 (Captions, Prerecorded) is a Level A requirement and is almost universally skipped on small-team and indie sites. The same setup as the rest of the skill's helpers (local-only, no API, no cost per minute) makes shipping captions cheap.

## Install

Single command — `pip install` plus a pre-download of the GGML weights:

```bash
pip install -r front/scripts/requirements.txt
python front/scripts/install_captions.py
```

The installer:

| Step | Behavior |
|---|---|
| Probe `import pywhispercpp` | Skips re-install if already importable. |
| Install via pip | `pip install --upgrade pywhispercpp` in the active interpreter. Pre-compiled wheels exist for macOS / Linux / Windows. |
| Pre-download the GGML model | Via `pywhispercpp.utils.download_model` into `~/.cache/front-skill/whisper/`. |

`--model` accepts every pywhispercpp alias: `tiny[.en]`, `base[.en]`, `small[.en]`, `medium[.en]`, `large-v1`, `large-v2`, `large-v3`, `large-v3-turbo` (default). Smaller models are faster but noticeably less accurate on accents / overlapping speech.

## Generate

```bash
# Captions for a video → input.vtt next to the file
python front/scripts/captions_from_whisper.py talk.mp4

# Plain transcript for an audio-only file
python front/scripts/captions_from_whisper.py podcast.mp3 --format text

# Specific language + SRT
python front/scripts/captions_from_whisper.py interview.wav --lang fr --format srt

# Smaller model for a quick draft
python front/scripts/captions_from_whisper.py call.m4a --model small
```

`--out PATH` overrides the default sibling-file destination. `--no-cache` bypasses the on-disk cache for a single run.

## Audio extraction

whisper.cpp needs 16 kHz mono WAV. The script tries, in order:

1. **`video-helper`** (<https://github.com/warith-harchaoui/video-helper>) for video sources.
2. **`audio-helper`** (<https://github.com/warith-harchaoui/audio-helper>) for audio sources.
3. **`ffmpeg`** subprocess as a fallback.

Install the helpers if you want a Python-native extraction path:

```bash
pip install git+https://github.com/warith-harchaoui/audio-helper
pip install git+https://github.com/warith-harchaoui/video-helper
```

If neither helper nor `ffmpeg` is available, the script exits with a list of install hints.

## Cache

Same shape as the alt-text and meta helpers:

- Location: `~/.cache/front-skill/captions/`.
- Key: SHA-256 of the extracted-audio bytes + model + lang + format, truncated to 32 hex characters.
- Bypass: `--no-cache` for one run, `FRONT_NO_CACHE=1` globally.
- Clear: delete the directory.

The cache stores the final WebVTT / SRT / text body — re-runs of the same input are near-instant.

## Vocabulary biasing

Whisper's accuracy on proper nouns and jargon drops sharply without domain context. The script accepts four shapes; the first non-empty source wins:

| Flag | Meaning |
|---|---|
| `--prompt "<text>"` | Verbatim `initial_prompt` for whisper.cpp. Highest precedence. |
| `--vocab path/to/glossary.txt` | Glossary file, one term per line, `#` starts a comment. |
| `--vocab-from path` | File OR directory. Directory → walked as a project root (top-level README / SKILL.md / manifests + `.md` files under `docs/`, `references/`, `src/`, …). |
| `--auto-project` | Walk upward from the source to discover the project root, then mine the whole tree. |

Beyond those flags, the resolver looks for a **sibling subtitle file** (`<stem>.vtt` / `.srt` / `.txt`) — for re-captioning runs, the prior transcript is the strongest signal — then a sibling README / `index.html`. Pass nothing, and the right thing usually happens.

The composed `initial_prompt` is in natural prose, not a comma list — Whisper was trained on continuous text, so `"The following terms may appear in the audio: Tailwind, Montserrat, OKLCH."` outperforms `"Tailwind, Montserrat, OKLCH"`. The opener is selected from a per-language template.

## Integration in the page

For `<video>`, ALWAYS emit `<track kind="captions">`. Add the other kinds when they apply.

```html
<video controls preload="metadata">
  <source src="/talk.mp4" type="video/mp4">

  <!-- Speech + sound effects in the source language. Required. -->
  <track kind="captions" src="/talk.vtt" srclang="en" label="English" default>

  <!-- Translation of dialogue. -->
  <track kind="subtitles" src="/talk.fr.vtt" srclang="fr" label="Français">

  <!-- Narration of visuals for blind users.
       Out of scope for whisper — separate workflow. -->
  <track kind="descriptions" src="/talk.descriptions.vtt" srclang="en" label="Audio descriptions">

  <!-- Navigation markers. Emit when the source has chapters. -->
  <track kind="chapters" src="/talk.chapters.vtt" srclang="en" label="Chapters">
</video>
```

For `<audio>`, captions don't render in the player — pair the file with an expandable transcript:

```html
<audio controls preload="metadata">
  <source src="/podcast.mp3" type="audio/mpeg">
</audio>
<details>
  <summary>Transcript</summary>
  <article id="transcript">…paste transcript here…</article>
</details>
```

The four `<track>` kinds:

| `kind` | Use | Source |
|---|---|---|
| `captions` | Speech + sound effects | `captions_from_whisper.py` (this script) |
| `subtitles` | Dialogue translation | Pass `--lang <target>` and a target-language vocabulary, or run a second pass per target language. Future flag `--task translate` will route through whisper.cpp's built-in English-translation mode. |
| `descriptions` | Visual narration for blind users | Out of scope for an audio model — frame extraction + Gemma vision. Documented as a future helper. |
| `chapters` | Navigation markers | Heuristic on long segment pauses; documented as a future helper. |

`meta-tags.md` covers the social-preview tags that pair with these surfaces.

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| `pywhispercpp not installed` | pip install skipped | `python front/scripts/install_captions.py`. |
| `Model … not found` on first transcribe | Pre-download skipped; pywhispercpp falls back to its own download but may fail offline | Run `install_captions.py --model <alias>` to pre-fetch, or set `FRONT_WHISPER_MODEL=/path/to/ggml-model.bin`. |
| `Neither audio-helper / video-helper nor ffmpeg is available` | No extractor on the host | Install one of the helper packages or `ffmpeg`. |
| Output is empty | Source has no audio track | Re-check the source; for video, confirm `ffprobe` finds an audio stream. |
| Bad accents or hallucinated text | Model too small for difficult audio | Use `large-v3-turbo` (default) or `large-v3`. |
| French in, English out | Language auto-detection misfired | Pass `--lang fr` explicitly. |

## Standards

- WCAG SC 1.2.2 — Captions (Prerecorded), Level A.
- WCAG SC 1.2.5 — Audio Description (Prerecorded), Level AA. (Captions alone do not satisfy this; audio descriptions need a separate workflow.)
- whisper.cpp licensing: MIT. Bundled GGML model files keep their original licenses (also MIT for the official OpenAI releases).

## Checklist

- [ ] Captions exist for every prerecorded video.
- [ ] Transcript exists for every prerecorded audio.
- [ ] `<track kind="captions" srclang="…" label="…">` matches the language.
- [ ] `--lang` set explicitly when the source's language is known.
- [ ] Reviewer pass before publishing — whisper makes occasional substitutions that the cache happily reuses.
