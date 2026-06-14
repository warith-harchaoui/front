#!/usr/bin/env python3
"""
simulate_cvd
============

Render an image as a color-blind viewer sees it.

Three CVD (color vision deficiency) types are supported:

* ``protanopia``     — no functional L cones; reds desaturate toward gray.
* ``deuteranopia``   — no functional M cones; the largest CVD population.
* ``tritanopia``     — no functional S cones (rare).

The implementation uses the Machado et al. (2009) precomputed simulation
matrices, applied in linear sRGB. The matrices are published; this script
embeds them verbatim. No model, no network, no surprises.

Output
------
By default, three sibling files are written next to the source image::

    <stem>-protanopia.png
    <stem>-deuteranopia.png
    <stem>-tritanopia.png

With ``--grid``, a single 2×2 mosaic is written instead, with the original
image in the top-left and each CVD variant labeled.

Usage
-----
::

    # Three sibling files
    python simulate_cvd.py public/hero.png

    # Side-by-side mosaic for design review
    python simulate_cvd.py public/hero.png --grid --out public/hero-cvd.png

    # Pick a subset of CVD types
    python simulate_cvd.py public/hero.png --types prot,deut

Notes
-----
* Python 3.9+, ``Pillow``.
* Numeric work uses Python floats (no NumPy dependency) — slower per pixel
  than NumPy but still milliseconds for typical screenshots, and one less
  dependency to install.
* Matrices: Machado, Oliveira, Fernandes (2009),
  "A Physiologically-based Model for Simulation of Color Vision Deficiency",
  IEEE Transactions on Visualization and Computer Graphics.

Author
------
`Warith Harchaoui, Ph.D. <https://www.linkedin.com/in/warith-harchaoui/>`_
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    sys.stderr.write(
        "This script needs Pillow. Install with:\n"
        "    pip install -r front/scripts/requirements.txt\n"
    )
    sys.exit(2)


# ── CVD simulation matrices (Machado et al. 2009, severity 1.0) ───────────────

#: Map from short CLI alias to the 3×3 matrix applied in linear sRGB.
#: Each matrix transforms an (R, G, B) vector into the CVD-simulated colour.
CVD_MATRICES: dict[str, tuple[tuple[float, float, float], ...]] = {
    "protanopia": (
        (0.152286, 1.052583, -0.204868),
        (0.114503, 0.786281,  0.099216),
        (-0.003882, -0.048116, 1.051998),
    ),
    "deuteranopia": (
        (0.367322, 0.860646, -0.227968),
        (0.280085, 0.672501,  0.047413),
        (-0.011820, 0.042940, 0.968881),
    ),
    "tritanopia": (
        (1.255528, -0.076749, -0.178779),
        (-0.078411, 0.930809,  0.147602),
        (0.004733, 0.691367, 0.303900),
    ),
}

#: Long-form labels used in the grid mosaic.
CVD_LABELS: dict[str, str] = {
    "protanopia":   "Protanopia — no L (red) cones",
    "deuteranopia": "Deuteranopia — no M (green) cones",
    "tritanopia":   "Tritanopia — no S (blue) cones",
}

#: Short CLI aliases users can type instead of the full name.
SHORTHAND: dict[str, str] = {
    "prot": "protanopia",
    "deut": "deuteranopia",
    "trit": "tritanopia",
}


# ── sRGB ↔ linear sRGB ─────────────────────────────────────────────────────

def srgb_to_linear(c: int) -> float:
    """
    Convert an 8-bit sRGB channel value to linear sRGB (in ``[0, 1]``).

    Parameters
    ----------
    c : int
        Channel value in ``[0, 255]``.

    Returns
    -------
    float
        Linear-light value in ``[0.0, 1.0]``.
    """
    f: float = c / 255.0
    # The standard sRGB transfer function: linear below the cusp, gamma
    # 2.4 above it. ``0.04045`` is the standard threshold.
    return f / 12.92 if f <= 0.04045 else ((f + 0.055) / 1.055) ** 2.4


def linear_to_srgb(f: float) -> int:
    """
    Convert a linear-sRGB value in ``[0, 1]`` back to an 8-bit sRGB channel.

    Parameters
    ----------
    f : float
        Linear-light value.

    Returns
    -------
    int
        Channel value clamped to ``[0, 255]``.
    """
    if f <= 0.0:
        return 0
    if f >= 1.0:
        return 255
    out: float = f * 12.92 if f <= 0.0031308 else 1.055 * f ** (1.0 / 2.4) - 0.055
    return max(0, min(255, round(out * 255)))


# ── Per-pixel transform ───────────────────────────────────────────────────

def simulate_pixel(
    rgb: tuple[int, int, int],
    matrix: tuple[tuple[float, float, float], ...],
) -> tuple[int, int, int]:
    """
    Apply a CVD matrix to a single 8-bit sRGB pixel.

    Parameters
    ----------
    rgb : tuple of int
        Source pixel ``(R, G, B)``.
    matrix : tuple of tuple of float
        3×3 transformation matrix from :data:`CVD_MATRICES`.

    Returns
    -------
    tuple of int
        Simulated pixel ``(R, G, B)``.
    """
    # Linearize the input — the matrix works in linear light, not in sRGB.
    r: float = srgb_to_linear(rgb[0])
    g: float = srgb_to_linear(rgb[1])
    b: float = srgb_to_linear(rgb[2])

    # Apply the 3×3 matrix.
    nr: float = matrix[0][0] * r + matrix[0][1] * g + matrix[0][2] * b
    ng: float = matrix[1][0] * r + matrix[1][1] * g + matrix[1][2] * b
    nb: float = matrix[2][0] * r + matrix[2][1] * g + matrix[2][2] * b

    return linear_to_srgb(nr), linear_to_srgb(ng), linear_to_srgb(nb)


def simulate_image(im: Image.Image, kind: str) -> Image.Image:
    """
    Apply a CVD simulation to a whole image.

    Parameters
    ----------
    im : Image.Image
        Source image. Will be converted to RGB internally.
    kind : str
        One of the keys in :data:`CVD_MATRICES`.

    Returns
    -------
    Image.Image
        New RGB image of the same size.
    """
    matrix = CVD_MATRICES[kind]
    rgb = im.convert("RGB")

    # Pixel-by-pixel iteration. For large images this is ~1 s; well within
    # acceptable for a static review tool. NumPy would be ~50× faster but
    # adds a dependency.
    out = Image.new("RGB", rgb.size)
    src_pixels = rgb.load()
    dst_pixels = out.load()
    w, h = rgb.size
    for y in range(h):
        for x in range(w):
            dst_pixels[x, y] = simulate_pixel(src_pixels[x, y], matrix)
    return out


# ── Grid mosaic ─────────────────────────────────────────────────────────────

def make_grid(original: Image.Image, simulated: dict[str, Image.Image]) -> Image.Image:
    """
    Compose a single image showing the original next to each CVD variant.

    The mosaic layout adapts to the number of supplied variants:

    * 1 variant  → 1×2 grid (original, variant).
    * 2 variants → 2×2 grid (original + 2 variants + an empty slot).
    * 3 variants → 2×2 grid (original + 3 variants).

    Parameters
    ----------
    original : Image.Image
        Source image, used for the top-left cell.
    simulated : dict
        Mapping of CVD kind → simulated image.

    Returns
    -------
    Image.Image
        Composite RGB image with labels overlaid in the top-left of each cell.
    """
    cells = [("Original", original)] + [(CVD_LABELS[k], simulated[k]) for k in simulated]
    cols: int = 2
    rows: int = (len(cells) + cols - 1) // cols
    cell_w, cell_h = original.size

    grid = Image.new("RGB", (cell_w * cols, cell_h * rows), (255, 255, 255))
    draw = ImageDraw.Draw(grid)

    # Pillow ships a tiny default font; that is enough for the corner label.
    try:
        font = ImageFont.load_default()
    except OSError:
        font = None  # pragma: no cover

    for idx, (label, im) in enumerate(cells):
        col: int = idx % cols
        row: int = idx // cols
        grid.paste(im.resize((cell_w, cell_h)), (col * cell_w, row * cell_h))
        # Translucent label background for legibility on busy images.
        text_pad: int = 8
        # Two-pass: white plate behind, black text in front. Plain default font.
        if font is not None:
            bbox = draw.textbbox((0, 0), label, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.rectangle(
                (col * cell_w, row * cell_h, col * cell_w + tw + 2 * text_pad, row * cell_h + th + 2 * text_pad),
                fill=(255, 255, 255),
            )
            draw.text(
                (col * cell_w + text_pad, row * cell_h + text_pad),
                label, fill=(0, 0, 0), font=font,
            )

    return grid


# ── CLI entry point ───────────────────────────────────────────────────────

def parse_types(arg: str) -> list[str]:
    """
    Parse a comma-separated list of CVD types or shorthands.

    Parameters
    ----------
    arg : str
        Comma-separated tokens. Each token may be either a full name
        (``protanopia``) or a shorthand (``prot``).

    Returns
    -------
    list of str
        Full CVD kind names, in source order.

    Raises
    ------
    argparse.ArgumentTypeError
        On unknown tokens.
    """
    out: list[str] = []
    for tok in arg.split(","):
        tok = tok.strip().lower()
        if not tok:
            continue
        full = SHORTHAND.get(tok, tok)
        if full not in CVD_MATRICES:
            raise argparse.ArgumentTypeError(f"Unknown CVD type: {tok}")
        out.append(full)
    return out or list(CVD_MATRICES.keys())


def main() -> int:
    """
    Generate the requested CVD-simulated outputs.

    Returns
    -------
    int
        Process exit code; ``0`` on success.
    """
    p = argparse.ArgumentParser(
        description="Render an image as a color-blind viewer sees it.",
    )
    p.add_argument(
        "source", type=Path,
        help="Path to the source image (PNG, JPG, WebP, …).",
    )
    p.add_argument(
        "--out", type=Path,
        help="Output path. For per-type mode, a directory; for --grid, a file. "
             "Defaults to siblings of the source.",
    )
    p.add_argument(
        "--types", type=parse_types, default=parse_types("protanopia,deuteranopia,tritanopia"),
        help="Comma-separated CVD types (default: all three).",
    )
    p.add_argument(
        "--grid", action="store_true",
        help="Write a single 2×2 mosaic instead of three sibling files.",
    )
    args = p.parse_args()

    try:
        original = Image.open(args.source).convert("RGB")
    except OSError as e:
        sys.stderr.write(f"Cannot open {args.source}: {e}\n")
        return 1

    simulated: dict[str, Image.Image] = {}
    for kind in args.types:
        simulated[kind] = simulate_image(original, kind)

    if args.grid:
        # Compose the mosaic and write a single file.
        grid = make_grid(original, simulated)
        out_path: Path = args.out or args.source.with_name(args.source.stem + "-cvd-grid.png")
        grid.save(out_path, format="PNG", optimize=True)
        print(f"→ Wrote grid to {out_path}")
    else:
        # Per-type sibling files.
        out_dir: Path = args.out or args.source.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        for kind, im in simulated.items():
            out_path = out_dir / f"{args.source.stem}-{kind}{args.source.suffix or '.png'}"
            im.save(out_path, format="PNG", optimize=True)
            print(f"→ Wrote {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
