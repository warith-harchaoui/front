"""
_style — house-style tokens shared by every make/audit script.

Exposes the single source of truth for palette, typography, and Vega
/ matplotlib configuration. When ``front-colors`` is co-installed
next to ``front-figures``, the palette is read from
``front-colors/references/palette.csv`` to keep make ↔ audit brand
tokens from drifting; otherwise the module's built-in curated
fallback (the same 8 saturated Apple-system hues) is used.

The module is **stdlib-only** — no numpy, no matplotlib, no pandas
at import time — so ``audit_figure.py`` can pull tokens without
installing the dataviz tier.

Author
------
`Warith Harchaoui, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


# ------------------------------------------------------------------
# Built-in curated fallback — the Apple-inspired 8 + 4 neutrals.
# The canonical source is front-colors/references/palette.csv, which
# projects each hex onto four semantic axes: **Emotion**, **Concepts**,
# **PsychologyPositive**, **PsychologyNegative**. The full mapping is
# documented at <https://harchaoui.org/warith/colors/>. When the CSV is
# available, :func:`load_semantic_palette` reads it. This fallback is
# used only when neither ``front-colors`` nor ``FRONT_COLORS_PALETTE``
# can be resolved.
# ------------------------------------------------------------------
_FALLBACK_PALETTE: Dict[str, str] = {
    # 8 saturated hues.
    "Red":    "#FF3B30",
    "Orange": "#FF9500",
    "Yellow": "#FFCC00",
    "Green":  "#34C759",
    "Mint":   "#00C7BE",
    "Teal":   "#5AC8FA",
    "Blue":   "#007AFF",
    "Purple": "#AF52DE",
    # 4 neutrals.
    "Gray":   "#8E8E93",
    "Brown":  "#A2845E",
    "Black":  "#000000",
    "White":  "#FFFFFF",
}


#: Emotion → hex fallback, mirroring the ``Emotion`` column of the
#: front-colors CSV. Anger / Sadness / Joy etc. Source:
#: <https://harchaoui.org/warith/colors/>.
_FALLBACK_EMOTIONS: Dict[str, str] = {
    "Anger":     "#FF3B30",
    "Surprise":  "#FF9500",
    "Joy":       "#FFCC00",
    "Disgust":   "#34C759",
    "Happiness": "#00C7BE",
    "Sadness":   "#007AFF",
    "Fear":      "#AF52DE",
    "Love":      "#FF2D55",
    "Comfort":   "#A2845E",
    "Silence":   "#000000",
    "Neutral":   "#8E8E93",
    "Peace":     "#FFFFFF",
}


def _sibling_palette_csv() -> Optional[Path]:
    """Locate ``front-colors/references/palette.csv`` if co-installed.

    Returns
    -------
    pathlib.Path or None
        The path to the CSV if found; ``None`` otherwise. Search:

        1. ``FRONT_COLORS_PALETTE`` env var (explicit override).
        2. Sibling directory (``../../front-colors/references/palette.csv``
           relative to this file).
        3. ``~/.claude/skills/front-colors/references/palette.csv``.
        4. ``~/.opencode/skills/front-colors/references/palette.csv``.
    """
    env = os.environ.get("FRONT_COLORS_PALETTE", "").strip()
    if env:
        p = Path(env).expanduser()
        if p.is_file():
            return p

    here = Path(__file__).resolve()
    # front-figures/scripts/_style.py -> repo-root/front-colors/references/palette.csv
    sibling = here.parent.parent.parent / "front-colors" / "references" / "palette.csv"
    if sibling.is_file():
        return sibling

    for runtime in ("claude", "opencode"):
        p = Path.home() / f".{runtime}" / "skills" / "front-colors" / "references" / "palette.csv"
        if p.is_file():
            return p

    return None


def load_palette() -> Dict[str, str]:
    """Read the canonical palette; fall back to the built-in curated set.

    Returns
    -------
    dict of str to str
        Mapping ``{"Red": "#FF3B30", ...}``. Column names are the
        palette CSV's ``Base`` values; values are the CSV's ``Hexcode``
        column. Order follows the CSV; the fallback follows the order
        in ``_FALLBACK_PALETTE``.
    """
    csv_path = _sibling_palette_csv()
    if csv_path is None:
        return dict(_FALLBACK_PALETTE)

    palette: Dict[str, str] = {}
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            name = (row.get("Base") or row.get("name") or "").strip()
            hexv = (row.get("Hexcode") or row.get("Hex") or row.get("hex") or "").strip()
            if name and hexv.startswith("#") and len(hexv) in (4, 7):
                palette[name] = hexv.upper()
    return palette or dict(_FALLBACK_PALETTE)


def load_semantic_palette() -> Dict[str, Dict[str, Any]]:
    """Load the full semantic palette (base + emotion + concepts + psychology).

    Reads every column of ``front-colors/references/palette.csv``:
    ``Hexcode``, ``Base``, ``LightHex``, ``Emotion``, ``Concepts``,
    ``PsychologyPositive``, ``PsychologyNegative``. Documented at
    <https://harchaoui.org/warith/colors/>.

    Returns
    -------
    dict of str to dict
        Mapping ``{base_color_name: {"hex": "#RRGGBB", "light":
        "#RRGGBB", "emotion": str, "concepts": [str, ...],
        "psychology_positive": [str, ...],
        "psychology_negative": [str, ...]}}``.
    """
    csv_path = _sibling_palette_csv()
    if csv_path is None:
        return _fallback_semantic()

    out: Dict[str, Dict[str, Any]] = {}
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            base = (row.get("Base") or "").strip()
            hex_ = (row.get("Hexcode") or "").strip().upper()
            if not (base and hex_.startswith("#")):
                continue
            out[base] = {
                "hex": hex_,
                "light": (row.get("LightHex") or "").strip().upper() or hex_,
                "emotion": (row.get("Emotion") or "").strip(),
                "concepts": [c.strip() for c in (row.get("Concepts") or "").split(",") if c.strip()],
                "psychology_positive": [
                    c.strip() for c in (row.get("PsychologyPositive") or "").split(",") if c.strip()
                ],
                "psychology_negative": [
                    c.strip() for c in (row.get("PsychologyNegative") or "").split(",") if c.strip()
                ],
            }
    return out or _fallback_semantic()


def _fallback_semantic() -> Dict[str, Dict[str, Any]]:
    """Return a minimal semantic palette when the CSV is unavailable."""
    return {
        base: {
            "hex": hexv,
            "light": hexv,
            "emotion": next((e for e, h in _FALLBACK_EMOTIONS.items() if h == hexv), ""),
            "concepts": [],
            "psychology_positive": [],
            "psychology_negative": [],
        }
        for base, hexv in _FALLBACK_PALETTE.items()
    }


def emotion_to_hex(emotion: str) -> Optional[str]:
    """Return the curated hex for one of the palette's Emotion labels.

    Parameters
    ----------
    emotion : str
        Case-insensitive Emotion label from the palette CSV
        (``"Anger"``, ``"Joy"``, ``"Sadness"``, …).

    Returns
    -------
    str or None
        Hex string, or ``None`` when the label is not in the palette.
    """
    target = emotion.strip().lower()
    for base, meta in load_semantic_palette().items():
        if meta["emotion"].lower() == target:
            return meta["hex"]
    fallback = {k.lower(): v for k, v in _FALLBACK_EMOTIONS.items()}
    return fallback.get(target)


def concept_search(term: str) -> List[str]:
    """Return every palette hex whose ``Concepts`` column mentions ``term``.

    Parameters
    ----------
    term : str
        Case-insensitive concept term (``"Trust"``, ``"Bold"``,
        ``"Optimism"``, …).

    Returns
    -------
    list of str
        Hex strings, order-preserving.
    """
    target = term.strip().lower()
    matches: List[str] = []
    for meta in load_semantic_palette().values():
        joined = " ".join(meta.get("concepts", [])).lower()
        joined_pos = " ".join(meta.get("psychology_positive", [])).lower()
        if target in joined or target in joined_pos:
            matches.append(meta["hex"])
    return matches


def psychology_for(base: str) -> Dict[str, List[str]]:
    """Return the positive / negative psychology terms for a base color.

    Parameters
    ----------
    base : str
        Case-insensitive base color name (``"Red"``, ``"Green"``, …).

    Returns
    -------
    dict
        ``{"positive": [...], "negative": [...]}``. Empty lists if the
        palette CSV is unavailable.
    """
    target = base.strip().lower()
    for name, meta in load_semantic_palette().items():
        if name.lower() == target:
            return {
                "positive": meta.get("psychology_positive", []),
                "negative": meta.get("psychology_negative", []),
            }
    return {"positive": [], "negative": []}


# ------------------------------------------------------------------
# Categorical sequences for chart encodings
# ------------------------------------------------------------------
def qualitative_sequence(n: int = 8) -> List[str]:
    """Return the first ``n`` curated saturated hues.

    Parameters
    ----------
    n : int, optional
        How many colors to return (default 8). Cycles the base list
        when ``n`` exceeds the palette size.

    Returns
    -------
    list of str
        ``n`` hex strings, brand-order.
    """
    base = list(load_palette().values())
    # Skip the neutrals for a qualitative encoding.
    saturated = [h for h in base if h.upper() not in {"#000000", "#FFFFFF", "#8E8E93", "#A2845E"}]
    if n <= len(saturated):
        return saturated[:n]
    out: List[str] = []
    while len(out) < n:
        out.extend(saturated)
    return out[:n]


# ------------------------------------------------------------------
# Vega-Lite house config
# ------------------------------------------------------------------
def vega_config(dark: bool = False) -> Dict[str, object]:
    """Emit the front-* house-style Vega-Lite ``config`` block.

    Parameters
    ----------
    dark : bool, optional
        Toggle the dark-mode variant (background, text, gridlines).

    Returns
    -------
    dict
        A JSON-serialisable ``config`` block ready to merge into a
        Vega-Lite v5 spec.
    """
    fg = "#F5F5F7" if dark else "#1D1D1F"
    bg = "#1D1D1F" if dark else "#FFFFFF"
    return {
        "background": bg,
        "font": "Roboto, Roboto Serif, Roboto Mono, system-ui, sans-serif",
        "view": {"stroke": None, "cornerRadius": 10},
        "axis": {
            "domain": True,
            "domainColor": fg,
            "labelColor": fg,
            "titleColor": fg,
            "grid": False,
            "ticks": False,
            "labelFont": "Roboto Mono",
            "titleFont": "Roboto",
        },
        "axisTop": {"domain": False, "domainColor": None, "labels": False, "ticks": False, "title": None},
        "axisRight": {"domain": False, "domainColor": None, "labels": False, "ticks": False, "title": None},
        "legend": {
            "titleFont": "Roboto",
            "labelFont": "Roboto",
            "labelColor": fg,
            "titleColor": fg,
        },
        "title": {"font": "Roboto", "fontSize": 14, "color": fg, "subtitleFont": "Roboto", "subtitleColor": fg},
        "range": {"category": qualitative_sequence(8)},
        "bar": {"cornerRadiusEnd": 4},
        "line": {"strokeWidth": 2},
        "point": {"filled": True, "size": 40},
    }


# ------------------------------------------------------------------
# Matplotlib rcParams
# ------------------------------------------------------------------
def matplotlib_rc(dark: bool = False) -> Dict[str, object]:
    """Return matplotlib ``rcParams`` overrides in the front-* house style.

    Parameters
    ----------
    dark : bool, optional
        Toggle the dark-mode variant (background, text, grid).

    Returns
    -------
    dict
        Overrides ready to merge into ``matplotlib.rcParams``.
    """
    fg = "#F5F5F7" if dark else "#1D1D1F"
    bg = "#1D1D1F" if dark else "#FFFFFF"
    return {
        "font.family": ["Roboto", "system-ui", "sans-serif"],
        "font.sans-serif": ["Roboto", "Roboto Serif", "system-ui", "sans-serif"],
        "font.monospace": ["Roboto Mono", "monospace"],
        "figure.facecolor": bg,
        "axes.facecolor": bg,
        "axes.edgecolor": fg,
        "axes.labelcolor": fg,
        "axes.titlecolor": fg,
        "xtick.color": fg,
        "ytick.color": fg,
        "text.color": fg,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "axes.prop_cycle": _cycler(qualitative_sequence(8)),
    }


def _cycler(hexes: List[str]) -> Any:  # matplotlib cycler, typed at runtime only
    """Build a matplotlib cycler from a hex list.

    Deferred import so ``_style.py`` remains matplotlib-free at import
    time (the auditor uses this module too).
    """
    from cycler import cycler  # type: ignore
    return cycler(color=hexes)


# ------------------------------------------------------------------
# Polarity vocabulary
# ------------------------------------------------------------------
POLARITY_HINTS: Dict[str, str] = {
    # metric substring (lowercase) -> "higher-better" | "lower-better"
    "latency":       "lower-better",
    "response":      "lower-better",
    "response_time": "lower-better",
    "error":         "lower-better",
    "errors":        "lower-better",
    "bug":           "lower-better",
    "bugs":          "lower-better",
    "cost":          "lower-better",
    "churn":         "lower-better",
    "attrition":     "lower-better",
    "conversion":    "higher-better",
    "revenue":       "higher-better",
    "sales":         "higher-better",
    "retention":     "higher-better",
    "engagement":    "higher-better",
    "accuracy":      "higher-better",
    "f1":            "higher-better",
    "recall":        "higher-better",
    "precision":     "higher-better",
    "auc":           "higher-better",
    "roc_auc":       "higher-better",
    "r2":            "higher-better",
    "throughput":    "higher-better",
    "uptime":        "higher-better",
    "availability":  "higher-better",
    "mae":           "lower-better",
    "mse":           "lower-better",
    "rmse":          "lower-better",
    "loss":          "lower-better",
}


def infer_polarity(metric_name: str) -> Optional[str]:
    """Guess polarity from a metric name; return ``None`` when ambiguous.

    Parameters
    ----------
    metric_name : str
        The axis-title or column name to score.

    Returns
    -------
    str or None
        ``"higher-better"``, ``"lower-better"``, or ``None`` if no
        substring in :data:`POLARITY_HINTS` matched.
    """
    if not metric_name:
        return None
    lower = metric_name.lower()
    for substr, polarity in POLARITY_HINTS.items():
        # word-ish boundary: substring surrounded by non-alphanumerics or ends
        if substr in lower:
            return polarity
    return None


# ------------------------------------------------------------------
# Polarity → color mapping
# ------------------------------------------------------------------
#: Base color to reach for by polarity intent. Rationale:
#: **higher-better** and **lower-better** are both "goal-directed" —
#: readers want to see the metric move — so both map to Green
#: (psychology-positive: *Health*, *Hope*, *Growth*, *Prosperity*).
#: **target=** shifts to Blue (psychology-positive: *Trust*, *Logic*,
#: *Security*) — the metric is neutral; the frame is compliance.
#: The **breach** overlay uses Red (psychology-negative: *Warning*,
#: *Danger*) to flag SLA violations without co-opting the base
#: encoding. Source: <https://harchaoui.org/warith/colors/>.
POLARITY_COLOR: Dict[str, str] = {
    "higher-better": "Green",
    "lower-better":  "Green",
    "target":        "Blue",
    "breach":        "Red",
    "neutral":       "Gray",
}


def polarity_color(
    polarity: Optional[str],
    *,
    role: str = "primary",
    dark: bool = False,
) -> Optional[str]:
    """Return the house-style hex for a polarity intent.

    Never a substitute for the polarity text tag on the axis title —
    ~8 % of male viewers cannot read the color signal alone (see
    ``cvd-simulation.md``). Used as a *reinforcement* layer.

    Parameters
    ----------
    polarity : str or None
        One of ``"higher-better"``, ``"lower-better"``, or
        ``"target=<N>"``. Anything else returns ``None`` (caller keeps
        the qualitative palette).
    role : {'primary', 'breach'}, optional
        ``"primary"`` returns the goal color (Green or Blue);
        ``"breach"`` returns the SLA-violation overlay (Red).
    dark : bool, optional
        Currently unused — every curated base hex meets contrast on
        both background modes. Reserved for future light/dark variant
        selection.

    Returns
    -------
    str or None
        A hex string from the curated palette, or ``None`` when the
        polarity is not one the mapping recognises.
    """
    if not polarity:
        return None
    if role == "breach":
        base: str | None = POLARITY_COLOR["breach"]
    elif polarity.startswith("target="):
        base = POLARITY_COLOR["target"]
    else:
        base = POLARITY_COLOR.get(polarity)
    if base is None:
        return None
    palette = load_palette()
    return palette.get(base)


def polarity_tag(polarity: Optional[str], lang: str = "en") -> str:
    """Return the parenthesised polarity tag for an axis title.

    Parameters
    ----------
    polarity : {'higher-better', 'lower-better', None} or ``"target=<N>"``
        The polarity to render.
    lang : str, optional
        BCP-47 base tag; controls the translation.

    Returns
    -------
    str
        E.g. ``" (higher is better)"`` — includes the leading space so
        it can be safely appended to any axis title. Empty when
        polarity is ``None``.
    """
    if not polarity:
        return ""
    translations = {
        "higher-better": {"en": " (higher is better)", "fr": " (plus haut = mieux)", "de": " (höher ist besser)", "es": " (más alto es mejor)"},
        "lower-better":  {"en": " (lower is better)",  "fr": " (plus bas = mieux)",  "de": " (niedriger ist besser)", "es": " (más bajo es mejor)"},
    }
    if polarity.startswith("target="):
        n = polarity.split("=", 1)[1]
        return {
            "en": f" (target = {n})",
            "fr": f" (cible = {n})",
            "de": f" (Ziel = {n})",
            "es": f" (objetivo = {n})",
        }.get(lang, f" (target = {n})")
    return translations.get(polarity, {}).get(lang, translations.get(polarity, {}).get("en", ""))
