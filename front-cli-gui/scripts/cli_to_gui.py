#!/usr/bin/env python3
"""
cli_to_gui
==========

Introspect an :mod:`argparse` parser belonging to a Python CLI and
emit a single-page vanilla-JS + Tailwind GUI that maps every
sub-command and flag to a form field. Output follows the
``front-ui`` stack rules so the emitted file drops onto an internal
box, into Tauri's web view, or into a static-asset bucket without
modification.

This is the make-side primary of the ``front-cli-gui`` skill — the
counterpart to ``audit_laws_of_ux.py`` / ``palette_to_tailwind.py``
elsewhere in the front-* ecosystem. It is **not** a runtime: the
emitted page builds the command string locally and shows it for the
user to copy / paste / submit through the host adapter of their
choice (FastAPI SSE, Tauri ``invoke()``, Express, plain shell).

Why introspect, not parse ``--help``?
-------------------------------------

``--help`` text is a presentation format. Two CLIs with identical
behaviour can ship very different ``--help`` outputs depending on
formatter, line-wrap width and the author's stylistic choices.
:mod:`argparse`'s in-memory parser carries the **structured** truth:
sub-parser actions, choice lists, ``type=`` callables, ``required``
flags, ``nargs`` shapes, defaults. The HTML emitter consumes that
structured form so the same input always yields the same output.

Inputs
------

The caller names a parser factory as ``SPEC``:

- ``path/to/file.py:make_parser`` — load the file as an anonymous
  module, call ``make_parser()`` to obtain the parser.
- ``my_pkg.my_cli:build_parser`` — import the dotted module path,
  call the named factory.

The factory must be a zero-argument callable returning an
:class:`argparse.ArgumentParser`. (Click / Typer apps can expose a
factory wrapping ``cli.to_info_dict()`` or
``click.make_default_short_help``; the converter does not import
those frameworks itself.)

Outputs
-------

A single HTML file (stdout by default; ``--out PATH`` to write to
disk) containing:

- Tailwind Play CDN bootstrap + the three-Roboto webfont fallback.
- A sticky header with the parser's prog name + description.
- One collapsed ``<details>`` per sub-command (or a single form
  when no sub-command exists), with form fields mapped per action.
- A "Build command" button that constructs the CLI line and
  displays it in a ``<pre>`` block ready for copy / Tauri-invoke.
- Dark-mode peers on every styled element + focus rings + reduced
  motion guards (per the front-ui hard rules).

Stack rules respected
---------------------

- Vanilla JS only (ES module, no React / Vue / Svelte).
- Tailwind utility classes only; no raw hex in markup.
- Semantic HTML (``<form>``, ``<label for>``, ``<button>``,
  ``<details>``).
- Visible focus ring everywhere; ``prefers-reduced-motion`` honoured.
- No third-party CDN fonts — fallback to ``system-ui`` /
  ``ui-monospace`` when Roboto is not installed.

Usage
-----
::

    # Wrap a Python CLI exposing make_parser() in a single-file GUI
    python scripts/cli_to_gui.py path/to/cli.py:make_parser \\
        --out dist/index.html --title "My Tool"

    # Pipe to stdout for a quick preview
    python scripts/cli_to_gui.py mypkg.cli:build_parser

Author
------
`Warith Harchaoui, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import argparse
import html as html_lib
import importlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from _argparse import make_parser


# ── Loading the user's parser ──────────────────────────────────────────────


def load_parser_from_spec(spec: str) -> argparse.ArgumentParser:
    """
    Load a parser factory from a ``module:callable`` spec.

    Two forms are accepted, distinguished by whether the module part
    looks like a filesystem path:

    * ``"path/to/file.py:factory"`` — load the file as an anonymous
      module via :mod:`importlib.util`; works on any standalone
      script, no package install needed.
    * ``"dotted.module:factory"`` — :func:`importlib.import_module`;
      the module must be on ``sys.path`` (typically because the user
      ran from the repo root).

    Parameters
    ----------
    spec : str
        The ``"<module>:<factory>"`` string.

    Returns
    -------
    argparse.ArgumentParser
        The parser returned by ``factory()``. The function does *not*
        call ``parse_args`` — it consumes the parser by introspection
        only.

    Raises
    ------
    ValueError
        If ``spec`` does not contain a single ``:`` separator, or the
        factory returns something that is not an
        :class:`argparse.ArgumentParser`.
    """
    if ":" not in spec:
        raise ValueError(
            f"Spec '{spec}' must be of the form 'module:factory' "
            f"(e.g. 'path/to/cli.py:make_parser')."
        )
    mod_part, _, factory_name = spec.rpartition(":")
    # File-path form?
    if mod_part.endswith(".py") or "/" in mod_part or mod_part.startswith("./"):
        mod_path: Path = Path(mod_part).resolve()
        if not mod_path.is_file():
            raise FileNotFoundError(f"No such file: {mod_path}")
        spec_obj = importlib.util.spec_from_file_location(
            "_cli_to_gui_target", mod_path
        )
        if spec_obj is None or spec_obj.loader is None:
            raise ImportError(f"Could not load {mod_path} as a module")
        mod = importlib.util.module_from_spec(spec_obj)
        # Adding the file's parent dir to sys.path lets the target
        # script's own ``import`` statements resolve siblings.
        parent: str = str(mod_path.parent)
        if parent not in sys.path:
            sys.path.insert(0, parent)
        spec_obj.loader.exec_module(mod)
    else:
        mod = importlib.import_module(mod_part)
    factory = getattr(mod, factory_name, None)
    if factory is None:
        raise AttributeError(
            f"Module '{mod_part}' has no attribute '{factory_name}'."
        )
    parser_obj = factory()
    if not isinstance(parser_obj, argparse.ArgumentParser):
        raise ValueError(
            f"Factory '{spec}' returned a "
            f"{type(parser_obj).__name__}, not ArgumentParser."
        )
    return parser_obj


# ── Walking the parser tree ────────────────────────────────────────────────


#: Sentinel returned by :func:`_safe_default` for defaults we cannot
#: safely serialise to JSON. The HTML treats it as "no default
#: published" and leaves the form field empty.
NO_DEFAULT: object = object()


def _safe_default(default: Any) -> Any:
    """Return a JSON-serialisable representation of an argparse default."""
    if default is argparse.SUPPRESS or default is None:
        return None
    if isinstance(default, (str, int, float, bool)):
        return default
    if isinstance(default, (list, tuple)):
        return [_safe_default(d) for d in default]
    return str(default)


def _action_kind(a: argparse.Action) -> str:
    """
    Map an :class:`argparse.Action` to an HTML form-field kind string.

    Returns one of: ``"bool"``, ``"int"``, ``"float"``, ``"choice"``,
    ``"text"``, ``"file"`` (for actions whose ``type`` looks like
    :func:`open` / :class:`argparse.FileType`).
    """
    if isinstance(a, (argparse._StoreTrueAction, argparse._StoreFalseAction)):
        return "bool"
    if a.choices:
        return "choice"
    if a.type is None:
        return "text"
    if a.type is int:
        return "int"
    if a.type is float:
        return "float"
    if isinstance(a.type, argparse.FileType):
        return "file"
    # ``type=open`` or callable — render as text and let the user paste a path.
    return "text"


def serialize_action(a: argparse.Action) -> dict[str, Any]:
    """Project one :class:`argparse.Action` into a JSON-friendly dict."""
    return {
        "dest": a.dest,
        "flags": list(a.option_strings),
        "kind": _action_kind(a),
        "choices": list(a.choices) if a.choices else None,
        "required": bool(a.required),
        "default": _safe_default(a.default),
        "help": (a.help or "").strip(),
        "nargs": a.nargs if isinstance(a.nargs, (str, int)) else None,
        "metavar": (
            a.metavar
            if isinstance(a.metavar, str)
            else (a.metavar[0] if isinstance(a.metavar, tuple) else None)
        ),
    }


def walk_parser(parser: argparse.ArgumentParser) -> dict[str, Any]:
    """
    Walk an :class:`argparse.ArgumentParser` into a serialisable tree.

    The shape mirrors ``argparse`` itself: a ``prog`` / ``description``
    pair, a list of leaf actions, and a (possibly empty)
    ``sub_commands`` dict for any nested sub-parsers.

    Help / version actions are filtered out — they exist only on the
    CLI surface, not in a GUI.
    """
    actions: list[dict[str, Any]] = []
    sub_commands: dict[str, dict[str, Any]] = {}
    for a in parser._actions:
        if isinstance(a, argparse._SubParsersAction):
            for name, sub in a.choices.items():
                sub_commands[name] = walk_parser(sub)
        elif isinstance(a, (argparse._HelpAction,)) or a.dest == argparse.SUPPRESS:
            continue
        elif getattr(a, "version", None) is not None:
            # ``action="version"`` — version banner, not a user input.
            continue
        else:
            actions.append(serialize_action(a))
    return {
        "prog": parser.prog,
        "description": (parser.description or "").strip(),
        "actions": actions,
        "sub_commands": sub_commands,
    }


# ── HTML rendering ─────────────────────────────────────────────────────────


def _e(text: str) -> str:
    """Shorthand for :func:`html.escape` (HTML-attribute-safe)."""
    return html_lib.escape(text, quote=True)


def _field_html(action: dict[str, Any], prefix: str) -> str:
    """
    Render one form field for an :func:`serialize_action` dict.

    ``prefix`` is the sub-command path joined by ``"."`` (empty for
    the root parser). It is folded into the field ``id``/``name`` so
    the page can carry multiple sub-command forms without ID
    collisions.
    """
    flag: str = action["flags"][0] if action["flags"] else action["dest"]
    label_text: str = action["dest"].replace("_", " ")
    help_text: str = action.get("help") or ""
    field_id: str = f"{prefix}_{action['dest']}" if prefix else action["dest"]
    field_name: str = field_id

    required_marker: str = (
        ' <span class="text-brand-red" aria-hidden="true">*</span>'
        if action.get("required")
        else ""
    )
    help_block: str = (
        f'<p class="mt-1 text-[13px] text-label-secondary '
        f'dark:text-label-secondary-dark">{_e(help_text)}</p>'
        if help_text
        else ""
    )
    flag_block: str = (
        f'<span class="ml-2 font-mono text-[12px] text-label-secondary '
        f'dark:text-label-secondary-dark">{_e(flag)}</span>'
        if action["flags"]
        else ""
    )

    kind: str = action["kind"]
    default: Any = action.get("default")
    default_attr: str = (
        f' value="{_e(str(default))}"'
        if default not in (None, "", []) and kind != "bool"
        else ""
    )
    common_classes: str = (
        "mt-1 block w-full min-h-11 rounded-xl border border-separator "
        "bg-surface-secondary px-3 py-2 text-[15px] text-label-primary "
        "focus:outline-none focus-visible:ring-2 "
        "focus-visible:ring-brand-blue focus-visible:ring-offset-2 "
        "dark:border-separator-dark dark:bg-surface-secondary-dark "
        "dark:text-label-primary-dark"
    )

    if kind == "bool":
        checked: str = ' checked' if default is True else ""
        # ``min-h-11`` on the checkbox satisfies the front-ux-laws Fitts
        # heuristic (44 px hit area); ``focus-visible:ring-2`` satisfies
        # the Aesthetic-Usability heuristic. The visible checkbox stays
        # small via the ``h-5 w-5`` token; the label extends the click
        # area through the ``for`` attribute. We pad the field-wrapper
        # in the calling code so the row itself is ≥ 44 px tall.
        body: str = (
            f'<input id="{_e(field_id)}" name="{_e(field_name)}" '
            f'type="checkbox" data-cli-flag="{_e(flag)}" '
            f'class="mt-1 h-5 w-5 min-h-11 rounded border-separator '
            f'text-brand-blue focus:outline-none '
            f'focus-visible:ring-2 focus-visible:ring-brand-blue '
            f'focus-visible:ring-offset-2"{checked}>'
        )
    elif kind == "choice":
        opts: list[str] = []
        for c in action.get("choices") or []:
            sel: str = ' selected' if c == default else ""
            opts.append(
                f'<option value="{_e(str(c))}"{sel}>{_e(str(c))}</option>'
            )
        body = (
            f'<select id="{_e(field_id)}" name="{_e(field_name)}" '
            f'data-cli-flag="{_e(flag)}" class="{common_classes}">'
            f'{"".join(opts)}</select>'
        )
    elif kind in ("int", "float"):
        step: str = "1" if kind == "int" else "any"
        body = (
            f'<input id="{_e(field_id)}" name="{_e(field_name)}" '
            f'type="number" step="{step}" data-cli-flag="{_e(flag)}" '
            f'class="{common_classes}"{default_attr}>'
        )
    elif kind == "file":
        # File-type actions still render as text; the user pastes the
        # path. A real file picker lives in the host (Tauri's
        # ``dialog`` API, or HTTP upload).
        body = (
            f'<input id="{_e(field_id)}" name="{_e(field_name)}" '
            f'type="text" placeholder="path/to/file" '
            f'data-cli-flag="{_e(flag)}" '
            f'class="{common_classes}"{default_attr}>'
        )
    else:
        body = (
            f'<input id="{_e(field_id)}" name="{_e(field_name)}" '
            f'type="text" data-cli-flag="{_e(flag)}" '
            f'class="{common_classes}"{default_attr}>'
        )

    return (
        '<div class="mb-4">'
        f'<label for="{_e(field_id)}" class="block text-[14px] '
        'font-medium text-label-primary dark:text-label-primary-dark">'
        f'{_e(label_text)}{required_marker}{flag_block}</label>'
        f'{body}{help_block}</div>'
    )


def _form_html(node: dict[str, Any], path: list[str]) -> str:
    """Render one sub-command form (or the root form when path is empty)."""
    prefix: str = "_".join(path) if path else ""
    sub_command_id: str = (
        ".".join(path) if path else ""
    )
    fields: str = "\n".join(
        _field_html(a, prefix) for a in node["actions"]
    )
    if not fields:
        fields = (
            '<p class="text-[14px] text-label-secondary '
            'dark:text-label-secondary-dark">This sub-command takes '
            'no arguments.</p>'
        )
    desc: str = (
        f'<p class="mb-3 text-[14px] text-label-secondary '
        f'dark:text-label-secondary-dark">{_e(node["description"])}</p>'
        if node.get("description")
        else ""
    )
    return (
        f'<form data-cli-form data-subcommand="{_e(sub_command_id)}">'
        f'{desc}{fields}'
        f'<button type="button" data-cli-build class="mt-4 inline-flex '
        'min-h-11 items-center justify-center gap-2 rounded-full '
        'bg-brand-blue px-5 py-3 text-[15px] font-semibold text-white '
        'hover:opacity-90 active:scale-[0.97] '
        'focus:outline-none focus-visible:ring-2 '
        'focus-visible:ring-brand-blue focus-visible:ring-offset-2 '
        'motion-reduce:active:scale-100">Build command</button>'
        '</form>'
    )


def _children_html(node: dict[str, Any], path: list[str]) -> str:
    """Render nested sub-commands as collapsible ``<details>`` blocks."""
    parts: list[str] = []
    for name, child in node["sub_commands"].items():
        body: str = _form_html(child, path + [name])
        inner_sub: str = _children_html(child, path + [name])
        parts.append(
            '<details class="mt-3 rounded-2xl bg-surface-secondary p-4 '
            'dark:bg-surface-secondary-dark">'
            # ``min-h-11`` + ``focus-visible:ring-*`` keep front-ux-laws
            # happy on the disclosure-control element. ``cursor-pointer``
            # is intentional here — the agent's anti-pattern refusal
            # targets clickable ``<div>``/``<span>``, not real ``<summary>``.
            f'<summary class="flex min-h-11 cursor-pointer items-center '
            'text-[16px] font-semibold text-label-primary '
            'focus:outline-none focus-visible:ring-2 '
            'focus-visible:ring-brand-blue focus-visible:ring-offset-2 '
            'rounded-lg dark:text-label-primary-dark">'
            f'{_e(name)}</summary>'
            f'<div class="mt-3">{body}{inner_sub}</div>'
            '</details>'
        )
    return "".join(parts)


def render_html(tree: dict[str, Any], title: str = "CLI GUI") -> str:
    """
    Compose the full HTML document from a walked parser tree.

    Parameters
    ----------
    tree : dict
        Output of :func:`walk_parser`.
    title : str, default "CLI GUI"
        Page ``<title>``. The prog name appears in the visible header
        block regardless.

    Returns
    -------
    str
        A complete, single-file HTML document. ``\n``-terminated.
    """
    root_form: str = (
        _form_html(tree, [])
        if tree["actions"]
        else ""
    )
    sub_html: str = _children_html(tree, [])
    desc: str = (
        f'<p class="text-[14px] text-label-secondary '
        f'dark:text-label-secondary-dark">{_e(tree["description"])}</p>'
        if tree["description"]
        else ""
    )

    # The JS payload below is intentionally tiny: walk every form,
    # collect data-cli-flag inputs, assemble the command string,
    # render it into <pre id="cli-out">. The host adapter (Tauri /
    # FastAPI / shell) takes it from there.
    js_payload: str = """
const escape = (s) => {
  // Conservative shell quoting: wrap in single quotes and escape
  // embedded ones. Good enough for clipboard / display; the host
  // adapter is free to use a stricter quoter.
  if (s === '' || /[^A-Za-z0-9_./:=,@%+-]/.test(s)) {
    return "'" + s.replace(/'/g, "'\\\\''") + "'";
  }
  return s;
};

document.querySelectorAll('[data-cli-build]').forEach((btn) => {
  btn.addEventListener('click', (ev) => {
    const form = ev.currentTarget.closest('form');
    const sub = form.getAttribute('data-subcommand') || '';
    const parts = ['<<PROG>>'];
    if (sub) parts.push(...sub.split('.'));
    form.querySelectorAll('[data-cli-flag]').forEach((el) => {
      const flag = el.getAttribute('data-cli-flag');
      if (el.type === 'checkbox') {
        if (el.checked) parts.push(flag);
        return;
      }
      const value = (el.value || '').trim();
      if (!value) return;
      if (flag.startsWith('-')) parts.push(flag, escape(value));
      else parts.push(escape(value));
    });
    const out = parts.join(' ');
    const pre = document.getElementById('cli-out');
    pre.textContent = out;
    pre.scrollIntoView({behavior: 'smooth', block: 'nearest'});
  });
});
""".replace("<<PROG>>", tree["prog"])

    return (
        '<!doctype html>\n'
        '<html lang="en" data-color-scheme="auto">\n'
        '<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>{_e(title)}</title>\n'
        '<script src="https://cdn.tailwindcss.com"></script>\n'
        '<style>\n'
        '  :root { color-scheme: light dark; }\n'
        '  html, body { font-family: ui-sans-serif, system-ui, sans-serif; '
        'background-color: #FFFFFF; color: #000000; }\n'
        '  html.dark, html[data-color-scheme="dark"], '
        'html[data-color-scheme="dark"] body { background-color: #000000; '
        'color: #FFFFFF; }\n'
        '  *:focus { outline: none; }\n'
        '</style>\n'
        '</head>\n'
        '<body class="min-h-screen bg-white text-black dark:bg-black dark:text-white">\n'
        '<main class="mx-auto max-w-3xl px-4 py-8">\n'
        f'<header class="mb-6"><h1 class="text-[28px] font-semibold">{_e(tree["prog"])}</h1>{desc}</header>\n'
        f'{root_form}\n'
        f'{sub_html}\n'
        '<section class="mt-8">\n'
        '  <h2 class="text-[16px] font-semibold mb-2">Built command</h2>\n'
        '  <pre id="cli-out" class="rounded-2xl bg-surface-secondary p-4 '
        'font-mono text-[13px] text-label-primary dark:bg-surface-secondary-dark '
        'dark:text-label-primary-dark overflow-x-auto">'
        '(press Build command above)</pre>\n'
        '</section>\n'
        '<footer class="mt-8 text-[12px] text-label-secondary '
        'dark:text-label-secondary-dark">\n'
        '  Generated by front-cli-gui/scripts/cli_to_gui.py. '
        'Wire the Build command output to your host '
        '(Tauri invoke / FastAPI SSE / Express / shell).\n'
        '</footer>\n'
        '</main>\n'
        '<script type="module">\n'
        f'{js_payload}\n'
        '</script>\n'
        '</body>\n'
        '</html>\n'
    )


# ── CLI driver ─────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    """
    CLI entry point.

    Returns
    -------
    int
        ``0`` on success, ``1`` on a load failure, ``2`` on an
        argparse usage error (delegated to the parser).
    """
    parser: argparse.ArgumentParser = make_parser(
        prog="front-cli-gui-to-html",
        description=(
            "Introspect an argparse-based Python CLI and emit a "
            "single-page vanilla-JS + Tailwind GUI mapping every "
            "sub-command and flag to a form field. Make-side primary "
            "of the front-cli-gui skill — counterpart to the static "
            "scaffold in assets/examples/cli-gui-demo/."
        ),
    )
    parser.add_argument(
        "spec",
        help=(
            "Parser factory spec — 'path/to/cli.py:factory' OR "
            "'pkg.mod:factory'. The factory is a zero-argument "
            "callable returning an argparse.ArgumentParser."
        ),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help=(
            "Write the emitted HTML to this file instead of stdout. "
            "The parent directory must already exist."
        ),
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Page <title>. Defaults to the parser's prog name.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help=(
            "Emit the walked parser as JSON instead of HTML. Useful "
            "when debugging the introspection step or when piping "
            "into a different renderer (e.g. a Tauri app)."
        ),
    )
    args: argparse.Namespace = parser.parse_args(argv)

    try:
        cli_parser: argparse.ArgumentParser = load_parser_from_spec(args.spec)
    except (ValueError, FileNotFoundError, ImportError, AttributeError) as exc:
        print(f"cli_to_gui: {exc}", file=sys.stderr)
        return 1

    tree: dict[str, Any] = walk_parser(cli_parser)
    output: str = (
        json.dumps(tree, indent=2, ensure_ascii=False) + "\n"
        if args.json
        else render_html(tree, title=args.title or tree["prog"])
    )

    if args.out is None:
        sys.stdout.write(output)
        return 0
    try:
        args.out.write_text(output, encoding="utf-8")
    except OSError as exc:
        print(f"cli_to_gui: write failed: {exc}", file=sys.stderr)
        return 1
    print(f"cli_to_gui: wrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
