"""
test_captions_eval — opt-in checks for ``captions_from_whisper``.

The deterministic suite mocks ``pywhispercpp.model.Model``. This module
actually runs the local whisper.cpp build against real audio fixtures
and asserts on transcription quality. Run with::

    pytest -m eval

Skips cleanly when:

- ``pywhispercpp`` is not installed.
- The audio fixtures aren't dropped in (see
  ``tests/fixtures/audio/README.md``).
- ``jiwer`` is not installed (for the WER assertion only — the
  structural-validity test runs without it).

Assertions, per ``.private/tests.md``:

- **WER ≤ 0.10** on clean English speech (``large-v3-turbo``).
- **WebVTT structurally valid**: first non-empty line is ``WEBVTT`` and
  every timestamp line parses to two ``HH:MM:SS.mmm`` values.
- **Multilingual**: French audio yields French output via
  ``_lang.detect_text_language``.
- **Glossary biasing**: words listed in ``tests/fixtures/vocab/glossary.txt``
  appear verbatim in the output when the audio actually contains them.

The audio fixture itself is *not* shipped in git — see the README in
``tests/fixtures/audio/``. Tests skip with an informative message
when a particular WAV is missing.

Author
------
`Warith Harchaoui, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# pywhispercpp is the heavy native dep — gate the whole module on it.
pytest.importorskip("pywhispercpp")

import captions_from_whisper  # noqa: E402 — via tests/conftest.py sys.path
from _lang import detect_text_language  # noqa: E402

pytestmark = pytest.mark.eval


# ── Helpers ─────────────────────────────────────────────────────────────────

# WebVTT timestamps: HH:MM:SS.mmm --> HH:MM:SS.mmm (or M:SS.mmm in loose VTT).
_VTT_CUE_RE = re.compile(
    r"^\s*(\d{1,2}:)?\d{1,2}:\d{2}\.\d{3}\s*-->\s*(\d{1,2}:)?\d{1,2}:\d{2}\.\d{3}",
)


def _read_truth(audio_path: Path) -> str:
    """
    Read the canonical transcript that lives alongside a WAV fixture.

    Convention from ``tests/fixtures/audio/README.md``: a ``.txt`` file
    with the same basename, one sentence per line.
    """
    txt = audio_path.with_suffix(".txt")
    if not txt.exists():
        pytest.skip(
            f"Ground-truth transcript missing for {audio_path.name}. "
            f"Create {txt.name} alongside it (one sentence per line). "
            f"See tests/fixtures/audio/README.md."
        )
    return txt.read_text(encoding="utf-8")


def _normalise_for_wer(s: str) -> str:
    """Lower-case, strip punctuation, collapse whitespace — same as ``jiwer``'s default."""
    s = s.lower()
    s = re.sub(r"[^a-z0-9' ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ── Tests ───────────────────────────────────────────────────────────────────

def test_english_wer_under_threshold(audio_fixture, eval_repo_root) -> None:
    """
    Transcribe the clean-English fixture and assert WER ≤ 0.10.

    Uses ``jiwer`` for the WER calculation; skips when the library
    isn't installed (it's an optional dev dep for this assertion).
    """
    jiwer = pytest.importorskip("jiwer")

    wav = audio_fixture("en-clean-30s")
    truth = _read_truth(wav)

    vtt: str = captions_from_whisper.transcribe(
        wav, model="large-v3-turbo", lang="en", fmt="text"
    )
    hypothesis: str = _normalise_for_wer(vtt)
    reference: str = _normalise_for_wer(truth)
    wer = jiwer.wer(reference, hypothesis)
    assert wer <= 0.10, f"WER {wer:.3f} exceeds 0.10 threshold.\nref={reference}\nhyp={hypothesis}"


def test_vtt_structurally_valid(audio_fixture) -> None:
    """
    The VTT output must start with ``WEBVTT`` and every cue header must
    parse as two HH:MM:SS.mmm timestamps. This test runs without
    ``jiwer`` — it is the cheapest signal that the pipeline produced a
    real output rather than a partial / corrupted file.
    """
    wav = audio_fixture("en-clean-30s")
    vtt: str = captions_from_whisper.transcribe(
        wav, model="large-v3-turbo", lang="en", fmt="vtt"
    )
    lines = vtt.splitlines()
    assert lines, "VTT output is empty"
    # WEBVTT must be the first non-empty line.
    first_non_empty = next((ln for ln in lines if ln.strip()), "")
    assert first_non_empty.strip() == "WEBVTT", (
        f"First non-empty line must be 'WEBVTT', got {first_non_empty!r}"
    )
    # At least one cue header present, and every cue header parses.
    cue_lines = [ln for ln in lines if "-->" in ln]
    assert cue_lines, "VTT output has no cue lines"
    for ln in cue_lines:
        assert _VTT_CUE_RE.match(ln), f"Cue line does not parse: {ln!r}"


def test_french_audio_yields_french_text(audio_fixture) -> None:
    """A French audio fixture should produce French text per ``detect_text_language``."""
    wav = audio_fixture("fr-clean-30s")
    text: str = captions_from_whisper.transcribe(
        wav, model="large-v3-turbo", lang="fr", fmt="text"
    )
    assert text.strip(), "French transcription is empty"
    detected = detect_text_language(text, fallback="en")
    assert detected == "fr", (
        f"Expected French output but detector returned {detected!r}. "
        f"First 200 chars: {text[:200]!r}"
    )


def test_vocab_glossary_words_appear(audio_fixture, fixtures_dir) -> None:
    """
    A clip that pronounces a glossary term should yield that term
    verbatim in the output when the term is passed via ``--vocab``.

    The recording is named ``vocab-biasing-clip.wav`` and must contain
    at least one of the glossary terms listed in
    ``tests/fixtures/vocab/glossary.txt``. The test reads the
    co-located ``.txt`` ground-truth to know which term to look for.
    """
    wav = audio_fixture("vocab-biasing-clip")
    truth = _read_truth(wav).lower()

    glossary_path: Path = fixtures_dir / "vocab" / "glossary.txt"
    terms: list[str] = [
        ln.strip()
        for ln in glossary_path.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    expected = [t for t in terms if t.lower() in truth]
    if not expected:
        pytest.skip(
            "vocab-biasing-clip.wav ground-truth contains none of the glossary terms — "
            "nothing to assert on. Re-record with a glossary term spoken aloud."
        )

    prompt: str = captions_from_whisper.compose_prompt(terms, "en")
    text: str = captions_from_whisper.transcribe(
        wav,
        model="large-v3-turbo",
        lang="en",
        fmt="text",
        initial_prompt=prompt,
    )
    text_lower = text.lower()
    assert any(t.lower() in text_lower for t in expected), (
        f"None of the expected glossary terms {expected} appear in the transcription.\n"
        f"Output: {text!r}"
    )
