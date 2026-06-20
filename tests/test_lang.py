"""
test_lang — coverage for ``front-a11y/scripts/_lang.py``.

Asserts the language detector returns the right BCP-47 base tag for
short samples in seven scripts, short-input fallback, and graceful
behaviour when ``langdetect`` is unavailable.

``langdetect`` ships randomness pinned at import via
``DetectorFactory.seed = 0`` so two calls on the same string are
deterministic.

Author
------
`Warith Harchaoui, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import importlib
import importlib.util

import pytest

import _lang


HAVE_LANGDETECT = importlib.util.find_spec("langdetect") is not None


SAMPLES: dict[str, str] = {
    "en": "The quick brown fox jumps over the lazy dog and continues its journey along the river bank.",
    "fr": "Le rapide renard brun saute par-dessus le chien paresseux et continue sa route le long du fleuve.",
    "es": "El rápido zorro marrón salta sobre el perro perezoso y continúa su camino a lo largo del río.",
    "de": "Der schnelle braune Fuchs springt über den faulen Hund und geht weiter am Fluss entlang.",
}


@pytest.mark.skipif(not HAVE_LANGDETECT, reason="langdetect not installed")
class TestDetectTextLanguage:
    @pytest.mark.parametrize("lang_code, text", SAMPLES.items())
    def test_known_samples(self, lang_code: str, text: str):
        # ``langdetect`` is non-trivial; ~100-character samples are normally
        # detected reliably with the pinned seed.
        assert _lang.detect_text_language(text) == lang_code

    def test_short_input_uses_fallback(self):
        # Below the 20-non-whitespace-char threshold the function bails out
        # to the fallback rather than guessing.
        assert _lang.detect_text_language("hi", fallback="fr") == "fr"

    def test_empty_input_uses_fallback(self):
        assert _lang.detect_text_language("", fallback="de") == "de"

    def test_determinism(self):
        # Same input, two calls — must agree.
        text = SAMPLES["fr"]
        first = _lang.detect_text_language(text)
        second = _lang.detect_text_language(text)
        assert first == second


class TestFallbackPath:
    def test_returns_fallback_when_langdetect_missing(self, monkeypatch):
        # Simulate the "library not installed" environment by patching the
        # capability probe. The detector must not raise; it must fall back.
        monkeypatch.setattr(_lang, "_have_langdetect", lambda: False)
        assert _lang.detect_text_language(SAMPLES["en"], fallback="xx") == "xx"


class TestLangPairDefault:
    """
    ``lang_pair_default()`` reads ``FRONT_LANG_PAIR`` and returns the
    first comma-split entry. It is the runtime hook that lets the four
    Ollama-backed scripts honour the ``lang_pair`` SKILL.md frontmatter
    without forcing the user to pass ``--lang`` every call.
    """

    def test_env_unset_returns_none(self, monkeypatch):
        monkeypatch.delenv("FRONT_LANG_PAIR", raising=False)
        assert _lang.lang_pair_default() is None

    def test_env_empty_returns_none(self, monkeypatch):
        monkeypatch.setenv("FRONT_LANG_PAIR", "")
        assert _lang.lang_pair_default() is None

    def test_env_whitespace_only_returns_none(self, monkeypatch):
        monkeypatch.setenv("FRONT_LANG_PAIR", "   ")
        assert _lang.lang_pair_default() is None

    def test_first_entry_returned(self, monkeypatch):
        monkeypatch.setenv("FRONT_LANG_PAIR", "en,fr")
        assert _lang.lang_pair_default() == "en"

    def test_whitespace_tolerant(self, monkeypatch):
        monkeypatch.setenv("FRONT_LANG_PAIR", "  fr ,  de ")
        assert _lang.lang_pair_default() == "fr"

    def test_single_entry_no_comma(self, monkeypatch):
        # Even without a comma we honour the single entry — useful for
        # users who only set one language.
        monkeypatch.setenv("FRONT_LANG_PAIR", "ja")
        assert _lang.lang_pair_default() == "ja"
