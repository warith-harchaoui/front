"""
_lang
=====

Tiny language-detection helper shared across the Ollama-backed scripts.

Wraps `langdetect`_ — the Python port of Google's language-detection
library — with a graceful fallback for environments where it is not
installed.

The library is opt-in. ``langdetect`` lives under each Ollama tool's
own ``requirements-*.txt`` file (alt text, meta tags, plain language,
captions) so the lightweight scripts that need no third-party deps
(``validate.py``, ``lint_a11y.py``, ``audit_contrast.py``,
``site_indexes.py``) install nothing extra.

Determinism note: ``langdetect`` seeds its random source from the input
string by default, but its public ``DetectorFactory`` exposes a manual
seed. We pin the seed once at import so two calls with the same text
always return the same language tag.

.. _langdetect: https://github.com/Mimino666/langdetect

Author
------
`Warith Harchaoui, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import importlib.util
import os


def lang_pair_default() -> str | None:
    """
    Return the first entry of the ``FRONT_LANG_PAIR`` env var, or ``None``.

    The env var holds a comma-separated language pair like ``"en,fr"``
    (matching the ``lang_pair`` field in each SKILL.md frontmatter). When
    set, the first entry is the preferred default language for any script
    that accepts ``--lang`` and was not given one on the command line.

    Whitespace around each comma-split entry is tolerated; an empty or
    whitespace-only entry yields ``None`` so the caller falls back to the
    next layer (langdetect, then env-derived locale).

    Examples
    --------
    >>> import os
    >>> os.environ.pop("FRONT_LANG_PAIR", None)
    >>> lang_pair_default() is None
    True
    >>> os.environ["FRONT_LANG_PAIR"] = "en,fr"
    >>> lang_pair_default()
    'en'
    >>> os.environ["FRONT_LANG_PAIR"] = "  fr ,  de "
    >>> lang_pair_default()
    'fr'
    >>> os.environ["FRONT_LANG_PAIR"] = ""
    >>> lang_pair_default() is None
    True
    >>> del os.environ["FRONT_LANG_PAIR"]
    """
    raw = os.environ.get("FRONT_LANG_PAIR", "")
    if not raw.strip():
        return None
    first = raw.split(",", 1)[0].strip()
    return first or None


def _have_langdetect() -> bool:
    """Return ``True`` when ``langdetect`` is importable."""
    return importlib.util.find_spec("langdetect") is not None


# Pin the seed once so output is reproducible. The import is guarded so
# this module stays importable on lightweight installs.
if _have_langdetect():
    from langdetect import DetectorFactory  # type: ignore[import-not-found]
    DetectorFactory.seed = 0


def detect_text_language(text: str, fallback: str = "en") -> str:
    """
    Detect the language of ``text`` as a two-letter BCP-47 base tag.

    Strategy:

    1. If ``langdetect`` is installed and the text has enough signal
       (≥ 20 non-whitespace characters), use it.
    2. Otherwise, return ``fallback``.

    Parameters
    ----------
    text : str
        Source text. Empty / whitespace-only input falls back immediately.
    fallback : str, optional
        Two-letter code returned when detection is not possible. Default
        ``"en"``.

    Returns
    -------
    str
        Lower-case two-letter language code.
    """
    if not _have_langdetect():
        return fallback
    stripped: str = "".join(text.split())
    if len(stripped) < 20:
        # Below the threshold langdetect's output is essentially random;
        # the fallback is more reliable.
        return fallback
    try:
        # ``langdetect.detect`` returns BCP-47 tags like "en", "fr",
        # "zh-cn"; we keep only the base subtag.
        from langdetect import detect  # type: ignore[import-not-found]
        from langdetect.lang_detect_exception import LangDetectException  # type: ignore[import-not-found]
        return detect(text).split("-")[0].lower()[:2]
    except LangDetectException:
        return fallback
