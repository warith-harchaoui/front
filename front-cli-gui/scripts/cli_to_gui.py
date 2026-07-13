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

Supported source frameworks
---------------------------

The emitter is **framework-agnostic** at the renderer boundary: a
small adapter protocol normalises every supported framework into a
canonical parser-tree dict (``prog`` / ``description`` / ``actions``
/ ``sub_commands``). Two adapters ship today:

- **argparse** (stdlib, always available). Walks
  :class:`argparse.ArgumentParser` via :func:`walk_parser`. Used
  when the factory returns an argparse parser.
- **Click** (optional dep). Walks :class:`click.Command` via
  :func:`walk_click`. Typer apps work via their underlying Click
  group (``app.cli``). Click is imported lazily so argparse-only
  users keep their stdlib-only run.

The renderer never branches on framework — :func:`walk` dispatches
by type and the HTML side sees a single shape. Adding a third
framework (Cobra via ``--from-help``, clap, …) is a new adapter +
the same dict; the renderer never moves.

Why introspect, not parse ``--help``?
-------------------------------------

``--help`` text is a presentation format — fragile under
formatter / line-wrap / locale variation. An in-memory parser
carries the **structured** truth (choice lists, ``type=`` callables,
``required`` flags, defaults). When the framework is reachable,
prefer introspection. For non-Python binaries (clap / cobra /
commander) or when the parser cannot be imported, the planned
``--from-help`` adapter parses the help text as a low-fidelity
fallback (everything maps to ``"text"`` unless ``[default: …]`` or
similar is visible).

Inputs
------

The caller names a parser factory as ``SPEC``:

- ``path/to/file.py:make_parser`` — load the file as an anonymous
  module, call ``make_parser()`` to obtain the parser.
- ``my_pkg.my_cli:build_parser`` — import the dotted module path,
  call the named factory.

The factory must be a zero-argument callable returning EITHER an
:class:`argparse.ArgumentParser` OR a :class:`click.Command`
(Click Group or Command). Adapter selection is automatic.

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
import re
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
    # Adapter dispatch (see :func:`walk`): an argparse.ArgumentParser
    # or any Click BaseCommand counts. Anything else is rejected with
    # an actionable error message — we name both frameworks the
    # adapter understands so the user knows what to return.
    if isinstance(parser_obj, argparse.ArgumentParser):
        return parser_obj
    # Click is an optional dependency. We import it lazily so the
    # ``language: python`` pre-commit hook + minimal CI runners that
    # only target argparse keep working without Click on the path.
    try:
        import click  # noqa: WPS433  (lazy by design)
    except ImportError:
        click = None  # type: ignore[assignment]
    if click is not None and isinstance(parser_obj, click.Command):
        return parser_obj
    raise ValueError(
        f"Factory '{spec}' returned a "
        f"{type(parser_obj).__name__}; expected argparse.ArgumentParser "
        f"or click.Command (install click if your factory returns "
        f"a Click app)."
    )


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

    See also :func:`walk` for the framework-agnostic entry point that
    dispatches between this and :func:`walk_click`.
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


# ── Click adapter ──────────────────────────────────────────────────────────


def _click_param_kind(param: Any) -> str:
    """
    Map a :class:`click.Parameter` to a form-field kind string.

    Mirrors :func:`_action_kind` but reads from Click's structured
    ``param.type`` / ``param.is_flag`` / ``param.multiple`` attributes
    instead of argparse's heuristic ``type=`` callable.

    Parameters
    ----------
    param : click.Parameter
        The Click parameter (an ``Option`` or ``Argument``).

    Returns
    -------
    str
        One of ``"bool"``, ``"int"``, ``"float"``, ``"choice"``,
        ``"file"``, ``"text"``.
    """
    # ``is_flag=True`` is Click's idiomatic boolean switch (parallel
    # to argparse's ``store_true`` / ``store_false``).
    if getattr(param, "is_flag", False):
        return "bool"
    # ``count=True`` increments an int per repetition (``-vvv``). We
    # render it as an integer field — the GUI cannot reasonably ask
    # the user to "click v three times".
    if getattr(param, "count", False):
        return "int"
    # ``click.types.*`` are concrete instances on ``param.type``. We
    # inspect the type's ``name`` so we do not need to import the
    # ``click.types`` symbols at module load (Click is optional).
    type_name: str = getattr(param.type, "name", "") or ""
    if type_name == "boolean":
        return "bool"
    if type_name in ("integer", "integer range"):
        return "int"
    if type_name in ("float", "float range"):
        return "float"
    if type_name == "choice":
        return "choice"
    if type_name in ("path", "filename", "file"):
        return "file"
    return "text"


def _click_param_choices(param: Any) -> list[str] | None:
    """Extract the choices list from a ``click.Choice`` param if present."""
    type_name: str = getattr(param.type, "name", "") or ""
    if type_name != "choice":
        return None
    choices: Any = getattr(param.type, "choices", None)
    if choices is None:
        return None
    return [str(c) for c in choices]


def _serialize_click_param(param: Any) -> dict[str, Any]:
    """
    Project one :class:`click.Parameter` into the canonical action dict.

    The output schema is identical to :func:`serialize_action` —
    ``dest``, ``flags``, ``kind``, ``choices``, ``required``,
    ``default``, ``help``, ``nargs``, ``metavar`` — so the HTML
    renderer never has to branch on the source framework.
    """
    # ``opts`` is the list of ``--flag`` strings for Options;
    # Arguments have no opts (positional).
    flags: list[str] = list(getattr(param, "opts", []) or [])
    # ``default`` is sometimes a callable (Click resolves it lazily).
    # We materialise + safe-serialise so the HTML emitter sees a
    # value it can write into ``value="…"``.
    default: Any = getattr(param, "default", None)
    if callable(default):
        try:
            default = default()
        except Exception:  # noqa: BLE001 — best-effort; fall back to None.
            default = None
    # Click 8.2+ uses a sentinel value (``click.core.Sentinel.UNSET``
    # or similar) for parameters with no explicit default; treat it
    # as "no default" so the HTML emitter does not stamp a literal
    # ``Sentinel.UNSET`` into the form's ``value="…"`` attribute.
    if default is not None and "Sentinel" in type(default).__name__:
        default = None
    return {
        "dest": param.name,
        "flags": flags,
        "kind": _click_param_kind(param),
        "choices": _click_param_choices(param),
        "required": bool(getattr(param, "required", False)),
        "default": _safe_default(default),
        "help": (getattr(param, "help", "") or "").strip(),
        # Click uses ``nargs=-1`` for "any number"; argparse uses "*".
        # We surface Click's int directly so the HTML side can decide.
        "nargs": getattr(param, "nargs", None),
        "metavar": getattr(param, "metavar", None),
    }


def walk_click(cmd: Any, prog: str | None = None) -> dict[str, Any]:
    """
    Walk a :class:`click.Command` into the canonical parser tree.

    Mirrors :func:`walk_parser` exactly — same dict shape — so the
    HTML renderer never branches on the source framework. Handles
    both leaf ``Command`` and nested ``Group`` trees; ``--help`` is
    filtered (Click adds it automatically and it has no GUI value).

    Parameters
    ----------
    cmd : click.Command
        A Click command or group. Typer apps expose their underlying
        Click group via ``app.cli`` — pass that.
    prog : str or None, optional
        Override the ``prog`` field. Defaults to the command's own
        ``name`` (Click sets this from the function name).

    Returns
    -------
    dict
        The canonical parser tree.
    """
    actions: list[dict[str, Any]] = []
    sub_commands: dict[str, dict[str, Any]] = {}
    # ``cmd.params`` are the leaf options / arguments.
    for param in getattr(cmd, "params", []) or []:
        # Click sometimes emits an ``HelpOption`` automatically; we
        # detect it via ``param.is_eager`` + an empty ``name``-shape.
        name: str | None = getattr(param, "name", None)
        if not name or name == "help":
            continue
        actions.append(_serialize_click_param(param))
    # ``Group.commands`` is a dict of sub-commands. Leaf ``Command``
    # objects do not have ``commands``.
    subs: dict[str, Any] = getattr(cmd, "commands", {}) or {}
    for name, sub in subs.items():
        sub_commands[name] = walk_click(sub, prog=name)
    return {
        "prog": prog or getattr(cmd, "name", "cli") or "cli",
        "description": (getattr(cmd, "help", "") or "").strip(),
        "actions": actions,
        "sub_commands": sub_commands,
    }


# ── --from-help adapter (framework-agnostic) ───────────────────────────────


#: Subprocess timeout (seconds) for the ``--help`` invocation. Long
#: enough for a slow JIT-warm CLI, short enough that a hanging
#: subprocess does not freeze the GUI generator.
HELP_TIMEOUT_S: float = 10.0


#: Section headers we recognise. Most CLI conventions converge on
#: these — argparse, Click, clap (Rust), cobra (Go), commander (Node)
#: all use some variation. We match case-insensitively + tolerate the
#: trailing-colon-and-optional-newline shape.
RE_OPTIONS_HEADER: re.Pattern[str] = re.compile(
    r"^\s*(options|optional arguments|flags):\s*$",
    re.IGNORECASE | re.MULTILINE,
)
RE_COMMANDS_HEADER: re.Pattern[str] = re.compile(
    r"^\s*(commands|sub-?commands|available commands):\s*$",
    re.IGNORECASE | re.MULTILINE,
)
RE_USAGE_HEADER: re.Pattern[str] = re.compile(
    r"^\s*usage:\s*(.+)$",
    re.IGNORECASE | re.MULTILINE,
)
RE_POSITIONAL_HEADER: re.Pattern[str] = re.compile(
    r"^\s*(positional arguments|arguments):\s*$",
    re.IGNORECASE | re.MULTILINE,
)

#: Line shape for one option entry: leading whitespace, one or more
#: ``-flag`` tokens (optionally with a comma-list and an inline
#: METAVAR), then 2+ whitespace and the help text.
#:
#: Permissive on purpose — argparse, Click, clap, cobra, commander
#: each format option lines slightly differently and we want all of
#: them to land in the same parse. The flag-token split happens
#: after the match, in :func:`_parse_option_line`.
#:
#: Captures:
#:   1. flags-and-metavar fragment (e.g. ``"-V, --version"``,
#:      ``"--input PATH"``, ``"--format [mp3|ogg|flac]"``)
#:   2. inline help text (may be empty when help is on the next line)
RE_OPTION_LINE: re.Pattern[str] = re.compile(
    r"^\s{2,}(-{1,2}[^\s,]+(?:,\s*-{1,2}[^\s,]+)*"
    r"(?:\s[^\s]+)?)"
    r"(?:\s{2,}(.*))?$"
)

#: One sub-command row: leading whitespace, the slug, two-or-more
#: spaces, the help fragment.
RE_COMMAND_LINE: re.Pattern[str] = re.compile(
    r"^\s{2,}([a-z0-9][a-z0-9_-]*)(?:\s{2,}(.*))?$",
    re.IGNORECASE,
)

#: ``[default: 128]`` / ``[default=128]`` / ``(default: 128)`` —
#: extracts the literal default the help text advertised.
RE_DEFAULT_HINT: re.Pattern[str] = re.compile(
    r"[\[\(]default[:= ]\s*([^\]\)]+)[\]\)]",
    re.IGNORECASE,
)
RE_REQUIRED_HINT: re.Pattern[str] = re.compile(
    r"\[required\]|\(required\)",
    re.IGNORECASE,
)
#: ``[mp3|ogg|flac]`` or ``{mp3,ogg,flac}`` — Click vs argparse styles.
RE_CHOICE_HINT: re.Pattern[str] = re.compile(
    r"\[([^\[\]]+\|[^\[\]]+)\]|\{([^{}]+,[^{}]+)\}"
)


def _run_help(cmdline: str) -> str:
    """
    Run ``<cmdline> --help`` and return its stdout.

    Parameters
    ----------
    cmdline : str
        The command to introspect, as a shell string. Split on
        whitespace; we never invoke the shell itself to keep
        injection surface narrow.

    Returns
    -------
    str
        Captured stdout. Stderr is folded in too because some CLIs
        (notably older argparse) write help to stderr.

    Raises
    ------
    FileNotFoundError
        If the command does not resolve on ``$PATH``.
    subprocess.TimeoutExpired
        If ``--help`` does not return within
        :data:`HELP_TIMEOUT_S` seconds.
    """
    import shlex
    import subprocess as sp

    parts: list[str] = shlex.split(cmdline) + ["--help"]
    proc = sp.run(
        parts,
        capture_output=True,
        text=True,
        timeout=HELP_TIMEOUT_S,
        check=False,
    )
    # Many CLIs exit non-zero on ``--help`` (notably tools that
    # treat help as "no real command was named"). Trust the output,
    # not the exit code.
    return proc.stdout + ("\n" + proc.stderr if proc.stderr else "")


def _extract_prog(cmdline: str, help_text: str = "") -> str:
    """
    Best-effort program name.

    Prefers the ``usage: <prog> …`` line in the help output (the CLI's
    own opinion of its prog name); falls back to the basename of the
    first shell token. Shell wrappers like ``python3 myscript.py`` get
    correctly identified by the usage line as ``myscript``, not
    ``python3``.
    """
    if help_text:
        m = RE_USAGE_HEADER.search(help_text)
        if m:
            usage_line: str = m.group(1).strip()
            first_token: str = usage_line.split()[0] if usage_line else ""
            if first_token:
                return first_token
    import shlex
    parts: list[str] = shlex.split(cmdline) if cmdline else []
    # Skip leading interpreter / wrapper tokens to land on the real
    # script name when invoked as ``python3 path/to/script.py``.
    for token in parts:
        name: str = Path(token).name
        if name and not name.startswith("-") and name not in {
            "python", "python3", "python2", "uvx", "uv", "npx", "node",
            "ruby", "perl", "bash", "sh",
        }:
            # Strip a ``.py`` / ``.js`` / ``.rb`` extension so the GUI
            # title is the conventional command name.
            return Path(name).stem or name
    return (parts[0] if parts else "cli")


#: argparse-style sub-command list: ``{cmd1,cmd2,cmd3}`` on a single
#: indented line under ``positional arguments:``.
RE_ARGPARSE_SUBS: re.Pattern[str] = re.compile(
    r"^\s{2,}\{([a-z0-9][a-z0-9_,-]*)\}\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def _section(text: str, header_re: re.Pattern[str]) -> str | None:
    """
    Return the lines between ``header_re`` and the next blank line.

    Returns ``None`` if the section is not present in ``text``.
    The slice ends at the first line that does not start with two
    or more spaces — that is how argparse / Click visually delimit
    one section from the next.
    """
    m = header_re.search(text)
    if not m:
        return None
    start: int = m.end()
    # Walk forward line by line until we hit a non-indented line.
    lines: list[str] = text[start:].splitlines()
    out: list[str] = []
    for line in lines:
        if not line.strip():
            # A blank line is permitted *between* entries; we keep
            # going until two consecutive blanks OR an outdented line.
            out.append(line)
            continue
        if not line.startswith(" "):
            break
        out.append(line)
    return "\n".join(out)


def _parse_option_line(
    line: str, help_continuation: str = ""
) -> dict[str, Any] | None:
    """Project one help-text option line into the canonical action dict."""
    m = RE_OPTION_LINE.match(line)
    if not m:
        return None
    flags_fragment: str = m.group(1).strip()
    inline_help: str = (m.group(2) or "").strip()
    full_help: str = (inline_help + " " + help_continuation).strip()

    # Split ``"-V, --version"`` → ``["-V", "--version"]``.
    flag_tokens: list[str] = []
    for piece in flags_fragment.split(","):
        token: str = piece.strip().split()[0] if piece.strip() else ""
        if token.startswith("-"):
            flag_tokens.append(token)
    if not flag_tokens:
        return None
    if any(t in ("-h", "--help") for t in flag_tokens):
        return None  # filter the omnipresent help line

    # ``--input PATH`` → metavar = "PATH". Lower-cased becomes our
    # candidate dest. If no metavar is present, fall back to the
    # longest flag with its leading dashes stripped.
    metavar: str | None = None
    after_flags: str = flags_fragment.split()[-1] if " " in flags_fragment else ""
    if (
        after_flags
        and not after_flags.startswith("-")
        and after_flags not in flag_tokens
    ):
        metavar = after_flags.rstrip("]").lstrip("[<(")

    longest: str = max(flag_tokens, key=len)
    dest: str = longest.lstrip("-").replace("-", "_")

    # Heuristic kind detection from help text + metavar.
    kind: str = "text"
    if metavar and metavar.upper() in ("INTEGER", "INT", "N"):
        kind = "int"
    elif metavar and metavar.upper() in ("FLOAT", "NUMBER"):
        kind = "float"
    elif metavar and metavar.upper() in ("PATH", "FILE", "FILENAME", "DIR"):
        kind = "file"
    elif not metavar:
        # No metavar usually means a boolean flag.
        kind = "bool"

    # Choices: ``[mp3|ogg|flac]`` or ``{mp3,ogg,flac}``.
    choices: list[str] | None = None
    cm = RE_CHOICE_HINT.search(flags_fragment + " " + full_help)
    if cm:
        raw: str = cm.group(1) or cm.group(2) or ""
        sep: str = "|" if "|" in raw else ","
        choices = [c.strip() for c in raw.split(sep) if c.strip()]
        if choices:
            kind = "choice"

    # Default: ``[default: 128]`` (Click) or ``(default: 128)`` (argparse).
    default: Any = None
    dm = RE_DEFAULT_HINT.search(full_help)
    if dm:
        raw_default: str = dm.group(1).strip()
        # Try int / float, fall back to string.
        try:
            default = int(raw_default)
        except ValueError:
            try:
                default = float(raw_default)
            except ValueError:
                default = raw_default

    required: bool = bool(RE_REQUIRED_HINT.search(full_help))

    return {
        "dest": dest,
        "flags": flag_tokens,
        "kind": kind,
        "choices": choices,
        "required": required,
        "default": default,
        "help": full_help,
        "nargs": None,
        "metavar": metavar,
    }


def _parse_options_section(section: str | None) -> list[dict[str, Any]]:
    """Walk an options section and produce one action dict per entry."""
    if not section:
        return []
    out: list[dict[str, Any]] = []
    pending_line: str | None = None
    for line in section.splitlines():
        if not line.strip():
            if pending_line is not None:
                parsed = _parse_option_line(pending_line)
                if parsed:
                    out.append(parsed)
                pending_line = None
            continue
        # An indented line that does NOT start with ``-`` (under deep
        # indent) is a help-text continuation for the previous option.
        stripped: str = line.lstrip()
        if pending_line is not None and not stripped.startswith("-"):
            # Fold continuation into the previous parse.
            parsed_prev = _parse_option_line(pending_line, stripped)
            if parsed_prev:
                out.append(parsed_prev)
            pending_line = None
            continue
        if pending_line is not None:
            parsed = _parse_option_line(pending_line)
            if parsed:
                out.append(parsed)
        pending_line = line
    if pending_line is not None:
        parsed = _parse_option_line(pending_line)
        if parsed:
            out.append(parsed)
    return out


def _parse_commands_section(section: str | None) -> list[tuple[str, str]]:
    """Yield (sub_command_name, short_help) from a Commands section."""
    if not section:
        return []
    out: list[tuple[str, str]] = []
    for line in section.splitlines():
        m = RE_COMMAND_LINE.match(line)
        if not m:
            continue
        name: str = m.group(1)
        help_text: str = (m.group(2) or "").strip()
        # Reject false matches that look like option lines.
        if name.startswith("-"):
            continue
        out.append((name, help_text))
    return out


def walk_from_help(
    cmdline: str,
    *,
    _depth: int = 0,
    _max_depth: int = 3,
) -> dict[str, Any]:
    """
    Parse ``<cmdline> --help`` into the canonical parser tree.

    Works on any CLI that emits a conventional help block:
    argparse, Click, Typer, clap (Rust), cobra (Go), commander
    (Node), even hand-rolled shell scripts that follow the
    standard sections. Lower fidelity than native introspection
    (everything maps to ``"text"`` unless a ``[default: …]``,
    ``[choices]`` or recognised METAVAR is visible).

    Parameters
    ----------
    cmdline : str
        The command to introspect (passed through :mod:`shlex.split`
        — never via the shell, to keep the injection surface narrow).
    _depth : int, default 0
        Internal — current recursion depth into sub-commands.
    _max_depth : int, default 3
        Internal — stop recursing into sub-commands past this many
        levels. Defends against pathological CLIs whose sub-command
        list includes itself.

    Returns
    -------
    dict
        Canonical parser tree.
    """
    help_text: str = _run_help(cmdline)
    description: str = ""
    usage_match = RE_USAGE_HEADER.search(help_text)
    if usage_match:
        # Treat any prose between the Usage block and the first
        # ``Options:`` / ``Commands:`` header as the description.
        after_usage: int = usage_match.end()
        next_header = min(
            (m.start() for m in [
                RE_OPTIONS_HEADER.search(help_text, after_usage),
                RE_COMMANDS_HEADER.search(help_text, after_usage),
                RE_POSITIONAL_HEADER.search(help_text, after_usage),
            ] if m is not None),
            default=len(help_text),
        )
        description = help_text[after_usage:next_header].strip()

    options: list[dict[str, Any]] = _parse_options_section(
        _section(help_text, RE_OPTIONS_HEADER)
    )
    positionals: list[dict[str, Any]] = _parse_options_section(
        _section(help_text, RE_POSITIONAL_HEADER)
    )
    commands_raw: list[tuple[str, str]] = _parse_commands_section(
        _section(help_text, RE_COMMANDS_HEADER)
    )
    # argparse uses ``positional arguments:`` + a ``{cmd1,cmd2}`` line
    # to list sub-commands. Detect that shape and fold its entries
    # into the same sub_commands recursion.
    for m in RE_ARGPARSE_SUBS.finditer(help_text):
        for name in m.group(1).split(","):
            name = name.strip()
            if name and not any(c[0] == name for c in commands_raw):
                commands_raw.append((name, ""))

    sub_commands: dict[str, dict[str, Any]] = {}
    if _depth < _max_depth:
        for name, _ in commands_raw:
            try:
                sub_commands[name] = walk_from_help(
                    f"{cmdline} {name}",
                    _depth=_depth + 1,
                    _max_depth=_max_depth,
                )
            except (FileNotFoundError, OSError):
                # The sub-command exists in the help text but cannot
                # be invoked. Skip rather than abort the whole walk.
                continue
            except Exception:  # noqa: BLE001 — best-effort.
                continue

    return {
        "prog": _extract_prog(cmdline, help_text),
        "description": description,
        "actions": options + positionals,
        "sub_commands": sub_commands,
    }


# ── Public dispatch ────────────────────────────────────────────────────────


def walk(obj: Any) -> dict[str, Any]:
    """
    Walk a CLI object (argparse or Click) into the canonical tree.

    Single entry point for the HTML renderer — it does not need to
    know which framework produced the input.

    Parameters
    ----------
    obj : argparse.ArgumentParser or click.Command
        The CLI to introspect.

    Returns
    -------
    dict
        Canonical parser tree (``prog``, ``description``, ``actions``,
        ``sub_commands``).

    Raises
    ------
    TypeError
        If ``obj`` is neither an argparse parser nor a Click command.
    """
    if isinstance(obj, argparse.ArgumentParser):
        return walk_parser(obj)
    # Click is optional; only attempt the isinstance check after a
    # successful lazy import. Skipping the import on argparse-only
    # users keeps the script stdlib-only at run time.
    try:
        import click  # noqa: WPS433
    except ImportError:
        click = None  # type: ignore[assignment]
    if click is not None and isinstance(obj, click.Command):
        return walk_click(obj)
    raise TypeError(
        f"walk() expected argparse.ArgumentParser or click.Command, "
        f"got {type(obj).__name__}"
    )


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
            "Introspect a Python CLI (argparse OR Click — autodetected) "
            "and emit a single-page vanilla-JS + Tailwind GUI mapping "
            "every sub-command and flag to a form field. Make-side "
            "primary of the front-cli-gui skill — counterpart to the "
            "static scaffold in assets/examples/cli-gui-demo/."
        ),
    )
    parser.add_argument(
        "spec",
        help=(
            "Parser factory spec — 'path/to/cli.py:factory' OR "
            "'pkg.mod:factory'. The factory is a zero-argument "
            "callable returning EITHER an argparse.ArgumentParser "
            "OR a click.Command (Group or Command). Adapter is "
            "auto-selected from the returned type. With "
            "``--from-help``, this argument is a shell command line "
            "instead; its '--help' output is parsed. Works on any "
            "CLI — Python or not, framework-agnostic — at lower "
            "fidelity than native introspection."
        ),
    )
    parser.add_argument(
        "--from-help",
        action="store_true",
        dest="from_help",
        help=(
            "Treat 'spec' as a shell command line; run "
            "'<command> --help' via subprocess and parse the output "
            "into the canonical parser tree. Works on non-Python "
            "CLIs (clap / cobra / commander) and on Python CLIs "
            "whose factory cannot be imported. Lower fidelity — "
            "everything maps to 'text' unless [default: …], "
            "[choices] or a recognised METAVAR is visible."
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

    tree: dict[str, Any]
    if args.from_help:
        # ``--from-help``: subprocess-based path. ``spec`` is a shell
        # command line, not a module:factory string.
        try:
            tree = walk_from_help(args.spec)
        except (FileNotFoundError, OSError) as exc:
            print(f"cli_to_gui: --from-help failed: {exc}", file=sys.stderr)
            return 1
    else:
        try:
            cli_obj: Any = load_parser_from_spec(args.spec)
        except (ValueError, FileNotFoundError, ImportError, AttributeError) as exc:
            print(f"cli_to_gui: {exc}", file=sys.stderr)
            return 1
        try:
            tree = walk(cli_obj)
        except TypeError as exc:
            print(f"cli_to_gui: {exc}", file=sys.stderr)
            return 1
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
