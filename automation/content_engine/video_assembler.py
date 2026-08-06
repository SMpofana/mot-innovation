#!/usr/bin/env python
"""
video_assembler.py — Assembles faceless YouTube Short videos from scripts + audio

Uses ffmpeg directly (fast, no moviepy overhead) to combine a text-overlay
background image with voiceover audio into a vertical MP4 (720x1280).

Usage:
    python video_assembler.py --script scripts/yt_short_*.md --audio audio/yt_short_*.mp3
    python video_assembler.py --all
    python video_assembler.py --all --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "videos"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WIDTH = 720
HEIGHT = 1280
BG_COLOR = (10, 10, 10)
TEXT_COLOR = (245, 241, 235)
MUTED_COLOR = (138, 138, 138)


def find_audio_for_script(script_path: Path) -> Path | None:
    """Find the matching voiceover audio file for a script."""
    audio_dir = SCRIPT_DIR / "audio"
    if not audio_dir.exists():
        return None
    stem = script_path.stem
    audio_path = audio_dir / f"{stem}.mp3"
    if audio_path.exists():
        return audio_path
    matches = list(audio_dir.glob(f"{stem}*.mp3"))
    return matches[0] if matches else None


def create_text_image(text: str, output_path: Path, font_size: int = 48) -> Path:
    """Create a dark background image with centered text using Pillow."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    # Word wrap
    lines = []
    words = text.split()
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] > WIDTH - 80:
            if current_line:
                lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)

    # Center text vertically
    line_height = font_size + 12
    total_height = len(lines) * line_height
    y_start = (HEIGHT - total_height) // 2

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        x = (WIDTH - (bbox[2] - bbox[0])) // 2
        y = y_start + i * line_height
        draw.text((x, y), line, fill=TEXT_COLOR, font=font)

    img.save(str(output_path), quality=95)
    return output_path


def assemble_video(script_data: dict, audio_path: Path, output_path: Path) -> Path | None:
    """Assemble a video using ffmpeg directly (fast, no moviepy needed)."""
    # Get the primary text overlay from the script scenes
    scenes = script_data.get("scenes", [])
    text = "M.O.T Innovation"
    if scenes:
        overlays = scenes[0].get("overlays", [])
        if overlays:
            text = overlays[0]
        elif len(scenes) > 2 and scenes[2].get("overlays"):
            text = scenes[2]["overlays"][0]

    print(f"   🎬 Assembling video from {audio_path.name}...")
    print(f"      Text: {text[:60]}")

    # Create background image
    bg_path = OUTPUT_DIR / f"_bg_{output_path.stem}.png"
    create_text_image(text, bg_path)

    # Use ffmpeg to combine image + audio into video
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(bg_path),
        "-i", str(audio_path),
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-movflags", "+faststart",
        str(output_path)
    ]

    print(f"      📐 Output: {WIDTH}x{HEIGHT} vertical")
    result = subprocess.run(cmd, capture_output=True, timeout=120)

    if result.returncode != 0:
        print(f"      ❌ ffmpeg failed: {result.stderr.decode('utf-8', errors='replace')[:200]}")
        # Try cleaning up
        bg_path.unlink(missing_ok=True)
        return None

    # Cleanup temp image
    bg_path.unlink(missing_ok=True)

    size_kb = output_path.stat().st_size // 1024
    print(f"      ✅ Video saved: {output_path.name} ({size_kb}KB)")
    return output_path


def parse_script(md_path: Path) -> dict[str, Any]:
    """Parse a YouTube Short script markdown file for scenes and metadata."""
    content = md_path.read_text(encoding="utf-8")

    title_match = re.search(r'\*\*Title:\*\*\s*(.+)', content)
    title = title_match.group(1).strip() if title_match else md_path.stem

    desc_match = re.search(r'\*\*Description:\*\*\s*(.+)', content)
    description = desc_match.group(1).strip() if desc_match else ""

    tags_match = re.search(r'\*\*Tags:\*\*\s*(.+)', content)
    tags = tags_match.group(1).strip() if tags_match else ""

    utm_match = re.search(r'\*\*UTM Link:\*\*\s*(.+)', content)
    utm_link = utm_match.group(1).strip() if utm_match else ""

    hashtag_match = re.search(r'\*\*Hashtags:\*\*\s*(.+)', content)
    hashtags = hashtag_match.group(1).strip() if hashtag_match else ""

    # Parse scenes for overlays
    scenes = []
    scene_pattern = re.findall(
        r'##\s+(?:Hook|Problem Agitation|Solution|CTA)\s*\((\d+-\d+s)\)\s*\n+'
        r'\*\*Visual:\*\*\s*\n```\s*\n(.+?)\n```\s*\n+'
        r'\*\*Voiceover:\*\*\s*\n```\s*\n(.+?)\n```',
        content, re.DOTALL
    )

    for timing, visual, voiceover in scene_pattern:
        overlays = re.findall(r'\[VISUAL: Text overlay — "(.+?)"\]', visual)
        scenes.append({
            "timing": timing,
            "overlays": overlays,
            "voiceover": voiceover.strip(),
        })

    return {
        "title": title,
        "description": description,
        "tags": tags,
        "utm_link": utm_link,
        "hashtags": hashtags,
        "scenes": scenes,
        "file_path": str(md_path),
    }


def assemble_from_files(script_path: Path, audio_path: Path | None = None) -> Path | None:
    """Assemble a video from a script file and optional audio file."""
    if not audio_path:
        audio_path = find_audio_for_script(script_path)
    if not audio_path:
        print(f"   ⚠️  No audio found for {script_path.name}")
        return None

    script_data = parse_script(script_path)
    output_path = OUTPUT_DIR / f"{script_path.stem}.mp4"

    if output_path.exists():
        print(f"   ⏭️  Video already exists: {output_path.name}")
        return output_path

    return assemble_video(script_data, audio_path, output_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Assemble faceless YouTube Short videos from scripts + audio"
    )
    parser.add_argument("--script", type=Path, help="Script markdown file")
    parser.add_argument("--audio", type=Path, help="Voiceover MP3 file")
    parser.add_argument("--all", action="store_true", help="Assemble all scripts with audio")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created")
    args = parser.parse_args()

    print("=" * 60)
    print("M.O.T INNOVATION — VIDEO ASSEMBLER")
    print("=" * 60)

    if args.all:
        scripts_dir = SCRIPT_DIR / "scripts"
        scripts = sorted(scripts_dir.glob("yt_short_*.md"))
        print(f"Found {len(scripts)} YouTube Short scripts\n")

        assembled = 0
        for script_path in scripts:
            audio_path = find_audio_for_script(script_path)
            if not audio_path:
                print(f"  ⏭️  {script_path.name} — no audio, skipping")
                continue

            output_path = OUTPUT_DIR / f"{script_path.stem}.mp4"
            if output_path.exists():
                print(f"  ⏭️  {script_path.name} — video exists, skipping")
                continue

            if args.dry_run:
                print(f"  📹 Would create: {output_path.name}")
                assembled += 1
            else:
                result = assemble_from_files(script_path, audio_path)
                if result:
                    assembled += 1

        print(f"\n{'Would assemble' if args.dry_run else 'Assembled'} {assembled} video(s)")
        return 0

    if args.script:
        result = assemble_from_files(args.script, args.audio)
        return 0 if result else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())