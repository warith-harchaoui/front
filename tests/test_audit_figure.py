"""
test_audit_figure — the front-figures static data-viz auditor.

`audit_figure.py` is a pure, deterministic auditor (no model, no network): a
Vega-Lite spec / SVG / HTML string in, a list of finding dicts out. That makes
its rule set directly unit-testable — each rule is asserted to fire on a
minimal offending spec and to stay silent on a clean one.

Author
------
Project maintainers.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "front-figures" / "scripts"))

import audit_figure as af  # noqa: E402


def _rules(spec: dict) -> set[str]:
    return {f["rule"] for f in af.rules_for_vega(spec, "spec.json")}


def test_clean_spec_has_no_findings() -> None:
    """A house-style bar chart with a titled, zero-based axis is clean."""
    spec = {
        "mark": "bar",
        "encoding": {
            "x": {"field": "name", "type": "nominal"},
            "y": {
                "field": "widgets",
                "type": "quantitative",
                "axis": {"title": "Widgets"},
                "scale": {"zero": True},
            },
        },
    }
    assert af.rules_for_vega(spec, "spec.json") == []


def test_missing_axis_title_fires() -> None:
    """A quantitative axis without a title is an error."""
    spec = {"encoding": {"y": {"type": "quantitative", "axis": {}}}}
    assert "missing-axis-title" in _rules(spec)


def test_dual_y_axis_fires() -> None:
    """Two independent y scales are an error."""
    spec = {"resolve": {"scale": {"y": "independent"}}}
    assert "dual-y-axis" in _rules(spec)


def test_truncated_baseline_fires_on_bar() -> None:
    """A bar chart with zero=false on a linear scale truncates the baseline."""
    spec = {
        "mark": "bar",
        "encoding": {"y": {"type": "quantitative", "axis": {"title": "Widgets"},
                           "scale": {"zero": False}}},
    }
    assert "truncated-baseline" in _rules(spec)


def test_truncated_baseline_exempt_on_log_scale() -> None:
    """A log scale legitimately has no zero — no truncated-baseline finding."""
    spec = {
        "mark": "bar",
        "encoding": {"y": {"type": "quantitative", "axis": {"title": "Widgets"},
                           "scale": {"zero": False, "type": "log"}}},
    }
    assert "truncated-baseline" not in _rules(spec)


def test_rainbow_palette_fires() -> None:
    """A rainbow/jet colour scheme is an error."""
    spec = {"encoding": {"color": {"type": "nominal", "scale": {"scheme": "rainbow"}}}}
    assert "rainbow-palette" in _rules(spec)


def test_missing_polarity_fires_on_known_metric() -> None:
    """A recognised polarised metric with no direction tag is flagged."""
    metric = af.POLARISED_METRIC_SUBSTRINGS[0]
    spec = {"encoding": {"y": {"type": "quantitative", "axis": {"title": metric}}}}
    assert "missing-polarity" in _rules(spec)


def test_missing_polarity_silent_when_tagged() -> None:
    """The same metric with a direction tag is clean of the polarity rule."""
    metric = af.POLARISED_METRIC_SUBSTRINGS[0]
    spec = {"encoding": {"y": {"type": "quantitative",
                               "axis": {"title": f"{metric} (higher is better)"}}}}
    assert "missing-polarity" not in _rules(spec)


def test_html_figure_without_role_is_flagged() -> None:
    """A rendered <figure> with no role/figcaption trips role-img-missing."""
    html = "<figure><img src='c.png' alt='chart'></figure>"
    rules = {f["rule"] for f in af.rules_for_html(html, "page.html")}
    assert "role-img-missing" in rules


def test_format_json_is_valid_json() -> None:
    """The JSON formatter emits parseable JSON carrying the rule ids."""
    findings = af.rules_for_vega({"encoding": {"y": {"type": "quantitative", "axis": {}}}},
                                 "spec.json")
    parsed = json.loads(af.format_json(findings))
    assert parsed["findings"][0]["rule"] == "missing-axis-title"
    assert parsed["summary"]["errors"] == 1


def test_make_finding_shape() -> None:
    """A finding carries path / line / rule / severity / message."""
    f = af.make_finding("x-rule", "error", "msg", "p.json", 3)
    assert set(f) == {"path", "line", "rule", "severity", "message"}
    assert f["severity"] == "error" and f["line"] == 3
