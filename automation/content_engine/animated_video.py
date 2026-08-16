#!/usr/bin/env python
"""
animated_video.py — Animated faceless YouTube Short generator.

Builds motion-rich vertical videos (720x1280) from a script + voiceover,
matching the M.O.T trionn monochrome aesthetic:

  - Ken Burns zoom/pan on every scene (zoompan)
  - Crossfade transitions between scenes (xfade)
  - Cream serif headline text on near-black, with plus-cross motifs
  - A thin progress bar that grows across the bottom
  - Scene counter + brand mark

Requires ffmpeg with zoompan + xfade (verified on ffmpeg 8.1.2).

Usage:
    python animated_video.py --script scripts/yt_short_*.md --audio audio/yt_short_*.mp3
    python animated_video.py --all
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "videos"
TMP_DIR = SCRIPT_DIR / "videos" / "_anim_tmp"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

WIDTH, HEIGHT = 720, 1280
FPS = 30
BG = (10, 10, 10)          # near-black
CREAM = (245, 241, 235)    # cream text
MUTED = (138, 138, 138)    # muted grey
ACCENT = (245, 241, 235)   # cream accent

# Editorial serif for headlines, sans for small labels
SERIF = "C:/Windows/Fonts/georgia.ttf"
SERIF_BOLD = "C:/Windows/Fonts/georgiab.ttf"
SANS = "C:/Windows/Fonts/arial.ttf"


# ── Script parsing ────────────────────────────────────────────────────────────

def parse_script(md_path: Path) -> dict[str, Any]:
    """Parse a YouTube Short script into scenes with timings + overlays."""
    content = md_path.read_text(encoding="utf-8")

    title_match = re.search(r"\*\*Title:\*\*\s*(.+)", content)
    title = title_match.group(1).strip() if title_match else md_path.stem

    # Scenes: ## Name (start-end s) with Visual + Voiceover blocks
    scenes = []
    scene_pattern = re.findall(
        r"##\s+(Hook|Problem Agitation|Solution|CTA)\s*\((\d+)-(\d+)s\)\s*\n+"
        r"\*\*Visual:\*\*\s*\n```\s*\n(.+?)\n```\s*\n+"
        r"\*\*Voiceover:\*\*\s*\n```\s*\n(.+?)\n```",
        content, re.DOTALL,
    )
    for name, start, end, visual, voiceover in scene_pattern:
        # Extract text overlays from [VISUAL: Text overlay — "..."], else the
        # first quoted phrase in the visual block.
        overlays = re.findall(r'Text overlay — "(.+?)"', visual)
        if not overlays:
            quoted = re.findall(r'"(.+?)"', visual)
            overlays = quoted[:1]
        scenes.append({
            "name": name,
            "start": int(start),
            "end": int(end),
            "duration": int(end) - int(start),
            "overlays": overlays,
            "voiceover": voiceover.strip(),
        })

    return {"title": title, "scenes": scenes, "file_path": str(md_path)}


# ── Scene background generation (Pillow) ────────────────────────────────────

def _draw_plus(draw, x, y, size, color, width=1):
    """Draw a plus-cross motif at (x, y)."""
    half = size // 2
    draw.line([(x - half, y), (x + half, y)], fill=color, width=width)
    draw.line([(x, y - half), (x, y + half)], fill=color, width=width)


def create_scene_image(scene: dict, idx: int, total: int, out_path: Path) -> Path:
    """Render a scene's background: headline text + plus-crosses + counter."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    # Corner plus-crosses (trionn motif)
    for cx, cy in [(40, 40), (WIDTH - 40, 40), (40, HEIGHT - 40), (WIDTH - 40, HEIGHT - 40)]:
        _draw_plus(draw, cx, cy, 18, MUTED, 1)

    # Scene label (small caps sans, top)
    try:
        label_font = ImageFont.truetype(SANS, 22)
    except Exception:
        label_font = ImageFont.load_default()
    label = f"{scene['name'].upper()}  /  {idx + 1:02d}"
    draw.text((WIDTH // 2, 90), label, font=label_font, fill=MUTED, anchor="mm")

    # Headline text (serif, centered, wrapped)
    try:
        head_font = ImageFont.truetype(SERIF_BOLD, 64)
    except Exception:
        head_font = ImageFont.load_default()

    text = scene["overlays"][0] if scene["overlays"] else scene["name"]
    lines = _wrap(draw, text, head_font, WIDTH - 120)
    line_h = 78
    total_h = len(lines) * line_h
    y = (HEIGHT - total_h) // 2 - 40
    for line in lines:
        draw.text((WIDTH // 2, y), line, font=head_font, fill=CREAM, anchor="mm")
        y += line_h

    # Small brand mark at bottom
    try:
        brand_font = ImageFont.truetype(SANS, 20)
    except Exception:
        brand_font = ImageFont.load_default()
    draw.text((WIDTH // 2, HEIGHT - 90), "M.O.T INNOVATION", font=brand_font,
              fill=MUTED, anchor="mm")

    img.save(str(out_path), quality=95)
    return out_path


def _wrap(draw, text: str, font, max_width: int) -> list[str]:
    """Word-wrap text to fit max_width."""
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


# ── ffmpeg assembly ──────────────────────────────────────────────────────────

def _ken_burns_clip(bg_path: Path, duration: float, out_path: Path,
                    zoom_in: bool = True) -> bool:
    """Render one scene as a Ken Burns clip (slow zoom/pan)."""
    # Scale to 2x for zoompan headroom (avoids jitter) — 8000px is far too
    # heavy on memory-constrained machines. 2x is plenty for a 1.0->1.35 zoom.
    z = "min(zoom+0.0012,1.35)" if zoom_in else "max(zoom-0.0012,1.0)"
    x = "iw/2-(iw/zoom/2)"
    y = "ih/2-(ih/zoom/2)"
    vf = (
        f"scale=1440:2560,"
        f"zoompan=z='{z}':d={int(duration * FPS)}:"
        f"x='{x}':y='{y}':s={WIDTH}x{HEIGHT}:fps={FPS}"
    )
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(bg_path), "-t", str(duration),
        "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
        str(out_path),
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=180)
    if r.returncode != 0:
        print(f"      ❌ ken_burns failed: {r.stderr.decode('utf-8', errors='replace')[:200]}")
        return False
    return True


def _concat_with_xfade(clips: list[Path], out_path: Path, transition: float = 0.5) -> bool:
    """Concatenate clips with crossfade transitions."""
    if not clips:
        return False
    if len(clips) == 1:
        import shutil
        shutil.copyfile(clips[0], out_path)
        return True

    # Build filter_complex with xfade between consecutive clips.
    inputs = []
    for c in clips:
        inputs += ["-i", str(c)]
    n = len(clips)
    # Each clip's duration (approx from fps*frames); we pass -t per input via
    # the filter using the clip length. Use xfade offsets.
    # Get durations via ffprobe.
    durations = [_probe_duration(c) for c in clips]
    total = sum(durations)
    # xfade offset for transition i = cumulative duration up to clip i, minus
    # i*transition (each transition overlaps).
    filters = []
    prev = "0:v"
    offset = 0.0
    for i in range(1, n):
        offset += durations[i - 1] - transition
        out_label = f"v{i}"
        filters.append(
            f"[{prev}][{i}:v]xfade=transition=fade:duration={transition}:"
            f"offset={offset:.3f}[{out_label}]"
        )
        prev = out_label
    fc = ";".join(filters)
    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", fc,
        "-map", f"[{prev}]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(FPS),
        str(out_path),
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=300)
    if r.returncode != 0:
        print(f"      ❌ xfade concat failed: {r.stderr.decode('utf-8', errors='replace')[:300]}")
        return False
    return True


def _probe_duration(path: Path) -> float:
    """Return video duration in seconds via ffprobe."""
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, timeout=30,
    )
    try:
        return float(r.stdout.decode().strip())
    except (ValueError, AttributeError):
        return 0.0


def _add_progress_bar(video_path: Path, duration: float, out_path: Path) -> bool:
    """Overlay a thin progress bar that grows across the bottom."""
    vf = (
        f"drawbox=x=0:y=ih-8:w='iw*t/{duration:.3f}':h=8:"
        f"color=white@0.85:t=fill"
    )
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path), "-vf", vf,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "copy",
        str(out_path),
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=180)
    if r.returncode != 0:
        print(f"      ❌ progress bar failed: {r.stderr.decode('utf-8', errors='replace')[:200]}")
        return False
    return True


# ── Public API ───────────────────────────────────────────────────────────────

def assemble_animated(script_path: Path, audio_path: Path | None = None) -> Path | None:
    """Assemble an animated video from a script + audio. Returns output path."""
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

    print(f"   🎬 Animating {len(scenes)} scenes from {audio_path.name}...")

    # 1. Render each scene background
    bg_paths = []
    for i, scene in enumerate(scenes):
        bg = TMP_DIR / f"bg_{i:02d}.png"
        create_scene_image(scene, i, len(scenes), bg)
        bg_paths.append(bg)

    # 2. Ken Burns clip per scene
    clips = []
    for i, (scene, bg) in enumerate(zip(scenes, bg_paths)):
        clip = TMP_DIR / f"clip_{i:02d}.mp4"
        if _ken_burns_clip(bg, scene["duration"], clip, zoom_in=(i % 2 == 0)):
            clips.append(clip)

    if not clips:
        print("   ❌ No clips generated")
        return None

    # 3. Crossfade concat
    concat = TMP_DIR / "concat.mp4"
    if not _concat_with_xfade(clips, concat):
        return None

    # 4. Progress bar
    total_dur = _probe_duration(concat)
    with_bar = TMP_DIR / "with_bar.mp4"
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
    print(f"      ✅ Animated video saved: {output_path.name} ({size_kb}KB, {total_dur:.0f}s)")
    return output_path


def _find_audio(script_path: Path) -> Path | None:
    audio_dir = SCRIPT_DIR / "audio"
    if not audio_dir.exists():
        return None
    stem = script_path.stem
    p = audio_dir / f"{stem}.mp3"
    if p.exists():
        return p
    matches = list(audio_dir.glob(f"{stem}*.mp3"))
    return matches[0] if matches else None


def _is_valid_video(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        if path.stat().st_size < 10_000:
            return False
        return _probe_duration(path) > 0
    except Exception:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Animated YouTube Short generator")
    parser.add_argument("--script", type=Path, help="Script markdown file")
    parser.add_argument("--audio", type=Path, help="Voiceover MP3 file")
    parser.add_argument("--all", action="store_true", help="Assemble all scripts with audio")
    args = parser.parse_args()

    print("=" * 60)
    print("M.O.T INNOVATION — ANIMATED VIDEO ASSEMBLER")
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
            if assemble_animated(s):
                done += 1
        print(f"\nAssembled {done} animated video(s)")
        return 0

    if args.script:
        return 0 if assemble_animated(args.script, args.audio) else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
