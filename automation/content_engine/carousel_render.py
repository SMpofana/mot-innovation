#!/usr/bin/env python
"""
carousel_render.py — Render LinkedIn carousel slides as PNG images.

Turns the carousel JSON design specs (from linkedin_carousel.py) into actual
1080x1350 portrait slide images using Pillow. Renders the trionn monochrome
style: dark bg, white/gray text, accent bars, slide numbers.

Usage:
    python carousel_render.py --carousel carousels/carousel_*.json
    python carousel_render.py --all
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CAROUSEL_DIR = SCRIPT_DIR / "carousels"
RENDER_DIR = SCRIPT_DIR / "carousels" / "rendered"
RENDER_DIR.mkdir(parents=True, exist_ok=True)

SLIDE_W, SLIDE_H = 1080, 1350
SANS = "C:/Windows/Fonts/arial.ttf"
SANS_BOLD = "C:/Windows/Fonts/arialbd.ttf"


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _font(size: int, bold: bool = False):
    from PIL import ImageFont
    try:
        return ImageFont.truetype(SANS_BOLD if bold else SANS, size)
    except Exception:
        return ImageFont.load_default()


def _wrap(draw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines


def render_slide(slide: dict, out_path: Path) -> Path:
    """Render one carousel slide to a PNG."""
    from PIL import Image, ImageDraw

    design = slide.get("design", {})
    bg = _hex_to_rgb(design.get("background_color", "#0a0a0a"))
    text_color = _hex_to_rgb(design.get("text_color", "#FFFFFF"))
    accent = _hex_to_rgb(design.get("accent_color", "#3B82F6"))
    positions = design.get("text_positions", {})

    img = Image.new("RGB", (SLIDE_W, SLIDE_H), bg)
    draw = ImageDraw.Draw(img)

    # Elements (accent bar, slide number)
    for el in design.get("elements", []):
        etype = el.get("type")
        if etype == "accent_bar":
            pos = el.get("position", "top")
            color = _hex_to_rgb(el.get("color", "#3B82F6"))
            h = int(el.get("height", "8px").replace("px", ""))
            if pos == "top":
                draw.rectangle([0, 0, SLIDE_W, h], fill=color)
            else:  # bottom
                draw.rectangle([0, SLIDE_H - h, SLIDE_W, SLIDE_H], fill=color)
        elif etype == "slide_number":
            pos = el.get("position", "top_right")
            color = _hex_to_rgb(el.get("color", "#999999"))
            f = _font(28)
            text = el.get("text", "")
            bbox = draw.textbbox((0, 0), text, font=f)
            tw = bbox[2] - bbox[0]
            if pos == "top_right":
                draw.text((SLIDE_W - tw - 40, 40), text, font=f, fill=color)
            else:
                draw.text((40, 40), text, font=f, fill=color)

    # Text positions
    for key, pos in positions.items():
        text = slide.get(key)
        if not text:
            continue
        size = int(pos.get("font_size", 32))
        bold = pos.get("font_weight") == "bold"
        raw_color = pos.get("color", "#FFFFFF" if key == "headline" else text_color)
        color = _hex_to_rgb(raw_color) if isinstance(raw_color, str) else raw_color
        f = _font(size, bold)
        max_w = int(SLIDE_W * 0.8)
        lines = _wrap(draw, text, f, max_w)
        line_h = int(size * 1.3)
        total_h = len(lines) * line_h
        y_pct = pos.get("y", "50%")
        y_pct = float(str(y_pct).replace("%", "")) / 100
        y = int(SLIDE_H * y_pct) - total_h // 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=f)
            tw = bbox[2] - bbox[0]
            x = (SLIDE_W - tw) // 2
            draw.text((x, y), line, font=f, fill=color)
            y += line_h

    img.save(str(out_path), quality=95)
    return out_path


def render_carousel(carousel_path: Path) -> list[Path]:
    """Render all slides of a carousel JSON to PNGs."""
    data = json.loads(carousel_path.read_text(encoding="utf-8"))
    slides = data.get("slides", [])
    stem = carousel_path.stem
    out_paths = []
    for i, slide in enumerate(slides):
        out = RENDER_DIR / f"{stem}_slide{i + 1}.png"
        render_slide(slide, out)
        out_paths.append(out)
    return out_paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Render carousel slides as PNGs")
    parser.add_argument("--carousel", type=Path, help="Carousel JSON file")
    parser.add_argument("--all", action="store_true", help="Render all carousels")
    args = parser.parse_args()

    print("=" * 60)
    print("M.O.T INNOVATION — CAROUSEL SLIDE RENDERER")
    print("=" * 60)

    if args.all:
        files = sorted(CAROUSEL_DIR.glob("carousel_*.json"))
        print(f"Found {len(files)} carousels\n")
        total = 0
        for f in files:
            outs = render_carousel(f)
            print(f"  ✅ {f.name} → {len(outs)} slides")
            total += len(outs)
        print(f"\nRendered {total} slides to {RENDER_DIR}")
        return 0

    if args.carousel:
        outs = render_carousel(args.carousel)
        print(f"Rendered {len(outs)} slides:")
        for o in outs:
            print(f"  → {o}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
