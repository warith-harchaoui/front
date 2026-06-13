#!/usr/bin/env python3
"""
favicons.py — generate a complete favicon / app-icon set from a single logo.

Input:  any raster image (PNG, JPG, WebP) or an SVG file.
Output: the full set of formats modern browsers actually use, plus a
        site.webmanifest and an HTML snippet ready to paste into <head>.

Files produced (relative to --out, default ./public/):

  favicon.svg              when the input is SVG (copied)
  favicon.ico              multi-resolution (16, 32, 48)
  favicon-16.png
  favicon-32.png
  favicon-48.png
  apple-touch-icon.png     180×180, opaque, no rounded corners (the OS adds them)
  icon-192.png             PWA install
  icon-512.png             PWA install
  icon-maskable-512.png    PWA maskable — content in central 80%
  site.webmanifest         minimal PWA manifest
  head.html                <link> tags + theme-color meta to paste in <head>

W3C / current best practice:
  - SVG is the preferred favicon format; rasters are fallback.
  - apple-touch-icon should be opaque; transparent edges are clipped by the OS.
  - Maskable icons reserve the central 80% (40% radius from center).
  - <meta name="theme-color"> matches the favicon's background for both schemes.

Requires: Pillow (>= 10).
        pip install -r front/scripts/requirements.txt
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.stderr.write(
        "This script needs Pillow. Install with:\n"
        "    pip install -r front/scripts/requirements.txt\n"
    )
    sys.exit(2)


# Sizes a modern site actually serves. Avoid the legacy 70/72/114/144 zoo.
PNG_SIZES = (16, 32, 48, 192, 512)
APPLE_TOUCH_SIZE = 180
MASKABLE_SIZE = 512
MASKABLE_SAFE = 0.8   # content occupies the central 80%; outer 10% is bleed.
ICO_SIZES = (16, 32, 48)


def parse_hex(s: str) -> tuple[int, int, int]:
    s = s.lstrip("#").strip()
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) != 6:
        raise argparse.ArgumentTypeError(f"Bad hex color: {s!r}")
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def open_source(path: Path) -> tuple[Image.Image, bool]:
    """Open the source as RGBA. Return (image, is_svg)."""
    if path.suffix.lower() == ".svg":
        # We don't rasterize SVG ourselves — let the user pre-rasterize, or
        # use a tool like rsvg-convert / Inkscape and pass the PNG output.
        sys.stderr.write(
            f"Input is SVG. The .svg will be copied as favicon.svg, but raster\n"
            f"variants need a PNG source. Run again with --raster <png-path>.\n"
        )
        # Return a tiny placeholder so the caller can decide.
        return Image.new("RGBA", (1, 1)), True
    im = Image.open(path).convert("RGBA")
    return im, False


def resize_square(im: Image.Image, size: int) -> Image.Image:
    """Resize so the longer edge fits `size`, centered on a transparent square."""
    src = im.copy()
    src.thumbnail((size, size), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(src, ((size - src.width) // 2, (size - src.height) // 2), src)
    return canvas


def flatten_on(bg: tuple[int, int, int], im: Image.Image) -> Image.Image:
    """Composite RGBA over a solid background → opaque RGB."""
    base = Image.new("RGB", im.size, bg)
    base.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
    return base


def make_maskable(im: Image.Image, bg: tuple[int, int, int]) -> Image.Image:
    """Put the source in the central MASKABLE_SAFE of a MASKABLE_SIZE square."""
    canvas = Image.new("RGB", (MASKABLE_SIZE, MASKABLE_SIZE), bg)
    inner = int(MASKABLE_SIZE * MASKABLE_SAFE)
    fit = im.copy()
    fit.thumbnail((inner, inner), Image.LANCZOS)
    pad = (MASKABLE_SIZE - fit.width) // 2, (MASKABLE_SIZE - fit.height) // 2
    canvas.paste(fit, pad, fit if fit.mode == "RGBA" else None)
    return canvas


def write_manifest(out_dir: Path, name: str, short: str, bg_hex: str, theme_hex: str) -> None:
    manifest = {
        "name": name,
        "short_name": short or name,
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
        "background_color": bg_hex,
        "theme_color": theme_hex,
        "display": "standalone",
        "start_url": "/",
    }
    (out_dir / "site.webmanifest").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def write_head_snippet(out_dir: Path, theme_hex_light: str, theme_hex_dark: str, has_svg: bool) -> None:
    snippet = []
    if has_svg:
        snippet.append('<link rel="icon" href="/favicon.svg" type="image/svg+xml">')
    snippet.append('<link rel="icon" href="/favicon.ico" sizes="any">')
    snippet.append('<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">')
    snippet.append('<link rel="icon" href="/favicon-16.png" sizes="16x16" type="image/png">')
    snippet.append('<link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180">')
    snippet.append('<link rel="manifest" href="/site.webmanifest">')
    snippet.append(f'<meta name="theme-color" content="{theme_hex_light}" media="(prefers-color-scheme: light)">')
    snippet.append(f'<meta name="theme-color" content="{theme_hex_dark}" media="(prefers-color-scheme: dark)">')
    (out_dir / "head.html").write_text("\n".join(snippet) + "\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("source", type=Path, help="Path to the logo (PNG, JPG, WebP, or SVG).")
    p.add_argument("--raster", type=Path, help="If --source is SVG, use this PNG for raster outputs.")
    p.add_argument("--out", type=Path, default=Path("public"), help="Output directory. Default: ./public")
    p.add_argument("--name", default="App", help="Long name in the webmanifest.")
    p.add_argument("--short-name", default=None, help="Short name in the webmanifest.")
    p.add_argument("--bg", default="#FFFFFF", help="Solid background for opaque icons (apple-touch, maskable).")
    p.add_argument("--theme-light", default=None, help="theme-color for prefers-color-scheme: light. Default: --bg")
    p.add_argument("--theme-dark", default="#000000", help="theme-color for prefers-color-scheme: dark.")
    args = p.parse_args()

    bg = parse_hex(args.bg)
    theme_light = args.theme_light or args.bg
    theme_dark = args.theme_dark
    args.out.mkdir(parents=True, exist_ok=True)

    source_im, is_svg = open_source(args.source)
    raster_source = args.raster or args.source
    if is_svg and not args.raster:
        # Still copy the SVG; bail out of the raster pipeline.
        shutil.copyfile(args.source, args.out / "favicon.svg")
        sys.stderr.write(
            "Wrote favicon.svg only. Re-run with --raster <png-path> to also produce the PNGs.\n"
        )
        return 0

    # Copy the SVG if provided.
    if is_svg:
        shutil.copyfile(args.source, args.out / "favicon.svg")
    raster_im = Image.open(raster_source).convert("RGBA") if is_svg else source_im

    # Standard PNG sizes (transparent).
    for size in PNG_SIZES:
        im = resize_square(raster_im, size)
        im.save(args.out / f"icon-{size}.png" if size >= 192 else args.out / f"favicon-{size}.png",
                format="PNG", optimize=True)

    # ICO with three embedded sizes.
    ico_im = resize_square(raster_im, max(ICO_SIZES))
    ico_im.save(args.out / "favicon.ico", sizes=[(s, s) for s in ICO_SIZES])

    # apple-touch-icon: opaque, no rounded corners.
    touch = flatten_on(bg, resize_square(raster_im, APPLE_TOUCH_SIZE))
    touch.save(args.out / "apple-touch-icon.png", format="PNG", optimize=True)

    # Maskable PWA icon.
    masked = make_maskable(raster_im, bg)
    masked.save(args.out / "icon-maskable-512.png", format="PNG", optimize=True)

    write_manifest(args.out, args.name, args.short_name or args.name, args.bg, theme_light)
    write_head_snippet(args.out, theme_light, theme_dark, has_svg=is_svg)

    print(f"→ Wrote favicon set to {args.out}/")
    print(f"  Paste {args.out}/head.html into your <head>.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
