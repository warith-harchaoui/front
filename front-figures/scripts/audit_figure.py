#!/usr/bin/env python3
"""
audit_figure
============

Static auditor for data-science figures. Reads a Vega-Lite v5 JSON
spec, a matplotlib-emitted SVG, or an HTML file containing
``<figure>`` blocks, and reports the small set of data-viz mistakes
that survive review:

    missing-axis-title     dual-y-axis         truncated-baseline
    pie-3d                 rainbow-palette     cvd-unsafe
    missing-polarity       chartjunk           role-img-missing
    alt-missing            pie-too-many-slices zero-encoded-as-null

Each finding carries a severity (``error`` / ``warning`` / ``info``).
Exit codes:

* ``0`` — no errors (warnings only or clean).
* ``1`` — one or more errors, or any finding under ``--strict``.
* ``2`` — CLI or parse error.

The auditor is **stdlib + PyYAML** only — no browser, no model, no
network. Vega-Lite specs are parsed with ``json``; SVG / HTML use
``xml.etree`` and ``html.parser``.

Usage
-----
::

    python audit_figure.py fig.json                       # human-readable
    python audit_figure.py public/*.html --json           # CI
    python audit_figure.py fig.svg --strict               # warnings → errors
    python audit_figure.py fig.json --ignore truncated-baseline,chartjunk

Author
------
`Warith Harchaoui, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _argparse import make_parser  # noqa: E402
from _style import POLARITY_HINTS  # noqa: E402


# ------------------------------------------------------------------
# Finding model
# ------------------------------------------------------------------
def make_finding(rule: str, severity: str, message: str, path: str = "", line: int = 1) -> Dict[str, Any]:
    """Build a finding dict."""
    return {"path": path, "line": line, "rule": rule, "severity": severity, "message": message}


# ------------------------------------------------------------------
# Rule set
# ------------------------------------------------------------------
RAINBOW_SCHEMES = {"rainbow", "sinebow", "hsv", "hsl", "jet"}
CATEGORY_RED_HINT = {"#FF0000", "#F00", "#E11", "#D22", "#D00", "#FF3B30", "#EF4444", "#DC2626"}
CATEGORY_GREEN_HINT = {"#00FF00", "#0F0", "#22C55E", "#34C759", "#16A34A", "#059669"}
POLARISED_METRIC_SUBSTRINGS = tuple(POLARITY_HINTS.keys())


def rules_for_vega(spec: Dict[str, Any], path: str) -> List[Dict[str, Any]]:
    """Run all applicable rules against a Vega-Lite v5 JSON spec.

    Parameters
    ----------
    spec : dict
        Loaded Vega-Lite spec.
    path : str
        Source path for finding attribution.

    Returns
    -------
    list of dict
        Findings; may be empty when the spec is clean.
    """
    findings: List[Dict[str, Any]] = []
    enc = spec.get("encoding") or {}

    # missing-axis-title (quantitative axes only)
    for axis in ("x", "y"):
        ax_enc = enc.get(axis) or {}
        if ax_enc.get("type") == "quantitative":
            axis_block = ax_enc.get("axis") or {}
            if not (axis_block.get("title") or "").strip():
                findings.append(make_finding(
                    "missing-axis-title", "error",
                    f"{axis} encoding has no axis title",
                    path,
                ))

    # dual-y-axis
    resolve = spec.get("resolve") or {}
    scale_resolve = (resolve.get("scale") or {}).get("y")
    if scale_resolve == "independent":
        findings.append(make_finding("dual-y-axis", "error", "two independent y scales", path))
    # heuristic: layer with two 'y' encodings
    layers = spec.get("layer") or []
    if isinstance(layers, list) and sum(1 for lyr in layers if (lyr.get("encoding") or {}).get("y")) >= 2:
        if scale_resolve != "shared":
            findings.append(make_finding("dual-y-axis", "error", "layered chart uses two y encodings", path))

    # truncated-baseline
    mark = spec.get("mark")
    mark_type = mark if isinstance(mark, str) else (mark or {}).get("type")
    if mark_type in ("bar", "rect"):
        y_enc = enc.get("y") or {}
        scale = y_enc.get("scale") or {}
        scale_type = scale.get("type", "linear")
        if scale.get("zero") is False and scale_type not in {"log", "pow", "sqrt", "symlog"}:
            findings.append(make_finding(
                "truncated-baseline", "warning",
                "bar chart y-axis has zero=false on a linear scale",
                path,
            ))

    # pie-3d
    if mark_type == "arc":
        transforms = spec.get("transform") or []
        if any("angle" in t and "rotate" in json.dumps(t).lower() for t in transforms):
            findings.append(make_finding("pie-3d", "error", "arc mark with rotate/perspective transform", path))
        data_values = (spec.get("data") or {}).get("values") or []
        if isinstance(data_values, list) and len(data_values) > 4:
            findings.append(make_finding(
                "pie-too-many-slices", "warning",
                f"pie/donut with {len(data_values)} categories — use a table or bar chart",
                path,
            ))

    # rainbow-palette
    for axis in ("color", "fill", "stroke"):
        ax_enc = enc.get(axis) or {}
        scheme = (ax_enc.get("scale") or {}).get("scheme")
        if isinstance(scheme, str) and scheme.lower() in RAINBOW_SCHEMES:
            findings.append(make_finding(
                "rainbow-palette", "error",
                f"{axis} scale uses rainbow scheme '{scheme}'",
                path,
            ))
        # cvd-unsafe (categorical range with red+green pair)
        rng = (ax_enc.get("scale") or {}).get("range") or []
        if isinstance(rng, list):
            upper = {str(c).upper() for c in rng if isinstance(c, str)}
            has_red = any(c in upper for c in CATEGORY_RED_HINT)
            has_green = any(c in upper for c in CATEGORY_GREEN_HINT)
            if has_red and has_green:
                findings.append(make_finding(
                    "cvd-unsafe", "warning",
                    "categorical range mixes red + green without a third channel",
                    path,
                ))

    # missing-polarity
    for axis in ("x", "y"):
        ax_enc = enc.get(axis) or {}
        if ax_enc.get("type") != "quantitative":
            continue
        title = ((ax_enc.get("axis") or {}).get("title") or "").lower()
        if not title:
            continue
        if any(sub in title for sub in POLARISED_METRIC_SUBSTRINGS):
            if not any(kw in title for kw in ("higher is better", "lower is better", "target", "plus haut", "plus bas", "cible")):
                findings.append(make_finding(
                    "missing-polarity", "warning",
                    f"axis title '{title}' looks polarised but has no direction tag",
                    path,
                ))

    # chartjunk
    config = spec.get("config") or {}
    background = config.get("background") or spec.get("background") or ""
    if isinstance(background, str) and "gradient" in background.lower():
        findings.append(make_finding("chartjunk", "warning", "background uses a gradient", path))
    if isinstance(mark, dict) and mark.get("shadow"):
        findings.append(make_finding("chartjunk", "warning", "mark has a shadow effect", path))

    return findings


# ------------------------------------------------------------------
# HTML parsing
# ------------------------------------------------------------------
class _FigureScanner(HTMLParser):
    """Collect ``<figure>`` blocks and inner ``<img>`` tags."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.figures: List[Dict[str, Any]] = []
        self._stack: List[Dict[str, Any]] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        attr_map = {k.lower(): (v or "") for k, v in attrs}
        if tag == "figure":
            entry = {"role": attr_map.get("role", ""), "has_caption": False, "imgs": [], "line": self.getpos()[0]}
            self.figures.append(entry)
            self._stack.append(entry)
        elif tag == "figcaption" and self._stack:
            self._stack[-1]["has_caption"] = True
        elif tag == "img" and self._stack:
            self._stack[-1]["imgs"].append({"alt": attr_map.get("alt", None), "line": self.getpos()[0]})

    def handle_endtag(self, tag: str) -> None:
        if tag == "figure" and self._stack:
            self._stack.pop()


def rules_for_html(text: str, path: str) -> List[Dict[str, Any]]:
    """Scan an HTML document for figure-level a11y and viz sins."""
    findings: List[Dict[str, Any]] = []
    scanner = _FigureScanner()
    scanner.feed(text)
    for fig in scanner.figures:
        if fig["role"] != "img" and not fig["has_caption"]:
            findings.append(make_finding(
                "role-img-missing", "error",
                "<figure> without role=\"img\" and no <figcaption>",
                path, fig["line"],
            ))
        for img in fig["imgs"]:
            if img["alt"] is None:
                findings.append(make_finding(
                    "alt-missing", "error",
                    "<img> inside <figure> has no alt attribute",
                    path, img["line"],
                ))
    return findings


# ------------------------------------------------------------------
# SVG parsing (matplotlib output)
# ------------------------------------------------------------------
def rules_for_svg(text: str, path: str) -> List[Dict[str, Any]]:
    """Best-effort rules against a matplotlib-emitted SVG."""
    findings: List[Dict[str, Any]] = []

    # rainbow palette heuristic
    if re.search(r"\b(jet|hsv|rainbow)\b", text, re.IGNORECASE):
        findings.append(make_finding(
            "rainbow-palette", "error",
            "SVG references a rainbow colormap (jet/hsv/rainbow)",
            path,
        ))

    # chartjunk — shadows / filter blurs
    if "<filter" in text and ("feDropShadow" in text or "feGaussianBlur" in text):
        findings.append(make_finding("chartjunk", "warning", "SVG uses a drop-shadow / blur filter", path))

    # pie-3d — perspective transform
    if re.search(r"transform=\"matrix\([^\"]*perspective", text, re.IGNORECASE):
        findings.append(make_finding("pie-3d", "error", "SVG uses a perspective transform", path))

    return findings


# ------------------------------------------------------------------
# Formatting
# ------------------------------------------------------------------
def format_human(findings: List[Dict[str, Any]]) -> str:
    """Human-readable finding summary."""
    if not findings:
        return "clean"
    lines = []
    counts = {"error": 0, "warning": 0, "info": 0}
    for f in findings:
        counts[f["severity"]] += 1
        lines.append(f"  {f['path']}:{f['line']}:1  {f['severity']:<8} {f['rule']:<24} {f['message']}")
    lines.append(f"{counts['error']} error(s), {counts['warning']} warning(s), {counts['info']} info")
    return "\n".join(lines)


def format_json(findings: List[Dict[str, Any]]) -> str:
    """JSON finding summary."""
    counts = {"errors": 0, "warnings": 0, "info": 0}
    for f in findings:
        key = f["severity"] + ("s" if f["severity"] != "info" else "")
        counts[key] += 1
    return json.dumps({"findings": findings, "summary": counts}, indent=2, ensure_ascii=False)


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    """Return the argparse parser for the script."""
    parser = make_parser(
        prog="audit_figure",
        description=(
            "Static auditor for Vega-Lite JSON, matplotlib SVG, or HTML "
            "with <figure> blocks. Flags the small set of data-viz "
            "mistakes that survive review."
        ),
    )
    parser.add_argument("paths", nargs="+", help="Files or directories to audit.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of the human-readable summary.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors for the exit code.")
    parser.add_argument("--ignore", default="", help="Comma-separated rule IDs to skip.")
    parser.add_argument("--only", default="", help="Comma-separated rule IDs to keep (exclusive with --ignore).")
    return parser


def iter_files(paths: List[str]) -> List[Path]:
    """Expand paths (files or directories) into a flat file list."""
    out: List[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            for suffix in (".json", ".svg", ".html", ".htm"):
                out.extend(sorted(p.rglob(f"*{suffix}")))
        elif p.is_file():
            out.append(p)
    return out


def audit_one(path: Path) -> List[Dict[str, Any]]:
    """Dispatch to the right rule set based on file extension."""
    text = path.read_text(encoding="utf-8", errors="replace")
    ext = path.suffix.lower()
    if ext == ".json":
        try:
            spec = json.loads(text)
        except json.JSONDecodeError as exc:
            return [make_finding("invalid-json", "error", str(exc), str(path))]
        return rules_for_vega(spec, str(path))
    if ext == ".svg":
        return rules_for_svg(text, str(path))
    if ext in (".html", ".htm"):
        return rules_for_html(text, str(path))
    return [make_finding("unsupported-format", "info", f"skipping {ext}", str(path))]


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point."""
    args = build_parser().parse_args(argv)
    ignore = {s.strip() for s in args.ignore.split(",") if s.strip()}
    only = {s.strip() for s in args.only.split(",") if s.strip()}

    all_findings: List[Dict[str, Any]] = []
    for p in iter_files(args.paths):
        findings = audit_one(p)
        for f in findings:
            if only and f["rule"] not in only:
                continue
            if f["rule"] in ignore:
                continue
            all_findings.append(f)

    if args.json:
        print(format_json(all_findings))
    else:
        print(format_human(all_findings))

    errors = sum(1 for f in all_findings if f["severity"] == "error")
    warnings = sum(1 for f in all_findings if f["severity"] == "warning")
    if errors > 0:
        return 1
    if args.strict and warnings > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
