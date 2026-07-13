"""
_lang — language / locale resolution for the front-figures scripts.

The resolver follows the precedence documented in every front-* SKILL.md:

    1. explicit ``--lang`` flag on the command line
    2. ``FRONT_LANG_PAIR`` env var (first comma-split entry)
    3. langdetect on the text hint supplied by the caller (when available)
    4. POSIX locale (``LANG`` / ``LC_ALL``)
    5. hard fallback: English (``en``)

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


# BCP-47 base tags this skill knows about. The order determines
# ``lang_pair`` precedence when the user has not overridden it.
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

    pair_env = os.environ.get("FRONT_LANG_PAIR", "").strip()
    if pair_env:
        first, *_ = [t.strip() for t in pair_env.split(",") if t.strip()]
        if first:
            return first.lower()

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
