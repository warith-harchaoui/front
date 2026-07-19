"""
_lang — language / locale resolution for the front-figures scripts.

The resolver follows the precedence documented in every front-* SKILL.md.
There is no configured default language — the output language is always
detected from the text:

    1. explicit ``--lang`` flag on the command line
    2. langdetect on the text hint supplied by the caller (when available)
    3. POSIX locale (``LANG`` / ``LC_ALL``)
    4. hard floor: English (``en``)

Duplicated (intentionally) across every front-* skill so each stays
self-contained. Keep this file in sync with the copies elsewhere.

Author
------
`Warith Harchaoui, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import locale
import os
from typing import Optional


# BCP-47 base tags this skill knows about. The first is the ``en`` floor
# returned only when the language cannot be detected from any text.
DEFAULT_PAIR = ("en", "fr")


def resolve_lang(
    explicit: Optional[str] = None,
    text_hint: Optional[str] = None,
) -> str:
    """Return the effective language tag for downstream renderers.

    Parameters
    ----------
    explicit : str or None
        The ``--lang`` flag from the command line, if the caller passed
        one. Wins over everything else.
    text_hint : str or None
        A short piece of text (chart title, axis label) the resolver
        can feed to ``langdetect`` when the caller has installed it.
        Missing dependency degrades gracefully — the resolver does not
        require ``langdetect`` at runtime.

    Returns
    -------
    str
        A BCP-47 base tag: ``"en"`` / ``"fr"`` / ``"de"`` / …
    """
    if explicit:
        return explicit.strip().lower()

    # No configured default language: detect from the text hint (chart
    # title / axis label) via langdetect, else fall through to the locale.
    if text_hint:
        try:
            from langdetect import detect  # type: ignore
            return detect(text_hint).lower()
        except Exception:
            pass

    for env_var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        raw = os.environ.get(env_var, "").strip()
        if raw and raw != "C":
            parsed, _ = locale.getlocale()
            if parsed:
                return parsed.split("_")[0].lower()
            return raw.split(".")[0].split("_")[0].lower()

    return DEFAULT_PAIR[0]
