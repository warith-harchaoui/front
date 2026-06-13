#!/usr/bin/env python3
"""
meta_from_ollama.py — draft HTML <meta> tags using a local Ollama vision /
text model, by understanding the page's goal and content.

Inputs (any combination):
  - A short goal description: --goal "Marketing landing for product X"
  - An existing HTML page:    path/to/page.html  (positional argument)
  - A live URL:               https://example.com/page  (positional)
  - The brand / site name:    --site-name "Acme"
  - The canonical URL:        --canonical https://example.com/page
  - Language:                 --lang fr  (default: detected)

Output: a JSON object with suggested fields, printed to stdout:

  {
    "title":            "…",
    "description":      "…",
    "og_title":         "…",
    "og_description":   "…",
    "og_image_alt":     "…",
    "twitter_title":    "…",
    "twitter_description": "…",
    "schema_type":      "WebSite" | "Article" | "Product" | …,
    "keywords_hint":    ["…", "…"]      // for the author, NOT for emit
  }

The script does NOT auto-write to your HTML. Inspect, edit, paste.

Standards referenced (see references/meta-tags.md):
  W3C HTML / WHATWG, Open Graph (ogp.me), Twitter Cards,
  Schema.org, Google Search Central.

Requires Python 3.9+ and `requests`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

try:
    import requests
except ImportError:
    sys.stderr.write(
        "This script needs `requests`. Install with:\n"
        "    pip install -r front/scripts/requirements.txt\n"
    )
    sys.exit(2)

# Reuse the alt-text helper's language tables.
sys.path.insert(0, str(Path(__file__).parent))
from alt_from_ollama import (   # noqa: E402
    OLLAMA_URL,
    LANG_INSTRUCTIONS,
    detect_lang,
    pick_default_model,
)


JSON_SCHEMA_HINT = """
Return a single JSON object, no prose around it, with exactly these keys:

  title              ≤ 60 chars, page-topic first, brand last separated by " — ".
  description        120–155 chars, one sentence, no marketing buzzwords.
  og_title           ≤ 60 chars. Usually identical to title (without brand).
  og_description     ≤ 155 chars. Usually identical to description.
  og_image_alt       Short description of the hero image content. ≤ 125 chars.
                     Empty string if no hero image is known.
  twitter_title      Same content as og_title.
  twitter_description Same content as og_description.
  schema_type        One of: WebSite, Article, NewsArticle, BlogPosting,
                     Product, Person, Recipe, Event, FAQPage,
                     LocalBusiness, Organization.
  keywords_hint      Array of 3–8 short keywords for the author's reference.
                     These are NOT meant to be emitted as <meta name="keywords">.

Rules:
  - No "Welcome to", no "Discover", no "Boost", no emojis.
  - Do not invent facts (numbers, names, claims).
  - If a value is unknown, return an empty string for it.
  - Output strict JSON — double-quoted keys and strings, no trailing comma.
"""


CACHE_DIR = Path(os.environ.get("FRONT_CACHE_DIR", Path.home() / ".cache" / "front-skill")) / "meta"
NO_CACHE = bool(os.environ.get("FRONT_NO_CACHE"))


def _cache_key(goal: str, page_text: str, site_name: str, lang: str, model: str) -> str:
    h = hashlib.sha256()
    h.update(f"{goal}\x00{page_text}\x00{site_name}\x00{lang}\x00{model}".encode("utf-8"))
    return h.hexdigest()[:32]


def _cache_get(key: str) -> dict | None:
    if NO_CACHE:
        return None
    path = CACHE_DIR / f"{key}.json"
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
    return None


def _cache_set(key: str, value: dict) -> None:
    if NO_CACHE:
        return
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        (CACHE_DIR / f"{key}.json").write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def fetch_url(url: str) -> str:
    with urllib.request.urlopen(url, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def extract_text(html: str, limit: int = 6000) -> str:
    """Cheap HTML-to-text: drop <script>/<style>/<svg>, strip tags, collapse ws."""
    html = re.sub(r"(?is)<(script|style|svg|noscript)\b.*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def build_prompt(goal: str, page_text: str, site_name: str, lang: str) -> str:
    lang_line = LANG_INSTRUCTIONS.get(lang, LANG_INSTRUCTIONS["en"])
    parts = [lang_line, JSON_SCHEMA_HINT]
    if site_name:
        parts.append(f"\nBrand / site name: {site_name}")
    if goal:
        parts.append(f"\nPage goal: {goal}")
    if page_text:
        parts.append(f"\nPage content (extracted text):\n{page_text}")
    parts.append("\nWrite the JSON now.")
    return "\n".join(parts)


def extract_json(text: str) -> dict:
    """Find the first {...} JSON object in a model reply that may wrap it in prose."""
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"Model did not return JSON. Raw response:\n{text}")
    return json.loads(text[start : end + 1])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("source", nargs="?", help="HTML file path, URL, or empty if --goal is enough.")
    ap.add_argument("--goal", default="", help="Free-text page goal.")
    ap.add_argument("--site-name", default="", help="Brand or site name.")
    ap.add_argument("--canonical", default="", help="Canonical absolute URL.")
    ap.add_argument("--lang", default=None, help="BCP-47 base tag (en, fr, es, …).")
    ap.add_argument("--model", default=None, help="Override the Ollama model tag.")
    args = ap.parse_args()

    if not args.source and not args.goal:
        ap.error("Provide a source (HTML path or URL) or --goal.")

    page_text = ""
    if args.source:
        if re.match(r"^https?://", args.source, re.I):
            page_text = extract_text(fetch_url(args.source))
        else:
            page_text = extract_text(Path(args.source).read_text(encoding="utf-8", errors="ignore"))

    lang = (args.lang or detect_lang()).lower()[:2]
    model = args.model or pick_default_model()
    prompt = build_prompt(args.goal, page_text, args.site_name, lang)

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.2, "num_predict": 600},
    }

    try:
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=180)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        sys.stderr.write(
            f"Cannot reach Ollama at {OLLAMA_URL}. "
            f"Run `python front/scripts/install_alt_ai.py` or `ollama serve`.\n"
        )
        return 2

    body = resp.json()
    raw = body.get("response", "")
    try:
        parsed = extract_json(raw)
    except Exception as e:
        sys.stderr.write(f"{e}\n")
        return 1

    if args.canonical:
        parsed["canonical"] = args.canonical
    json.dump(parsed, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
