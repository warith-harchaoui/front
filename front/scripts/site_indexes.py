#!/usr/bin/env python3
"""
site_indexes
============

Generate the standard set of site-index files for a project's web output.

Always emitted
--------------

* **``robots.txt``** — controls crawler access; references the sitemap.
* **``sitemap.xml``** — per the sitemaps.org spec (XML 0.9 namespace).
* **``llms.txt``** — per https://llmstxt.org/. Title, summary, and a
  bullet list of important pages.

Conditional
-----------

* **``feed.atom``** — Atom 1.0 (RFC 4287). Emitted when a blog directory
  (``posts/`` or ``blog/``) is detected at the project root, or when
  ``--feed-from DIR`` is supplied. RSS 2.0 is available with ``--rss``
  for clients that haven't moved past 2002.
* **``humans.txt``** — per https://humanstxt.org/. Emitted only when
  ``--humans`` is passed or an ``AUTHORS`` / ``CREDITS`` file exists at
  the project root.

Specs honored
-------------
* robots.txt — Google Search Central:
  https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt
* Sitemap — https://www.sitemaps.org/protocol.html
* llms.txt — https://llmstxt.org/
* Atom 1.0 — RFC 4287 (https://datatracker.ietf.org/doc/html/rfc4287)
* RSS 2.0 — https://www.rssboard.org/rss-specification
* humans.txt — https://humanstxt.org/Standard.html

Usage
-----
::

    # Most common: emit the three always-on files
    python site_indexes.py --root . --base-url https://example.com

    # Project with a blog
    python site_indexes.py --root . --base-url https://example.com --feed-from posts

    # Force RSS 2.0 instead of Atom
    python site_indexes.py --root . --base-url https://example.com --feed-from posts --rss

    # Ship a humans.txt (will read AUTHORS / CREDITS if present)
    python site_indexes.py --root . --base-url https://example.com --humans

    # Choose a non-default output directory
    python site_indexes.py --root . --base-url https://example.com --out public

Notes
-----
* Python 3.9+, stdlib only.
* The script reads ``.html`` files at the project root and inside common
  output folders (``public/``, ``dist/``, ``site/``, ``_site/``,
  ``build/``) to populate sitemap and llms.txt. ``.md`` files at the
  root and under ``docs/`` are also included.

Author
------
`Warith Harchaoui, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
import xml.etree.ElementTree as ET
from email.utils import format_datetime
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import urljoin


# ── Module-level configuration ────────────────────────────────────────────────

#: Directories at the project root that may contain static HTML output.
WEB_OUTPUT_DIRS: tuple[str, ...] = ("public", "dist", "site", "_site", "build", "out")

#: Names recognized as a default blog folder when ``--feed-from`` is absent.
DEFAULT_BLOG_DIRS: tuple[str, ...] = ("posts", "blog", "articles")

#: Per-spec maximum number of URLs in a single sitemap. The sitemaps.org
#: protocol caps a single ``sitemap.xml`` at 50000 URLs / 50 MB; this
#: script does not split sitemaps because real-world projects emitting
#: more than 50000 pages need a dedicated tool.
SITEMAP_MAX_URLS: int = 50_000


# ── Utility helpers ────────────────────────────────────────────────────────

def _today_iso() -> str:
    """Return today's date as ISO-8601 (YYYY-MM-DD) in UTC."""
    return datetime.date.today().isoformat()


def _format_url(base_url: str, rel_path: Path) -> str:
    """
    Combine the base URL with a relative project path.

    Parameters
    ----------
    base_url : str
        Origin of the published site, with or without a trailing slash.
    rel_path : Path
        Path relative to the project root (or the output directory).

    Returns
    -------
    str
        Fully-qualified URL. ``index.html`` is collapsed to a directory URL.
    """
    posix: str = rel_path.as_posix()
    # Strip ``index.html`` suffix so the URL looks like ``/section/`` rather
    # than ``/section/index.html`` — what most servers serve and what
    # crawlers prefer.
    if posix.endswith("/index.html"):
        posix = posix[: -len("index.html")]
    elif posix == "index.html":
        posix = ""
    if not base_url.endswith("/"):
        base_url = base_url + "/"
    return urljoin(base_url, posix)


def _read_title(path: Path) -> str:
    """
    Extract a human-readable title from an HTML or Markdown page.

    Falls back to the file's stem when no title is found.

    Parameters
    ----------
    path : Path
        File to read.

    Returns
    -------
    str
        Title string.
    """
    text: str = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() in {".html", ".htm"}:
        m = re.search(r"<title>([^<]+)</title>", text, re.I)
        if m:
            return m.group(1).strip()
        m = re.search(r"<h1[^>]*>([^<]+)</h1>", text, re.I)
        if m:
            return re.sub(r"\s+", " ", m.group(1)).strip()
    else:
        # Markdown: first ATX-style heading.
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
    return path.stem.replace("-", " ").replace("_", " ").title()


def _read_description(path: Path) -> str:
    """
    Extract a one-sentence description from an HTML or Markdown page.

    Returns an empty string when no description is found. Used for
    llms.txt entries.
    """
    text: str = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() in {".html", ".htm"}:
        m = re.search(
            r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
            text, re.I,
        )
        if m:
            return m.group(1).strip()
        m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
                      text, re.I)
        if m:
            return m.group(1).strip()
        return ""
    # Markdown: first blockquote or first paragraph after the title.
    in_post_title: bool = False
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("# "):
            in_post_title = True
            continue
        if in_post_title:
            return line.lstrip("> ").strip()
    return ""


# ── Page discovery ────────────────────────────────────────────────────────

def discover_pages(root: Path) -> list[Path]:
    """
    Discover web-facing pages in the project tree.

    Walks the project root looking for ``.html`` files at the root and in
    the conventional output directories (:data:`WEB_OUTPUT_DIRS`), plus
    ``.md`` files at the root and under ``docs/``.

    Parameters
    ----------
    root : Path
        Project root.

    Returns
    -------
    list of Path
        Discovered files, in stable sorted order, paths relative to ``root``.
    """
    found: set[Path] = set()
    for pattern in ("*.html", "*.md"):
        for p in root.glob(pattern):
            if p.is_file():
                found.add(p.relative_to(root))
    for sub in WEB_OUTPUT_DIRS:
        d = root / sub
        if d.is_dir():
            for p in d.rglob("*.html"):
                found.add(p.relative_to(root))
    docs = root / "docs"
    if docs.is_dir():
        for p in docs.rglob("*.md"):
            found.add(p.relative_to(root))
    return sorted(found)


# ── robots.txt ────────────────────────────────────────────────────────────

def render_robots(base_url: str, sitemap_url: str) -> str:
    """
    Render a minimal robots.txt allowing all crawlers.

    Parameters
    ----------
    base_url : str
        Site origin (for context only — not embedded).
    sitemap_url : str
        Absolute URL of the sitemap to advertise.

    Returns
    -------
    str
        File body.
    """
    # A conservative default: allow everything, point crawlers at the sitemap.
    return (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {sitemap_url}\n"
    )


# ── sitemap.xml ───────────────────────────────────────────────────────────

def render_sitemap(base_url: str, pages: Iterable[tuple[Path, str]]) -> str:
    """
    Render a sitemap.xml document per sitemaps.org 0.9.

    Parameters
    ----------
    base_url : str
        Site origin.
    pages : iterable of (Path, str)
        ``(relative_path, lastmod_iso)`` tuples to include.

    Returns
    -------
    str
        XML document body.
    """
    SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
    urlset = ET.Element(f"{{{SITEMAP_NS}}}urlset")
    count: int = 0
    for rel, lastmod in pages:
        if count >= SITEMAP_MAX_URLS:
            break
        url = ET.SubElement(urlset, f"{{{SITEMAP_NS}}}url")
        ET.SubElement(url, f"{{{SITEMAP_NS}}}loc").text = _format_url(base_url, rel)
        if lastmod:
            ET.SubElement(url, f"{{{SITEMAP_NS}}}lastmod").text = lastmod
        count += 1
    # ``ET.tostring`` with ``xml_declaration=True`` emits the canonical
    # ``<?xml version="1.0" encoding="UTF-8"?>`` prologue.
    return ET.tostring(urlset, encoding="unicode", xml_declaration=True).rstrip() + "\n"


# ── llms.txt ──────────────────────────────────────────────────────────────

def render_llms_txt(
    base_url: str,
    project_name: str,
    summary: str,
    sections: dict[str, list[tuple[str, str, str]]],
) -> str:
    """
    Render an llms.txt file per https://llmstxt.org/.

    Parameters
    ----------
    base_url : str
        Site origin, used to fully qualify the links.
    project_name : str
        H1 title.
    summary : str
        Single-paragraph blockquote summary.
    sections : dict
        Map from H2 heading to a list of ``(name, url, description)``
        link entries. ``description`` may be empty.

    Returns
    -------
    str
        Markdown document body.
    """
    lines: list[str] = [f"# {project_name}", ""]
    if summary:
        lines.append(f"> {summary}")
        lines.append("")
    for heading, entries in sections.items():
        lines.append(f"## {heading}")
        lines.append("")
        for name, url, desc in entries:
            full = url if url.startswith(("http://", "https://")) else _format_url(base_url, Path(url))
            if desc:
                lines.append(f"- [{name}]({full}): {desc}")
            else:
                lines.append(f"- [{name}]({full})")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


# ── Atom feed ─────────────────────────────────────────────────────────────

def render_atom(
    base_url: str,
    feed_id: str,
    feed_title: str,
    posts: list[tuple[Path, str, str, str]],
) -> str:
    """
    Render an Atom 1.0 feed per RFC 4287.

    Parameters
    ----------
    base_url : str
        Site origin.
    feed_id : str
        Permanent feed URI (e.g. ``tag:example.com,2026:feed``).
    feed_title : str
        Human-readable feed title.
    posts : list of (Path, str, str, str)
        ``(relative_path, title, updated_iso, summary)`` per post, in
        reverse-chronological order.

    Returns
    -------
    str
        Atom XML document body.
    """
    ATOM_NS = "http://www.w3.org/2005/Atom"
    ET.register_namespace("", ATOM_NS)
    feed = ET.Element(f"{{{ATOM_NS}}}feed")
    ET.SubElement(feed, f"{{{ATOM_NS}}}title").text = feed_title
    ET.SubElement(feed, f"{{{ATOM_NS}}}id").text = feed_id

    link_self = ET.SubElement(feed, f"{{{ATOM_NS}}}link")
    link_self.set("rel", "self")
    link_self.set("href", _format_url(base_url, Path("feed.atom")))
    link_html = ET.SubElement(feed, f"{{{ATOM_NS}}}link")
    link_html.set("rel", "alternate")
    link_html.set("type", "text/html")
    link_html.set("href", base_url)

    # The feed-level ``<updated>`` mirrors the newest entry.
    feed_updated: str = posts[0][2] if posts else _today_iso() + "T00:00:00Z"
    ET.SubElement(feed, f"{{{ATOM_NS}}}updated").text = feed_updated

    for rel, title, updated, summary in posts:
        entry = ET.SubElement(feed, f"{{{ATOM_NS}}}entry")
        ET.SubElement(entry, f"{{{ATOM_NS}}}title").text = title
        post_url: str = _format_url(base_url, rel)
        ET.SubElement(entry, f"{{{ATOM_NS}}}id").text = post_url
        link = ET.SubElement(entry, f"{{{ATOM_NS}}}link")
        link.set("rel", "alternate")
        link.set("type", "text/html")
        link.set("href", post_url)
        ET.SubElement(entry, f"{{{ATOM_NS}}}updated").text = updated
        if summary:
            ET.SubElement(entry, f"{{{ATOM_NS}}}summary").text = summary

    return ET.tostring(feed, encoding="unicode", xml_declaration=True).rstrip() + "\n"


# ── RSS 2.0 feed (alternative output) ─────────────────────────────────────

def render_rss(
    base_url: str,
    feed_title: str,
    feed_description: str,
    posts: list[tuple[Path, str, str, str]],
) -> str:
    """
    Render an RSS 2.0 feed.

    Parameters
    ----------
    base_url : str
        Site origin.
    feed_title : str
        Channel title.
    feed_description : str
        Channel description.
    posts : list of (Path, str, str, str)
        ``(relative_path, title, updated_iso, summary)`` per post.

    Returns
    -------
    str
        RSS XML document body.
    """
    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = feed_title
    ET.SubElement(channel, "link").text = base_url
    ET.SubElement(channel, "description").text = feed_description
    if posts:
        # ``email.utils.format_datetime`` produces RFC 822 dates, which RSS
        # requires (not ISO-8601 like Atom).
        try:
            dt = datetime.datetime.fromisoformat(posts[0][2].replace("Z", "+00:00"))
            ET.SubElement(channel, "lastBuildDate").text = format_datetime(dt)
        except ValueError:
            pass

    for rel, title, updated, summary in posts:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = title
        link_url: str = _format_url(base_url, rel)
        ET.SubElement(item, "link").text = link_url
        ET.SubElement(item, "guid").text = link_url
        if summary:
            ET.SubElement(item, "description").text = summary
        try:
            dt = datetime.datetime.fromisoformat(updated.replace("Z", "+00:00"))
            ET.SubElement(item, "pubDate").text = format_datetime(dt)
        except ValueError:
            pass

    return ET.tostring(rss, encoding="unicode", xml_declaration=True).rstrip() + "\n"


# ── humans.txt ────────────────────────────────────────────────────────────

def render_humans(authors: list[str], site_meta: dict[str, str]) -> str:
    """
    Render a humans.txt file per humanstxt.org.

    Parameters
    ----------
    authors : list of str
        Author / contributor lines, e.g. ``"Warith Harchaoui - Author -
        warith@example.com - linkedin.com/in/warith-harchaoui"``.
    site_meta : dict
        Free-form key/value pairs for the ``/* SITE */`` section
        (``Last update``, ``Standards``, ``Components``, ``Software``).

    Returns
    -------
    str
        File body.
    """
    lines: list[str] = ["/* TEAM */", ""]
    if not authors:
        authors = ["Author -- see repository metadata."]
    lines.extend(authors)
    lines.append("")
    lines.append("/* SITE */")
    lines.append("")
    lines.append(f"Last update: {_today_iso()}")
    for key, value in site_meta.items():
        lines.append(f"{key}: {value}")
    lines.append("")
    return "\n".join(lines) + "\n"


def read_authors(root: Path) -> list[str]:
    """
    Read author lines from ``AUTHORS``, ``CREDITS``, or ``HUMANS`` files at
    the project root.

    Parameters
    ----------
    root : Path
        Project root.

    Returns
    -------
    list of str
        One non-empty line per author. Empty list when none of the files exist.
    """
    for name in ("AUTHORS", "AUTHORS.txt", "AUTHORS.md", "CREDITS", "CREDITS.txt", "HUMANS"):
        p = root / name
        if p.is_file():
            return [
                line.strip()
                for line in p.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.startswith("#")
            ]
    return []


# ── Blog-post discovery ────────────────────────────────────────────────────

def discover_posts(feed_dir: Path) -> list[tuple[Path, str, str, str]]:
    """
    Walk ``feed_dir`` and discover Markdown / HTML posts.

    Each post becomes a tuple ``(relative_path, title, updated_iso,
    summary)``. ``updated_iso`` is the file's mtime as an ISO-8601 UTC
    string.

    Parameters
    ----------
    feed_dir : Path
        Directory containing the blog posts.

    Returns
    -------
    list of tuple
        Posts in reverse-chronological order by mtime.
    """
    posts: list[tuple[Path, str, str, str]] = []
    for pattern in ("*.html", "*.md"):
        for p in feed_dir.rglob(pattern):
            if not p.is_file():
                continue
            # ``index.{html,md}`` at the feed root is the listing page; skip it.
            if p.name.lower() in {"index.html", "index.md"} and p.parent == feed_dir:
                continue
            stat = p.stat()
            updated = (
                datetime.datetime.fromtimestamp(stat.st_mtime, tz=datetime.timezone.utc)
                .isoformat(timespec="seconds")
                .replace("+00:00", "Z")
            )
            title = _read_title(p)
            summary = _read_description(p)
            posts.append((p, title, updated, summary))
    # Reverse chronological order — newest first.
    posts.sort(key=lambda x: x[2], reverse=True)
    # Convert paths to feed-relative for the renderer.
    rel_posts: list[tuple[Path, str, str, str]] = [
        (p[0].relative_to(feed_dir.parent), p[1], p[2], p[3]) for p in posts
    ]
    return rel_posts


# ── Orchestration ─────────────────────────────────────────────────────────

def find_blog_dir(root: Path, explicit: Optional[Path]) -> Optional[Path]:
    """
    Resolve the blog-posts directory.

    Parameters
    ----------
    root : Path
        Project root.
    explicit : Path or None
        Value of ``--feed-from`` (may be absolute or relative to ``root``).

    Returns
    -------
    Path or None
        Resolved directory, or ``None`` when no blog is detected.
    """
    if explicit is not None:
        candidate = explicit if explicit.is_absolute() else root / explicit
        return candidate if candidate.is_dir() else None
    for name in DEFAULT_BLOG_DIRS:
        candidate = root / name
        if candidate.is_dir():
            return candidate
    return None


def main() -> int:
    """CLI entry point. Writes the requested files into ``--out`` (default ``root``)."""
    p = argparse.ArgumentParser(
        description=__doc__.split("\n", 1)[0],
    )
    p.add_argument(
        "--root", type=Path, default=Path("."),
        help="Project root. Default: current directory.",
    )
    p.add_argument(
        "--base-url", required=True,
        help="Absolute origin of the published site (e.g. https://example.com).",
    )
    p.add_argument(
        "--out", type=Path,
        help="Output directory. Default: same as --root.",
    )
    p.add_argument(
        "--feed-from", type=Path, dest="feed_from",
        help="Directory containing blog posts. When omitted, posts/ or blog/ is auto-detected.",
    )
    p.add_argument(
        "--rss", action="store_true",
        help="Emit RSS 2.0 instead of Atom 1.0.",
    )
    p.add_argument(
        "--humans", action="store_true",
        help="Emit humans.txt (always reads AUTHORS / CREDITS when present).",
    )
    p.add_argument(
        "--name", default="",
        help="Project name. Falls back to the H1 / <title> of the root README / index.",
    )
    p.add_argument(
        "--summary", default="",
        help="Site summary used in llms.txt blockquote.",
    )
    args = p.parse_args()

    root: Path = args.root.resolve()
    out_dir: Path = (args.out or root).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    base_url: str = args.base_url.rstrip("/")

    # Project metadata: prefer the README's title; fall back to the folder name.
    project_name: str = args.name
    if not project_name:
        for candidate in ("README.md", "index.html", "index.md"):
            path = root / candidate
            if path.is_file():
                project_name = _read_title(path)
                break
    if not project_name:
        project_name = root.name

    # 1. robots.txt
    sitemap_url: str = _format_url(base_url + "/", Path("sitemap.xml"))
    (out_dir / "robots.txt").write_text(
        render_robots(base_url, sitemap_url),
        encoding="utf-8",
    )
    print(f"→ Wrote {out_dir / 'robots.txt'}")

    # 2. sitemap.xml
    pages: list[Path] = discover_pages(root)
    today: str = _today_iso()
    sitemap_pages: list[tuple[Path, str]] = [(p, today) for p in pages]
    (out_dir / "sitemap.xml").write_text(
        render_sitemap(base_url, sitemap_pages),
        encoding="utf-8",
    )
    print(f"→ Wrote {out_dir / 'sitemap.xml'} ({len(pages)} URL(s))")

    # 3. llms.txt
    sections: dict[str, list[tuple[str, str, str]]] = {"Pages": []}
    for page in pages:
        title = _read_title(root / page)
        desc = _read_description(root / page)
        sections["Pages"].append((title, page.as_posix(), desc))
    (out_dir / "llms.txt").write_text(
        render_llms_txt(base_url, project_name, args.summary, sections),
        encoding="utf-8",
    )
    print(f"→ Wrote {out_dir / 'llms.txt'}")

    # 4. Feed (conditional)
    feed_dir: Optional[Path] = find_blog_dir(root, args.feed_from)
    if feed_dir is not None:
        posts = discover_posts(feed_dir)
        if posts:
            if args.rss:
                body = render_rss(
                    base_url,
                    feed_title=project_name,
                    feed_description=args.summary or f"{project_name} feed",
                    posts=posts,
                )
                feed_path = out_dir / "rss.xml"
            else:
                feed_id = f"tag:{re.sub(r'^https?://', '', base_url)},{today}:feed"
                body = render_atom(
                    base_url,
                    feed_id=feed_id,
                    feed_title=project_name,
                    posts=posts,
                )
                feed_path = out_dir / "feed.atom"
            feed_path.write_text(body, encoding="utf-8")
            print(f"→ Wrote {feed_path} ({len(posts)} post(s))")
        else:
            print(f"→ No posts found in {feed_dir}; skipping feed.")

    # 5. humans.txt (opt-in or AUTHORS-driven)
    authors = read_authors(root)
    if args.humans or authors:
        site_meta: dict[str, str] = {
            "Language": "English",
            "Doctype": "HTML5",
            "Components": "vanilla JavaScript, Tailwind CSS, Montserrat",
        }
        (out_dir / "humans.txt").write_text(
            render_humans(authors, site_meta),
            encoding="utf-8",
        )
        print(f"→ Wrote {out_dir / 'humans.txt'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
