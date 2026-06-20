# Audio fixtures for `tests/eval/test_captions_eval.py`

Caption-quality evaluation needs real human speech. The repository does
not ship audio assets — they are too bulky for git and we cannot
synthesize realistic speech for free. Drop two files in this directory
to enable the full eval suite:

| Filename | Source idea | What the test asserts |
| --- | --- | --- |
| `en-clean-30s.wav` | 30 s of clean English speech from [Mozilla Common Voice](https://commonvoice.mozilla.org/) or a public-domain podcast. | WER ≤ 0.10 against `en-clean-30s.txt` (place the ground-truth transcript alongside, one sentence per line). |
| `fr-clean-30s.wav` | 30 s of clean French speech, same sources. | Output detected as French via `_lang.detect_text_language`. |

Recommended format: 16 kHz mono PCM, 16-bit. Anything `ffmpeg` can
decode also works since `captions_from_whisper.extract_audio` re-encodes
to that target.

When the files are missing the eval tests `pytest.skip()` with a
message that points back at this README. They do **not** fail.

## Ground-truth transcript files

Save the canonical transcript next to each WAV with the same basename
and a `.txt` extension. For example:

```
en-clean-30s.wav
en-clean-30s.txt
```

The test reads the `.txt` file verbatim, lower-cases both sides, and
computes Word Error Rate via `jiwer`.

## Glossary biasing fixture

The vocab-biasing assertion uses `tests/fixtures/vocab/glossary.txt`.
Record (or pick a clip with) at least one of those terms uttered
clearly — `pywhispercpp`, `VisionCell`, or `Acme Robotics` work well.
Save the clip as `vocab-biasing-clip.wav` here; the test reads its
basename to know which glossary word should appear verbatim.
