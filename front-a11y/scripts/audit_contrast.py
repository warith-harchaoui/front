#!/usr/bin/env python3
"""
audit_contrast
==============

Audit a palette's foreground / background contrast against the WCAG
ratio thresholds (4.5:1 for body text, 3:1 for large text and UI, 7:1
for AAA). For failing pairs, propose the nearest accessible alternative
by walking the OKLCH lightness axis.

The script accepts two input shapes:

* A JSON palette: ``{"role": "#RRGGBB", ...}`` or ``{"role": {"DEFAULT": "#…", "dark": "#…"}, ...}``.
* The skill's built-in default palette (when no ``--palette`` is given).

It is **deterministic** — no model, no network — and uses standard formulas:

* WCAG relative luminance (the 2.4-gamma formula).
* OKLab / OKLCH conversion via Björn Ottosson's published matrices
  (https://bottosson.github.io/posts/oklab/).

Usage
-----
::

    # Audit the skill's built-in palette at WCAG AA (4.5:1)
    python audit_contrast.py

    # AAA threshold
    python audit_contrast.py --target 7

    # External palette + suggested fixes
    python audit_contrast.py --palette my-palette.json --fix

    # JSON output for CI
    python audit_contrast.py --format json

Notes
-----
* Python 3.9+, stdlib only.
* The "fix" search walks the OKLCH L axis at 0.01 resolution; in practice
  the search converges in tens of microseconds per pair.

Author
------
`Warith Harchaoui, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path as _PathHelper

sys.path.insert(0, str(_PathHelper(__file__).resolve().parent))
from _argparse import make_parser  # noqa: E402
from pathlib import Path


# ── Skill's built-in palette ────────────────────────────────────────────────

#: Default palette used when ``--palette`` is not supplied. Mirrors the
#: skill's semantic Tailwind tokens.
DEFAULT_PALETTE: dict[str, dict[str, str]] = {
    "brand-blue":      {"DEFAULT": "#007AFF", "dark": "#0A84FF", "light": "#CCE4FF"},
    "brand-red":       {"DEFAULT": "#FF3B30", "dark": "#FF453A", "light": "#FFD8D6"},
    "brand-green":     {"DEFAULT": "#28CD41", "dark": "#30D158", "light": "#D4F5D9"},
    "brand-orange":    {"DEFAULT": "#FF9500", "dark": "#FF9F0A", "light": "#FFEACC"},
    "brand-yellow":    {"DEFAULT": "#FFCC00", "dark": "#FFD60A", "light": "#FFF5CC"},
    "brand-purple":    {"DEFAULT": "#AF52DE", "dark": "#BF5AF2", "light": "#EFDCF8"},
    "brand-pink":      {"DEFAULT": "#FF2D55", "dark": "#FF375F", "light": "#FFD5DD"},
    "brand-turquoise": {"DEFAULT": "#79DBDC", "dark": "#64D2FF", "light": "#00FFEF"},
    "label-primary":   {"DEFAULT": "#000000", "dark": "#FFFFFF"},
    "label-secondary": {"DEFAULT": "#3C3C434D", "dark": "#EBEBF54D"},
    "surface-primary": {"DEFAULT": "#FFFFFF", "dark": "#000000"},
    "surface-secondary": {"DEFAULT": "#F2F2F7", "dark": "#1C1C1E"},
}


# ── Hex ↔ linear sRGB ──────────────────────────────────────────────────────

def parse_hex(s: str) -> tuple[float, float, float]:
    """
    Parse a 3-, 6-, or 8-digit hex color into linear sRGB.

    The alpha channel (if present) is dropped — WCAG contrast is computed
    against opaque backgrounds; transparent overlays must be flattened
    upstream of this script.

    Parameters
    ----------
    s : str
        Hex color, with or without a leading ``#``.

    Returns
    -------
    tuple of float
        ``(R, G, B)`` triple of *linear-light* values in ``[0.0, 1.0]``.

    Raises
    ------
    ValueError
        On an unrecognized format.
    """
    s = s.lstrip("#").strip()
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) == 8:
        # Drop the alpha channel for contrast math.
        s = s[:6]
    if len(s) != 6:
        raise ValueError(f"Bad hex color: {s!r}")
    r8, g8, b8 = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
    return srgb_to_linear(r8), srgb_to_linear(g8), srgb_to_linear(b8)


def srgb_to_linear(c: int) -> float:
    """Convert an 8-bit sRGB channel to linear sRGB in ``[0, 1]``."""
    f: float = c / 255.0
    return f / 12.92 if f <= 0.04045 else ((f + 0.055) / 1.055) ** 2.4


def linear_to_srgb(f: float) -> int:
    """Convert a linear-sRGB value to an 8-bit channel, clamped to ``[0, 255]``."""
    if f <= 0.0:
        return 0
    if f >= 1.0:
        return 255
    out: float = f * 12.92 if f <= 0.0031308 else 1.055 * f ** (1.0 / 2.4) - 0.055
    return max(0, min(255, round(out * 255)))


def to_hex(rgb_linear: tuple[float, float, float]) -> str:
    """Format linear sRGB as an upper-case ``#RRGGBB`` string."""
    return "#" + "".join(f"{linear_to_srgb(c):02X}" for c in rgb_linear)


# ── WCAG relative luminance + contrast ratio ────────────────────────────────

def relative_luminance(rgb_linear: tuple[float, float, float]) -> float:
    """
    Compute WCAG relative luminance.

    Parameters
    ----------
    rgb_linear : tuple of float
        Linear-light sRGB values.

    Returns
    -------
    float
        Luminance in ``[0, 1]``.
    """
    r, g, b = rgb_linear
    # Weights from WCAG 2.x.
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    """
    Compute the WCAG contrast ratio between two colours.

    Parameters
    ----------
    a, b : tuple of float
        Linear-light sRGB triples.

    Returns
    -------
    float
        Ratio in ``[1.0, 21.0]``.
    """
    la = relative_luminance(a)
    lb = relative_luminance(b)
    light = max(la, lb)
    dark = min(la, lb)
    return (light + 0.05) / (dark + 0.05)


# ── OKLab ↔ linear sRGB (Björn Ottosson) ───────────────────────────────────

def linear_to_oklab(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    """
    Convert linear sRGB to OKLab.

    Parameters
    ----------
    rgb : tuple of float
        Linear-light sRGB values.

    Returns
    -------
    tuple of float
        ``(L, a, b)`` in OKLab.
    """
    r, g, b = rgb
    # Step 1: linear sRGB → LMS (cone responses).
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    # Step 2: cube root (perceptual companding).
    l_ = l ** (1 / 3) if l >= 0 else -(-l) ** (1 / 3)
    m_ = m ** (1 / 3) if m >= 0 else -(-m) ** (1 / 3)
    s_ = s ** (1 / 3) if s >= 0 else -(-s) ** (1 / 3)
    # Step 3: LMS → Lab.
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklab_to_linear(lab: tuple[float, float, float]) -> tuple[float, float, float]:
    """Inverse of :func:`linear_to_oklab`."""
    L, a, b = lab
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l = l_ ** 3
    m = m_ ** 3
    s = s_ ** 3
    return (
        +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )


def oklab_to_oklch(lab: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert OKLab to OKLCH (polar form)."""
    L, a, b = lab
    C = math.sqrt(a * a + b * b)
    H = math.degrees(math.atan2(b, a))
    if H < 0:
        H += 360
    return L, C, H


def oklch_to_oklab(lch: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert OKLCH back to OKLab."""
    L, C, H = lch
    rad = math.radians(H)
    return L, C * math.cos(rad), C * math.sin(rad)


# ── Suggestion search ──────────────────────────────────────────────────────

def adjust_for_contrast(
    fg_linear: tuple[float, float, float],
    bg_linear: tuple[float, float, float],
    target: float,
) -> tuple[str, float] | None:
    """
    Find the nearest accessible alternative to ``fg_linear`` on the
    OKLCH lightness axis (keeping hue and chroma fixed).

    The search walks L from 0 to 1 in 0.01 steps, picks the candidate that
    passes the target *and* is closest to the original L.

    Parameters
    ----------
    fg_linear : tuple of float
        Source foreground in linear sRGB.
    bg_linear : tuple of float
        Background in linear sRGB.
    target : float
        Minimum acceptable contrast ratio.

    Returns
    -------
    tuple of (str, float) or None
        ``(suggested_hex, achieved_ratio)`` or ``None`` if no candidate
        meets the target (very rare — usually means the background itself
        is very close to mid-gray).
    """
    L, C, H = oklab_to_oklch(linear_to_oklab(fg_linear))
    best: tuple[float, tuple[float, float, float]] | None = None
    # ``L'' steps from 0.0 to 1.0 inclusive.
    for i in range(0, 101):
        l_test: float = i / 100.0
        candidate = oklab_to_linear(oklch_to_oklab((l_test, C, H)))
        ratio = contrast_ratio(candidate, bg_linear)
        if ratio >= target:
            distance: float = abs(l_test - L)
            if best is None or distance < best[0]:
                best = (distance, candidate)
    if best is None:
        return None
    return to_hex(best[1]), contrast_ratio(best[1], bg_linear)


# ── Audit logic ─────────────────────────────────────────────────────────────

def normalize_palette(raw: dict) -> dict[str, str]:
    """
    Flatten a nested palette to ``{role: hex}``.

    Accepts both flat (``{"key": "#fff"}``) and nested
    (``{"key": {"DEFAULT": "#fff", "dark": "#000"}}``) shapes.

    Parameters
    ----------
    raw : dict
        Parsed JSON palette.

    Returns
    -------
    dict of str
        Map from a fully-qualified role name to its hex value.
    """
    flat: dict[str, str] = {}
    for role, value in raw.items():
        if isinstance(value, str):
            flat[role] = value
        elif isinstance(value, dict):
            for variant, hex_val in value.items():
                key: str = role if variant.upper() == "DEFAULT" else f"{role}-{variant}"
                flat[key] = hex_val
    return flat


#: Which "foreground" roles should be checked against which "background" roles.
#: The naming convention is conventional for this skill — anything with
#: "label" or "brand" treated as text/icon, anything with "surface" treated as
#: a background.
def is_foreground(role: str) -> bool:
    """Return True when ``role`` is conventionally drawn on top of a surface."""
    return role.startswith(("label-", "brand-")) and not role.endswith(("-light", "-dark"))


def is_background(role: str) -> bool:
    """Return True when ``role`` is conventionally a surface colour."""
    return role.startswith("surface-")


def audit(
    palette: dict[str, str],
    target: float,
    propose_fix: bool,
) -> dict:
    """
    Audit every (foreground, background) pair against the target ratio.

    Parameters
    ----------
    palette : dict of str
        Flattened palette (role → hex).
    target : float
        Minimum acceptable WCAG contrast ratio.
    propose_fix : bool
        If True, attach a suggested replacement to each failing pair.

    Returns
    -------
    dict
        ``{"target": <target>, "pairs": [...]}`` where each pair entry has
        ``fg``, ``bg``, ``ratio``, ``passes``, and optionally ``suggested``.
    """
    out: list[dict] = []
    for fg_role, fg_hex in palette.items():
        if not is_foreground(fg_role):
            continue
        for bg_role, bg_hex in palette.items():
            if not is_background(bg_role):
                continue
            fg = parse_hex(fg_hex)
            bg = parse_hex(bg_hex)
            ratio = contrast_ratio(fg, bg)
            entry: dict = {
                "fg": {"role": fg_role, "hex": fg_hex.upper()},
                "bg": {"role": bg_role, "hex": bg_hex.upper()},
                "ratio": round(ratio, 2),
                "passes": ratio >= target,
            }
            if not entry["passes"] and propose_fix:
                fix = adjust_for_contrast(fg, bg, target)
                if fix is not None:
                    entry["suggested"] = {"hex": fix[0], "ratio": round(fix[1], 2)}
            out.append(entry)
    return {"target": target, "pairs": out}


# ── CLI entry point ────────────────────────────────────────────────────────

def main() -> int:
    """Run the audit. Exit code 0 when every checked pair passes, 1 otherwise."""
    p = make_parser(
        prog="front-a11y-contrast",
        description="Audit a palette's foreground/background contrast against WCAG. "
                    "Walks every (label, surface) pair, suggests the nearest OKLCH "
                    "neighbour for failing pairs when --fix is set.",
        epilog="Examples:\n"
               "  front-a11y-contrast --palette palette.json\n"
               "  front-a11y-contrast --palette palette.json --target 7 --fix\n"
               "  front-a11y-contrast --format json --palette palette.json\n",
    )
    p.add_argument(
        "--palette", type=Path,
        help="JSON palette. When omitted, the skill's built-in default is used.",
    )
    p.add_argument(
        "--target", type=float, default=4.5,
        help="Minimum acceptable WCAG contrast ratio. 4.5 (AA body), 7 (AAA), or 3 (UI/large).",
    )
    p.add_argument(
        "--fix", action="store_true",
        help="Propose a suggested fix for each failing pair (nearest OKLCH neighbour).",
    )
    p.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format. Default: text.",
    )
    args = p.parse_args()

    if args.palette is not None:
        raw = json.loads(args.palette.read_text(encoding="utf-8"))
    else:
        raw = DEFAULT_PALETTE
    flat = normalize_palette(raw)

    result = audit(flat, args.target, args.fix)

    if args.format == "json":
        json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        print(f"Target ratio: {result['target']}")
        print()
        passing = 0
        failing = 0
        for pair in result["pairs"]:
            mark = "✓" if pair["passes"] else "✗"
            print(
                f"  {mark} {pair['fg']['role']:>22}  on  {pair['bg']['role']:>22}"
                f"   ratio {pair['ratio']:.2f}"
            )
            if not pair["passes"]:
                failing += 1
                if "suggested" in pair:
                    print(
                        f"      → suggest {pair['suggested']['hex']}  "
                        f"(ratio {pair['suggested']['ratio']:.2f})"
                    )
            else:
                passing += 1
        print()
        print(f"{passing} pass, {failing} fail.")

    failing_count: int = sum(1 for p in result["pairs"] if not p["passes"])
    return 0 if failing_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
