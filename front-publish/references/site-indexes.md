# Site indexes — `site_indexes.py`

Generate the standard set of site-index files for a project's web output, respecting the canonical specs for each. One Python script, stdlib only.

## What it emits

| File | Spec | When |
|---|---|---|
| `robots.txt` | [Google Search Central — robots.txt](https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt) | Always |
| `sitemap.xml` | [sitemaps.org 0.9](https://www.sitemaps.org/protocol.html) | Always |
| `llms.txt` | [llmstxt.org](https://llmstxt.org/) | Always |
| `feed.atom` | [Atom 1.0 (RFC 4287)](https://datatracker.ietf.org/doc/html/rfc4287) | When a blog directory is detected (`posts/`, `blog/`, `articles/`) |
| `rss.xml` | [RSS 2.0](https://www.rssboard.org/rss-specification) | Same as Atom, but emitted instead when `--rss` is passed |
| `humans.txt` | [humanstxt.org](https://humanstxt.org/Standard.html) | When `--humans` is passed OR an `AUTHORS` / `CREDITS` file exists at the root |

## Run

```bash
# Bare minimum: a project root + the public origin
python scripts/site_indexes.py --root . --base-url https://example.com

# Project with a blog folder under posts/
python scripts/site_indexes.py --root . --base-url https://example.com --feed-from posts

# Force RSS 2.0 for clients that haven't moved past 2002
python scripts/site_indexes.py --root . --base-url https://example.com --feed-from posts --rss

# Ship a humans.txt explicitly
python scripts/site_indexes.py --root . --base-url https://example.com --humans

# Override the output directory (default: --root)
python scripts/site_indexes.py --root . --base-url https://example.com --out public
```

The script walks the project root looking for `.html` files at the root and inside the conventional output directories (`public/`, `dist/`, `site/`, `_site/`, `build/`, `out/`) plus `.md` files at the root and under `docs/`. Each becomes a sitemap entry and an `llms.txt` bullet.

## What the skill does automatically

When Claude emits a website (the **Markdown → website workflow** in SKILL.md, or any other surface that produces an HTML tree), it runs `site_indexes.py` as the final step:

1. Picks `--base-url` from the user's stated origin, or a sensible placeholder marked as TODO.
2. Auto-detects a blog folder (`posts/`, `blog/`, `articles/`) and emits the Atom feed when found.
3. Reads `AUTHORS` / `CREDITS` at the root if present, and emits `humans.txt` automatically.
4. Writes everything next to `index.html` (or under `public/` if that's the chosen output directory).
5. Surfaces the resulting URLs in the page's `<head>` via the meta-tags reference (`references/meta-tags.md`):

```html
<link rel="sitemap" type="application/xml" href="/sitemap.xml">
<link rel="alternate" type="application/atom+xml" href="/feed.atom" title="Site feed">
<!-- RSS variant: -->
<link rel="alternate" type="application/rss+xml" href="/rss.xml" title="Site feed">
```

The robots.txt's `Sitemap:` line is set automatically too.

## Why Atom is the default (not RSS 2.0)

- Atom 1.0 is an IETF standard with strict semantics; RSS 2.0 is a vendor format with ambiguous fields.
- Modern aggregators (NetNewsWire, Inoreader, FreshRSS, Feedbin, Bluesky's feed reader, Mastodon) all read Atom.
- Apple Podcasts still requires RSS 2.0 with `<itunes:*>` extensions — for podcasts specifically, the user should run with `--rss` and post-process the file to add the iTunes block.

## Composition with other helpers

`site_indexes.py` is one node in the skill's emission pipeline:

```text
.md sources ──► HTML pages ──► favicons.py ──► meta_from_ollama.py ──► site_indexes.py
                                  (icons + manifest)   (per-page meta)     (whole-site indexes)
```

For pages with embedded images or video, alt text and captions are produced by `alt_from_ollama.py` and `captions_from_whisper.py` in the same pass.

## Checklist (before publishing the site)

- [ ] `robots.txt`, `sitemap.xml`, `llms.txt` present at the site root.
- [ ] `<link rel="sitemap">` and `<link rel="alternate" type="application/atom+xml">` in every page's `<head>` (handled by `meta-tags.md`).
- [ ] `robots.txt`'s `Sitemap:` line points at the absolute URL.
- [ ] Atom feed validates via <https://validator.w3.org/feed/>.
- [ ] `llms.txt` follows the llmstxt.org shape: H1, blockquote, `## Optional` for non-essential links.
- [ ] If a podcast, RSS 2.0 emitted (`--rss`) and iTunes block added.
- [ ] `humans.txt` shipped if there's an AUTHORS file or `--humans` was passed.
