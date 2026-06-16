#!/usr/bin/env python3
"""
lint_a11y
=========

Lightweight accessibility linter for HTML emitted by (or for) the ``front``
skill. The linter is **static** — no browser, no DOM, no JS execution —
so it runs in milliseconds and slots cleanly into a code-emit pipeline or
a pre-commit hook.

The rules are curated to catch the ~20 violations that account for the
bulk of real-world WCAG / WAI-ARIA failures. None of them require the
runtime DOM; all are decidable from source.

Rule catalogue
--------------
========================  =====================================================
``img-missing-alt``         ``<img>`` with no ``alt`` attribute. Empty
                            ``alt=""`` is correct for decorative images;
                            *omitting* the attribute is not.
``img-redundant-aria``      ``alt=""`` plus ``role="presentation"`` or
                            ``aria-hidden="true"``: redundant.
``a-missing-href``          ``<a>`` without ``href`` (use ``<button>``).
``a-empty``                 ``<a>`` with no text and no accessible name.
``button-empty``            ``<button>`` with no text and no ``aria-label``.
``div-onclick``             ``<div>`` / ``<span>`` with ``onclick`` but no
                            ``role="button"`` and ``tabindex``.
``input-missing-label``     ``<input>`` not wrapped in a ``<label>`` and not
                            referenced by a ``<label for=>``.
``dialog-missing-close``    ``<dialog>`` without a close affordance
                            (``<button>``, ``value="cancel"``, ``[autofocus]``).
``html-missing-lang``       ``<html>`` without ``lang``.
``tabindex-positive``       ``tabindex`` ≥ 1.
``aria-hidden-interactive`` ``aria-hidden="true"`` on a button / link / input.
``heading-skip``            Headings out of order (e.g. ``<h2>`` → ``<h4>``).
``color-only-state``        Tailwind ``*-red-*`` / ``*-green-*`` on a span
                            with no icon, label, or text sibling. Catches the
                            "red is bad / green is good" anti-pattern.
``motion-no-reduce-guard``  ``animate-*`` or ``transition-transform`` without
                            a ``motion-reduce:`` peer.
========================  =====================================================

Output
------
Plain-text report by default; use ``--format json`` for machine consumption.
Exit code ``1`` on any finding (unless ``--ignore`` covers it), ``0``
otherwise. The script can be pointed at a single file or a directory.

Usage
-----
::

    # Lint a single page
    python lint_a11y.py public/index.html

    # Lint a tree
    python lint_a11y.py public/

    # JSON output for CI
    python lint_a11y.py --format json public/index.html

    # Suppress two rules
    python lint_a11y.py --ignore heading-skip,motion-no-reduce-guard public/

Notes
-----
* Python 3.9+, stdlib only (``html.parser``, ``argparse``, ``pathlib``).
* The parser is forgiving — it walks documents that contain mixed-case
  tags, missing closures, and inline scripts without raising.
* This linter is a *first pass*, not a replacement for ``axe-core`` or
  manual screen-reader testing. It catches the violations easiest to fix.

Author
------
`Warith Harchaoui, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional


# ── Data structures ────────────────────────────────────────────────────────

@dataclass
class Element:
    """
    Minimal representation of one HTML element captured during parsing.

    Attributes
    ----------
    tag : str
        Lower-cased tag name (``"img"``, ``"button"``, …).
    attrs : dict
        Attribute map. Boolean attributes resolve to the empty string.
    line : int
        1-based source line of the element's opening tag.
    text : str
        Concatenated text content of the element (children stripped).
    children : list of Element
        Direct element children, in source order.
    parent : Element or None
        Parent element, or ``None`` for the synthetic root.
    """

    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    line: int = 0
    text: str = ""
    children: list["Element"] = field(default_factory=list)
    parent: Optional["Element"] = None


@dataclass
class Finding:
    """
    One reported accessibility violation.

    Attributes
    ----------
    rule : str
        Rule identifier (e.g. ``"img-missing-alt"``).
    line : int
        1-based source line of the offending element.
    message : str
        Human-readable explanation suitable for a console line.
    """

    rule: str
    line: int
    message: str


# ── HTML walker ────────────────────────────────────────────────────────────

# Void elements that never have a closing tag in HTML5; ``html.parser`` does
# not flag them, so the walker maintains an explicit list.
VOID_ELEMENTS: frozenset[str] = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "keygen", "link", "meta", "param", "source", "track", "wbr",
})


class TreeBuilder(HTMLParser):
    """
    Build a lightweight element tree from an HTML string.

    The parser is intentionally forgiving — case-folding tag names, treating
    void elements as self-closing, and collecting source line numbers so
    findings can be reported usefully.
    """

    def __init__(self) -> None:
        # ``convert_charrefs=False`` keeps entities literal so ``<pre>`` blocks
        # in user docs survive the round-trip unchanged.
        super().__init__(convert_charrefs=False)
        # The root is a synthetic ``html`` element so the tree always has a
        # single entry point; the real ``<html>`` becomes its only child.
        self.root: Element = Element(tag="root", line=0)
        self.stack: list[Element] = [self.root]

    # html.parser hooks --------------------------------------------------

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        # ``getpos()`` returns (line, column) for the current token; only
        # the line is preserved.
        line, _ = self.getpos()
        elem = Element(
            tag=tag.lower(),
            attrs={k.lower(): (v or "") for k, v in attrs},
            line=line,
            parent=self.stack[-1],
        )
        self.stack[-1].children.append(elem)
        # Void elements never push onto the stack — they would otherwise leak
        # if the source forgets a trailing ``/``.
        if tag.lower() not in VOID_ELEMENTS:
            self.stack.append(elem)

    def handle_endtag(self, tag: str) -> None:
        # Pop until we hit a matching open tag (or the root). This handles
        # documents with mismatched closes without raising.
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag.lower():
                del self.stack[i:]
                return

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        # Self-closing form (``<br />``); treat as a leaf.
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID_ELEMENTS:
            self.stack.pop()

    def handle_data(self, data: str) -> None:
        # Append text to the *currently open* element. Whitespace-only text
        # outside any element is ignored.
        if self.stack and data.strip():
            self.stack[-1].text += data


def walk(elem: Element):  # type: ignore[no-untyped-def]
    """
    Depth-first iterator over every descendant of ``elem`` (excluding the root).

    Parameters
    ----------
    elem : Element
        Root of the subtree to traverse.

    Yields
    ------
    Element
        Each descendant in document order.
    """
    for child in elem.children:
        yield child
        yield from walk(child)


def accessible_name(elem: Element) -> str:
    """
    Best-effort accessible name for an element.

    The function picks the first non-empty source from:

    1. ``aria-label`` (explicit override).
    2. ``title`` (tooltip fallback).
    3. Concatenated text content of the element AND every descendant.
       This is what a screen reader announces by default — the simple
       direct-text-only view misses the common ``<a><span>Label</span></a>``
       shape.

    Parameters
    ----------
    elem : Element
        Element under inspection.

    Returns
    -------
    str
        The accessible name, or ``""`` when none is present.
    """
    for attr in ("aria-label", "title"):
        if elem.attrs.get(attr, "").strip():
            return elem.attrs[attr].strip()

    # Aggregate text from this element and every descendant.
    parts: list[str] = [elem.text]
    parts.extend(d.text for d in walk(elem))
    return " ".join(p.strip() for p in parts if p and p.strip()).strip()


def has_descendant(elem: Element, tag: str) -> bool:
    """Return ``True`` when ``elem`` contains any descendant of ``tag``."""
    return any(d.tag == tag for d in walk(elem))


# ── Rule implementations ──────────────────────────────────────────────────

def check_html_lang(root: Element) -> list[Finding]:
    """Rule ``html-missing-lang`` — the ``<html>`` element must declare ``lang``."""
    findings: list[Finding] = []
    for elem in walk(root):
        if elem.tag == "html" and not elem.attrs.get("lang", "").strip():
            findings.append(Finding(
                rule="html-missing-lang",
                line=elem.line,
                message="<html> missing required lang attribute.",
            ))
    return findings


def check_img(root: Element) -> list[Finding]:
    """Rules ``img-missing-alt`` and ``img-redundant-aria``."""
    findings: list[Finding] = []
    for elem in walk(root):
        if elem.tag != "img":
            continue
        if "alt" not in elem.attrs:
            findings.append(Finding(
                rule="img-missing-alt",
                line=elem.line,
                message='<img> missing alt attribute. Use alt="" for decorative images.',
            ))
            continue
        # ``role="presentation"`` and ``aria-hidden`` are redundant with
        # an explicit empty ``alt`` per W3C / WAI guidance.
        if elem.attrs.get("alt", "") == "" and (
            elem.attrs.get("role", "") == "presentation"
            or elem.attrs.get("aria-hidden", "") == "true"
        ):
            findings.append(Finding(
                rule="img-redundant-aria",
                line=elem.line,
                message='Decorative <img alt="">: drop role="presentation" / aria-hidden="true" (redundant).',
            ))
    return findings


def check_links(root: Element) -> list[Finding]:
    """Rules ``a-missing-href`` and ``a-empty``."""
    findings: list[Finding] = []
    for elem in walk(root):
        if elem.tag != "a":
            continue
        # ``<a>`` without ``href`` is not a link — it has no role, no
        # keyboard handling. Use ``<button>``.
        if "href" not in elem.attrs:
            findings.append(Finding(
                rule="a-missing-href",
                line=elem.line,
                message="<a> without href is not a link. Use <button>.",
            ))
        # An empty link has no accessible name and no destination preview.
        if not accessible_name(elem) and not has_descendant(elem, "img"):
            findings.append(Finding(
                rule="a-empty",
                line=elem.line,
                message="<a> has no accessible name.",
            ))
    return findings


def check_buttons(root: Element) -> list[Finding]:
    """Rule ``button-empty``: every ``<button>`` needs an accessible name."""
    findings: list[Finding] = []
    for elem in walk(root):
        if elem.tag != "button":
            continue
        if not accessible_name(elem) and not has_descendant(elem, "img") and not has_descendant(elem, "svg"):
            findings.append(Finding(
                rule="button-empty",
                line=elem.line,
                message="<button> has no accessible name. Add text or aria-label.",
            ))
    return findings


def check_divspan_onclick(root: Element) -> list[Finding]:
    """Rule ``div-onclick``: ``<div>`` / ``<span>`` with ``onclick`` must be a button."""
    findings: list[Finding] = []
    for elem in walk(root):
        if elem.tag not in {"div", "span"}:
            continue
        if "onclick" not in elem.attrs:
            continue
        # If the author opted into ``role="button"`` and a ``tabindex``,
        # they've at least done the keyboard / AT plumbing. Still suboptimal
        # vs. a real <button> but not a violation worth flagging.
        if elem.attrs.get("role", "") == "button" and "tabindex" in elem.attrs:
            continue
        findings.append(Finding(
            rule="div-onclick",
            line=elem.line,
            message=f"<{elem.tag}> with onclick: prefer <button>, or add role=\"button\" + tabindex.",
        ))
    return findings


def check_input_label(root: Element) -> list[Finding]:
    """Rule ``input-missing-label``: every focusable ``<input>`` needs a label."""
    findings: list[Finding] = []
    # Collect every ``for=...`` so we can answer "is this input referenced?".
    referenced_ids: set[str] = set()
    for elem in walk(root):
        if elem.tag == "label" and elem.attrs.get("for", "").strip():
            referenced_ids.add(elem.attrs["for"].strip())

    for elem in walk(root):
        if elem.tag != "input":
            continue
        # Hidden / submit / button / image inputs don't need a label.
        if elem.attrs.get("type", "text").lower() in {
            "hidden", "submit", "button", "reset", "image",
        }:
            continue
        # A wrapped <label><input/></label> is fine — walk parents.
        wrapped: bool = False
        parent = elem.parent
        while parent is not None and parent.tag != "root":
            if parent.tag == "label":
                wrapped = True
                break
            parent = parent.parent

        if wrapped:
            continue
        if elem.attrs.get("id", "") in referenced_ids:
            continue
        if elem.attrs.get("aria-label", "").strip():
            continue
        findings.append(Finding(
            rule="input-missing-label",
            line=elem.line,
            message="<input> has no associated <label> and no aria-label.",
        ))
    return findings


def check_dialog_close(root: Element) -> list[Finding]:
    """Rule ``dialog-missing-close``: every ``<dialog>`` needs a way out."""
    findings: list[Finding] = []
    for elem in walk(root):
        if elem.tag != "dialog":
            continue
        # A close button with ``value="cancel"`` is the conventional pattern;
        # the browser closes the dialog when it's clicked.
        ok: bool = False
        for descendant in walk(elem):
            if descendant.tag == "button" and (
                descendant.attrs.get("value", "") in {"cancel", "close"}
                or "autofocus" in descendant.attrs
                or accessible_name(descendant).lower() in {
                    "close", "cancel", "fermer", "annuler", "schließen",
                }
            ):
                ok = True
                break
        if not ok:
            findings.append(Finding(
                rule="dialog-missing-close",
                line=elem.line,
                message="<dialog> has no obvious close affordance (button value=cancel / autofocus / 'Close' / 'Cancel').",
            ))
    return findings


def check_tabindex_positive(root: Element) -> list[Finding]:
    """Rule ``tabindex-positive``: ``tabindex`` ≥ 1 is an anti-pattern."""
    findings: list[Finding] = []
    for elem in walk(root):
        raw = elem.attrs.get("tabindex", "").strip()
        if not raw:
            continue
        try:
            value = int(raw)
        except ValueError:
            continue
        if value >= 1:
            findings.append(Finding(
                rule="tabindex-positive",
                line=elem.line,
                message=f"<{elem.tag} tabindex=\"{value}\">: positive tabindex breaks DOM order.",
            ))
    return findings


def check_aria_hidden_interactive(root: Element) -> list[Finding]:
    """Rule ``aria-hidden-interactive``: hidden interactive elements are unreachable."""
    findings: list[Finding] = []
    for elem in walk(root):
        if elem.tag not in {"button", "a", "input", "select", "textarea"}:
            continue
        if elem.attrs.get("aria-hidden", "") == "true":
            findings.append(Finding(
                rule="aria-hidden-interactive",
                line=elem.line,
                message=f'<{elem.tag} aria-hidden="true"> removes the control from AT.',
            ))
    return findings


HEADING_TAGS: tuple[str, ...] = ("h1", "h2", "h3", "h4", "h5", "h6")


def check_heading_order(root: Element) -> list[Finding]:
    """Rule ``heading-skip``: heading levels must not skip downward."""
    findings: list[Finding] = []
    previous: int = 0
    for elem in walk(root):
        if elem.tag not in HEADING_TAGS:
            continue
        current: int = HEADING_TAGS.index(elem.tag) + 1
        # Skipping *up* is fine (h3 → h2). Skipping *down* by more than one
        # is the anti-pattern (h2 → h4 skips h3).
        if previous and current > previous + 1:
            findings.append(Finding(
                rule="heading-skip",
                line=elem.line,
                message=f"<{elem.tag}> follows <h{previous}>: heading levels skip downward.",
            ))
        previous = current
    return findings


# Compiled patterns reused across calls.
_COLOR_STATE_PAT: re.Pattern[str] = re.compile(
    r"(?:text|bg|border|ring)-(?:red|green|emerald|rose|crimson)-\d+"
)
_MOTION_PAT: re.Pattern[str] = re.compile(
    r"\b(animate-(?:spin|ping|pulse|bounce)|transition-transform|transition-all)\b"
)
_MOTION_REDUCE_PAT: re.Pattern[str] = re.compile(r"motion-reduce:")


def check_color_only_state(root: Element) -> list[Finding]:
    """Rule ``color-only-state``: a red/green token alone is not a state cue."""
    findings: list[Finding] = []
    for elem in walk(root):
        cls: str = elem.attrs.get("class", "")
        if not _COLOR_STATE_PAT.search(cls):
            continue
        # Skip if the element has accompanying text or icon content; a state
        # banner with an icon + label is fine.
        if elem.text.strip():
            continue
        if has_descendant(elem, "svg") or has_descendant(elem, "img"):
            continue
        findings.append(Finding(
            rule="color-only-state",
            line=elem.line,
            message=f"<{elem.tag}> uses a red/green token but has no icon or text. State must not rely on color alone.",
        ))
    return findings


def check_motion_reduce(root: Element) -> list[Finding]:
    """Rule ``motion-no-reduce-guard``: animations need a reduced-motion peer."""
    findings: list[Finding] = []
    for elem in walk(root):
        cls: str = elem.attrs.get("class", "")
        if not _MOTION_PAT.search(cls):
            continue
        if _MOTION_REDUCE_PAT.search(cls):
            continue
        findings.append(Finding(
            rule="motion-no-reduce-guard",
            line=elem.line,
            message=f"<{elem.tag}> animates without a motion-reduce: peer (prefers-reduced-motion ignored).",
        ))
    return findings


# Registered rules — declaring them in a list makes ``--ignore`` cheap.
ALL_RULES: dict[str, callable] = {
    "html-missing-lang": check_html_lang,
    "img-missing-alt": check_img,
    "img-redundant-aria": check_img,
    "a-missing-href": check_links,
    "a-empty": check_links,
    "button-empty": check_buttons,
    "div-onclick": check_divspan_onclick,
    "input-missing-label": check_input_label,
    "dialog-missing-close": check_dialog_close,
    "tabindex-positive": check_tabindex_positive,
    "aria-hidden-interactive": check_aria_hidden_interactive,
    "heading-skip": check_heading_order,
    "color-only-state": check_color_only_state,
    "motion-no-reduce-guard": check_motion_reduce,
}


# ── Orchestration ────────────────────────────────────────────────────────

def lint_file(path: Path, ignored: set[str]) -> list[Finding]:
    """
    Run every enabled rule against one HTML file.

    Parameters
    ----------
    path : Path
        HTML file to lint.
    ignored : set of str
        Rule identifiers to suppress.

    Returns
    -------
    list of Finding
        All findings from the enabled rules, deduplicated by (rule, line).
    """
    html = path.read_text(encoding="utf-8", errors="ignore")
    parser = TreeBuilder()
    parser.feed(html)
    parser.close()

    findings: list[Finding] = []
    # Some rule functions emit two rule ids (e.g. ``check_img`` for missing
    # alt and redundant aria). Run each distinct rule function once and
    # then filter findings by the ignored set.
    seen: set[int] = set()
    for fn in {ALL_RULES[r] for r in ALL_RULES if r not in ignored}:
        if id(fn) in seen:
            continue
        seen.add(id(fn))
        for f in fn(parser.root):
            if f.rule in ignored:
                continue
            findings.append(f)

    # Stable order: by line, then by rule.
    findings.sort(key=lambda x: (x.line, x.rule))
    return findings


def collect_targets(target: Path) -> list[Path]:
    """
    Resolve ``target`` to a list of ``.html`` files to lint.

    Parameters
    ----------
    target : Path
        File or directory.

    Returns
    -------
    list of Path
        Every ``.html`` file at or under ``target``.
    """
    if target.is_file():
        return [target]
    return sorted(target.rglob("*.html"))


def main() -> int:
    """
    CLI entry point.

    Returns
    -------
    int
        ``0`` on no findings, ``1`` on any finding.
    """
    p = argparse.ArgumentParser(
        description="W3C/WAI accessibility linter for HTML emitted by the front skill.",
    )
    p.add_argument(
        "target", type=Path,
        help="HTML file or directory to lint.",
    )
    p.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format. Default: text.",
    )
    p.add_argument(
        "--ignore", default="",
        help="Comma-separated list of rule ids to skip.",
    )
    args = p.parse_args()

    ignored: set[str] = {r.strip() for r in args.ignore.split(",") if r.strip()}
    paths = collect_targets(args.target)
    if not paths:
        sys.stderr.write(f"No HTML files found under {args.target}\n")
        return 0

    total: int = 0
    failing_files: int = 0
    report: list[dict] = []
    for path in paths:
        findings = lint_file(path, ignored)
        if not findings:
            continue
        total += len(findings)
        failing_files += 1
        if args.format == "text":
            print(f"{path}:")
            for f in findings:
                print(f"  L{f.line:>4}  [{f.rule}] {f.message}")
        # ``report`` is populated in both formats so the JSON output has the
        # same coverage as the text output.
        report.append({
            "file": str(path),
            "findings": [
                {"rule": f.rule, "line": f.line, "message": f.message}
                for f in findings
            ],
        })

    if args.format == "json":
        json.dump({"findings_total": total, "files": report},
                  sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        print()
        if total == 0:
            print("0 findings.")
        else:
            print(f"{total} finding(s) across {failing_files} file(s).")

    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
