# Captions / transcripts — `captions_from_whisper.py`

Generate WebVTT captions, SRT subtitles, or plain transcripts from any audio or video file, using a **local** [whisper.cpp](https://github.com/ggerganov/whisper.cpp) build. The default model is **`large-v3-turbo`** — small enough to run on a laptop and accurate enough for production captions.

The script handles both video (caption track for a `<video>`) and audio-only files (transcript for a podcast or interview).

## Why it matters

WCAG SC 1.2.2 (Captions, Prerecorded) is a Level A requirement and is almost universally skipped on small-team and indie sites. The same setup as the rest of the skill's helpers (local-only, no API, no cost per minute) makes shipping captions cheap.

## Install

One command:

```bash
python front/scripts/install_captions.py
```

The installer:

| Step | Behavior |
|---|---|
| Probe for `whisper-cli` on `PATH` | Skips re-install if a binary is present. |
| Install whisper.cpp on macOS | `brew install whisper-cpp`. |
| Install whisper.cpp on Linux | `brew install whisper-cpp` if Homebrew is present; otherwise build from source with `git clone … && make`. |
| Install whisper.cpp on Windows | `winget install ggerganov.whisper.cpp`. |
| Download the model | `ggml-large-v3-turbo.bin` (≈ 1.5 GB) into `~/.cache/front-skill/whisper/`. |

`--model` accepts: `tiny`, `base`, `small`, `medium`, `large-v3`, `large-v3-turbo` (default). Smaller models are faster but noticeably less accurate on accents / overlapping speech.

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

## Integration in the page

For video:

```html
<video controls preload="metadata">
  <source src="/talk.mp4" type="video/mp4">
  <track kind="captions" src="/talk.vtt" srclang="en" label="English" default>
</video>
```

For audio:

```html
<audio controls preload="metadata">
  <source src="/podcast.mp3" type="audio/mpeg">
</audio>
<details>
  <summary>Transcript</summary>
  <article id="transcript">…paste transcript here…</article>
</details>
```

`meta-tags.md` covers the social-preview tags that pair with these surfaces.

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| `whisper.cpp binary not found on PATH` | Installer skipped or `PATH` not refreshed | Run `install_captions.py`; open a new shell. |
| `Model file … not found` | Installer didn't run, or wrong alias | Run `install_captions.py --model <alias>`. |
| `Neither audio-helper / video-helper nor ffmpeg is available` | No extractor on the host | `brew install ffmpeg` or install the helper packages. |
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
