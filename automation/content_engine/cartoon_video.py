#!/usr/bin/env python
"""
cartoon_video.py — Flat-cartoon faceless YouTube Short generator.

Draws simple flat-vector cartoon scene illustrations with Pillow (no API),
then animates them with ffmpeg (Ken Burns + crossfades + progress bar).

Each scene gets a themed cartoon illustration based on its role:
  - Hook:            bold title card over a cartoon backdrop
  - Problem Agitation: messy desk, scattered papers, disconnected tools,
                       frustrated character
  - Solution:        clean connected system, organized dashboard, happy
                       character
  - CTA:             brand mark + call to action

Style: flat colors, dark outlines, simple shapes — a clean vector-cartoon
look. Headline text is overlaid in the trionn cream serif.

Usage:
    python cartoon_video.py --script scripts/yt_short_*.md --audio audio/yt_short_*.mp3
    python cartoon_video.py --all
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from animated_video import (
    parse_script, _ken_burns_clip, _concat_with_xfade, _add_progress_bar,
    _probe_duration, _find_audio, _is_valid_video, TMP_DIR, OUTPUT_DIR,
    WIDTH, HEIGHT, FPS, SERIF_BOLD, SANS,
)

# Cartoon palette (flat, friendly, high-contrast)
SKY = (135, 206, 250)        # light blue sky
SKY_DARK = (70, 130, 180)    # deeper blue
GROUND = (144, 238, 144)     # light green ground
GROUND_DARK = (34, 139, 34)  # darker green
SUN = (255, 215, 0)          # yellow sun
CLOUD = (255, 255, 255)      # white cloud
OUTLINE = (40, 40, 40)       # dark outline
CHAR_SKIN = (255, 224, 189)  # skin tone
CHAR_SHIRT = (70, 130, 180)  # blue shirt
CHAR_PANTS = (60, 60, 60)    # dark pants
PAPER = (255, 250, 240)      # paper
RED = (220, 80, 80)          # alert red
GREEN = (60, 179, 113)       # success green
CREAM = (245, 241, 235)      # text cream


# ── Drawing helpers ───────────────────────────────────────────────────────────

def _ellipse(draw, cx, cy, rx, ry, fill, outline=OUTLINE, width=3):
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill,
                 outline=outline, width=width)


def _rounded_rect(draw, box, radius, fill, outline=OUTLINE, width=3):
    draw.rounded_rectangle(box, radius=radius, fill=fill,
                           outline=outline, width=width)


def _draw_character(draw, x, y, scale=1.0, happy=True, frustrated=False):
    """Draw a simple flat cartoon character. (x,y) is the head center."""
    s = scale
    # Head
    _ellipse(draw, x, y, 40 * s, 40 * s, CHAR_SKIN)
    # Eyes
    eye_y = y - 8 * s
    if frustrated:
        # Angled brows + small eyes
        draw.line([(x - 18 * s, y - 22 * s), (x - 6 * s, y - 16 * s)],
                  fill=OUTLINE, width=4)
        draw.line([(x + 18 * s, y - 22 * s), (x + 6 * s, y - 16 * s)],
                  fill=OUTLINE, width=4)
        _ellipse(draw, x - 14 * s, eye_y, 5 * s, 5 * s, OUTLINE)
        _ellipse(draw, x + 14 * s, eye_y, 5 * s, 5 * s, OUTLINE)
        # Frown
        draw.arc([x - 12 * s, y + 8 * s, x + 12 * s, y + 24 * s],
                 20, 160, fill=OUTLINE, width=3)
    else:
        _ellipse(draw, x - 14 * s, eye_y, 6 * s, 6 * s, OUTLINE)
        _ellipse(draw, x + 14 * s, eye_y, 6 * s, 6 * s, OUTLINE)
        # Smile
        draw.arc([x - 12 * s, y + 2 * s, x + 12 * s, y + 20 * s],
                 20, 160, fill=OUTLINE, width=3)
    # Body (rounded rect below head)
    body_top = y + 40 * s
    _rounded_rect(draw, [x - 30 * s, body_top, x + 30 * s, body_top + 70 * s],
                  15 * s, CHAR_SHIRT)
    # Arms
    draw.line([(x - 30 * s, body_top + 15 * s), (x - 55 * s, body_top + 45 * s)],
              fill=CHAR_SHIRT, width=int(8 * s))
    draw.line([(x + 30 * s, body_top + 15 * s), (x + 55 * s, body_top + 45 * s)],
              fill=CHAR_SHIRT, width=int(8 * s))


def _draw_cloud(draw, x, y, s=1.0):
    _ellipse(draw, x, y, 30 * s, 20 * s, CLOUD)
    _ellipse(draw, x - 25 * s, y + 5 * s, 22 * s, 16 * s, CLOUD)
    _ellipse(draw, x + 25 * s, y + 5 * s, 22 * s, 16 * s, CLOUD)


def _draw_sun(draw, x, y, r=40):
    _ellipse(draw, x, y, r, r, SUN, outline=None)
    for i in range(8):
        import math
        a = math.radians(i * 45)
        draw.line([(x + (r + 8) * math.cos(a), y + (r + 8) * math.sin(a)),
                   (x + (r + 22) * math.cos(a), y + (r + 22) * math.sin(a))],
                  fill=SUN, width=5)


def _draw_building(draw, x, y, w, h, color):
    """Draw a simple flat building. (x,y) is bottom-center."""
    _rounded_rect(draw, [x - w // 2, y - h, x + w // 2, y], 6, color)
    # Windows
    for wy in range(int(y - h + 20), int(y - 20), 30):
        for wx in range(int(x - w // 2 + 12), int(x + w // 2 - 12), 26):
            _rounded_rect(draw, [wx, wy, wx + 12, wy + 12], 2, (255, 255, 255),
                          outline=None)


def _draw_desk(draw, x, y, w, h):
    """Draw a desk with scattered papers + a monitor. (x,y) is top-center."""
    _rounded_rect(draw, [x - w // 2, y, x + w // 2, y + h], 6, (139, 90, 43))
    # Monitor
    _rounded_rect(draw, [x - 40, y - 30, x + 40, y + 10], 4, (60, 60, 60))
    _rounded_rect(draw, [x - 32, y - 22, x + 32, y + 2], 2, (135, 206, 250),
                  outline=None)
    # Scattered papers
    for i, (px, py, rot) in enumerate([(-70, y + 20, 0), (-40, y + 40, 15),
                                       (50, y + 25, -10), (80, y + 45, 5)]):
        _rounded_rect(draw, [px, py, px + 40, py + 30], 2, PAPER)
        draw.line([(px + 5, py + 8), (px + 35, py + 8)], fill=OUTLINE, width=2)
        draw.line([(px + 5, py + 16), (px + 30, py + 16)], fill=OUTLINE, width=2)


def _draw_connected_nodes(draw, cx, cy, n=5, r=28):
    """Draw a network of connected nodes (solution scene)."""
    import math
    pts = []
    for i in range(n):
        a = math.radians(i * (360 / n) - 90)
        pts.append((cx + r * 2.2 * math.cos(a), cy + r * 2.2 * math.sin(a)))
    # Connections
    for i in range(n):
        for j in range(i + 1, n):
            draw.line([pts[i], pts[j]], fill=GREEN, width=4)
    # Nodes
    for p in pts:
        _ellipse(draw, p[0], p[1], r, r, (100, 149, 237))
        _ellipse(draw, p[0], p[1], r // 2, r // 2, (255, 255, 255), outline=None)


# ── Scene illustration dispatch ───────────────────────────────────────────────

def draw_scene_illustration(draw, scene_name: str, pain_point: str):
    """Draw the cartoon illustration for a scene based on its role."""
    name = scene_name.lower()

    if "hook" in name:
        # Title card: sky + sun + clouds + skyline
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=SKY)
        _draw_sun(draw, WIDTH - 90, 150)
        _draw_cloud(draw, 120, 200)
        _draw_cloud(draw, 300, 140, 0.8)
        # Skyline
        _draw_building(draw, 120, HEIGHT - 200, 120, 200, (176, 196, 222))
        _draw_building(draw, 260, HEIGHT - 200, 100, 200, (119, 136, 153))
        _draw_building(draw, 400, HEIGHT - 200, 140, 200, (176, 196, 222))
        _draw_building(draw, 560, HEIGHT - 200, 110, 200, (119, 136, 153))
        draw.rectangle([0, HEIGHT - 200, WIDTH, HEIGHT], fill=GROUND)

    elif "problem" in name:
        # Messy desk + frustrated character + disconnected tools
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=SKY)
        draw.rectangle([0, HEIGHT - 300, WIDTH, HEIGHT], fill=GROUND)
        _draw_desk(draw, WIDTH // 2, HEIGHT - 300, 420, 120)
        _draw_character(draw, WIDTH // 2, HEIGHT - 420, 1.1, frustrated=True)
        # Disconnected tool icons (scattered)
        for i, (tx, ty) in enumerate([(90, 300), (WIDTH - 100, 260),
                                      (150, 200), (WIDTH - 140, 380)]):
            _rounded_rect(draw, [tx - 20, ty - 20, tx + 20, ty + 20], 6,
                          (200, 200, 200))
            draw.line([(tx - 10, ty), (tx + 10, ty)], fill=OUTLINE, width=3)
            draw.line([(tx, ty - 10), (tx, ty + 10)], fill=OUTLINE, width=3)

    elif "solution" in name:
        # Clean connected system + happy character
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=SKY)
        draw.rectangle([0, HEIGHT - 300, WIDTH, HEIGHT], fill=GROUND)
        _draw_connected_nodes(draw, WIDTH // 2, 300, n=5, r=26)
        _draw_character(draw, WIDTH // 2, HEIGHT - 420, 1.1, happy=True)
        # A clean dashboard panel
        _rounded_rect(draw, [WIDTH // 2 - 150, HEIGHT - 280, WIDTH // 2 + 150,
                             HEIGHT - 120], 10, (255, 255, 255))
        for i in range(3):
            _rounded_rect(draw, [WIDTH // 2 - 130, HEIGHT - 260 + i * 45,
                                 WIDTH // 2 + 130, HEIGHT - 230 + i * 45],
                          4, (100, 149, 237), outline=None)

    elif "cta" in name:
        # Brand card: dark bg + cream text handled by overlay; draw a badge
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(10, 10, 10))
        _draw_connected_nodes(draw, WIDTH // 2, 300, n=4, r=24)
        # Big plus-cross motif
        cx, cy = WIDTH // 2, HEIGHT // 2 - 100
        for s in (60, 40, 20):
            draw.line([(cx - s, cy), (cx + s, cy)], fill=CREAM, width=4)
            draw.line([(cx, cy - s), (cx, cy + s)], fill=CREAM, width=4)

    else:
        draw.rectangle([0, 0, WIDTH, HEIGHT], fill=SKY)


# ── Scene image generation ────────────────────────────────────────────────────

def create_cartoon_scene_image(scene: dict, idx: int, total: int,
                               out_path: Path) -> Path:
    """Render a cartoon scene background + headline text overlay."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (WIDTH, HEIGHT), SKY)
    draw = ImageDraw.Draw(img)

    pain_point = scene.get("pain_point", "")
    draw_scene_illustration(draw, scene["name"], pain_point)

    # Headline text overlay (cream serif, centered, with subtle shadow)
    try:
        head_font = ImageFont.truetype(SERIF_BOLD, 60)
    except Exception:
        head_font = ImageFont.load_default()

    text = scene["overlays"][0] if scene["overlays"] else scene["name"]
    lines = _wrap(draw, text, head_font, WIDTH - 100)
    line_h = 74
    total_h = len(lines) * line_h
    y = (HEIGHT - total_h) // 2 - 40

    # Semi-transparent band behind text for readability
    band_top = y - 20
    band_bottom = y + total_h + 20
    band = Image.new("RGBA", (WIDTH, band_bottom - band_top), (0, 0, 0, 120))
    img.paste(band, (0, band_top), band)

    for line in lines:
        # Shadow
        draw.text((WIDTH // 2 + 2, y + 2), line, font=head_font,
                  fill=(0, 0, 0), anchor="mm")
        draw.text((WIDTH // 2, y), line, font=head_font, fill=CREAM, anchor="mm")
        y += line_h

    # Scene label (top)
    try:
        label_font = ImageFont.truetype(SANS, 22)
    except Exception:
        label_font = ImageFont.load_default()
    label = f"{scene['name'].upper()}  /  {idx + 1:02d}"
    draw.text((WIDTH // 2, 60), label, font=label_font, fill=(255, 255, 255),
              anchor="mm")

    img.save(str(out_path), quality=95)
    return out_path


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


# ── Assembly ──────────────────────────────────────────────────────────────────

def assemble_cartoon(script_path: Path, audio_path: Path | None = None) -> Path | None:
    """Assemble a flat-cartoon animated video from a script + audio."""
    if not audio_path:
        audio_path = _find_audio(script_path)
    if not audio_path:
        print(f"   ⚠️  No audio found for {script_path.name}")
        return None

    script = parse_script(script_path)
    scenes = script["scenes"]
    if not scenes:
        print(f"   ⚠️  No scenes parsed from {script_path.name}")
        return None

    print(f"   🎨 Drawing {len(scenes)} cartoon scenes from {audio_path.name}...")

    # 1. Render each cartoon scene
    bg_paths = []
    for i, scene in enumerate(scenes):
        bg = TMP_DIR / f"cartoon_bg_{i:02d}.png"
        create_cartoon_scene_image(scene, i, len(scenes), bg)
        bg_paths.append(bg)

    # 2. Ken Burns clip per scene
    clips = []
    for i, (scene, bg) in enumerate(zip(scenes, bg_paths)):
        clip = TMP_DIR / f"cartoon_clip_{i:02d}.mp4"
        if _ken_burns_clip(bg, scene["duration"], clip, zoom_in=(i % 2 == 0)):
            clips.append(clip)

    if not clips:
        print("   ❌ No clips generated")
        return None

    # 3. Crossfade concat
    concat = TMP_DIR / "cartoon_concat.mp4"
    if not _concat_with_xfade(clips, concat):
        return None

    # 4. Progress bar
    total_dur = _probe_duration(concat)
    with_bar = TMP_DIR / "cartoon_with_bar.mp4"
    if not _add_progress_bar(concat, total_dur, with_bar):
        return None

    # 5. Mux with audio
    output_path = OUTPUT_DIR / f"{script_path.stem}.mp4"
    cmd = [
        "ffmpeg", "-y", "-i", str(with_bar), "-i", str(audio_path),
        "-c:v", "copy", "-c:a", "aac", "-shortest", "-movflags", "+faststart",
        str(output_path),
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=180)
    if r.returncode != 0:
        print(f"      ❌ mux failed: {r.stderr.decode('utf-8', errors='replace')[:200]}")
        return None

    size_kb = output_path.stat().st_size // 1024
    print(f"      ✅ Cartoon video saved: {output_path.name} ({size_kb}KB, {total_dur:.0f}s)")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Flat-cartoon YouTube Short generator")
    parser.add_argument("--script", type=Path, help="Script markdown file")
    parser.add_argument("--audio", type=Path, help="Voiceover MP3 file")
    parser.add_argument("--all", action="store_true", help="Assemble all scripts with audio")
    args = parser.parse_args()

    print("=" * 60)
    print("M.O.T INNOVATION — CARTOON VIDEO ASSEMBLER")
    print("=" * 60)

    if args.all:
        scripts = sorted((SCRIPT_DIR / "scripts").glob("yt_short_*.md"))
        print(f"Found {len(scripts)} YouTube Short scripts\n")
        done = 0
        for s in scripts:
            out = OUTPUT_DIR / f"{s.stem}.mp4"
            if _is_valid_video(out):
                print(f"  ⏭️  {s.name} — video exists, skipping")
                continue
            if assemble_cartoon(s):
                done += 1
        print(f"\nAssembled {done} cartoon video(s)")
        return 0

    if args.script:
        return 0 if assemble_cartoon(args.script, args.audio) else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
