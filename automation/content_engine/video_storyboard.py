#!/usr/bin/env python
"""
video_storyboard.py — M.O.T Innovation Video Storyboard Generator

Generates a storyboard JSON for each script with:
    - Scene timings (0-5s hook, 5-15s problem, 15-45s solution, 45-60s CTA)
    - Visual cues (stock footage queries for Pexels, text overlays, screen recording instructions)
    - CapCut assembly instructions (what clips to use, transitions, text overlays)
    - Thumbnail design spec (Canva template description)

Usage:
    # Generate storyboard from a script file
    python video_storyboard.py --script scripts/yt_short_disconnected_tools_20250101_120000.md

    # Generate from pain point + service (creates script first if needed)
    python video_storyboard.py --pain-point disconnected_tools --service dam

    # Generate storyboards for all scripts in the scripts/ directory
    python video_storyboard.py --all
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from data import (  # noqa: E402
    BRAND_NAME, WEBSITE_URL,
    PAIN_POINTS, SERVICES, CASE_STUDIES,
    get_pain_point, get_service, case_studies_for_service,
)

STORYBOARD_DIR = SCRIPT_DIR / "storyboards"
STORYBOARD_DIR.mkdir(parents=True, exist_ok=True)

SCRIPTS_DIR = SCRIPT_DIR / "scripts"

# Pexels stock footage search queries by pain point
PEXELS_QUERIES = {
    "disconnected_tools": ["messy desk computer cables", "frustrated office worker computer", "software integration dashboard", "marketing technology stack"],
    "manual_posting": ["social media phone typing", "person multiple phones social media", "social media scheduling app", "content creation workflow"],
    "scattered_assets": ["messy computer files folders", "disorganized desk paperwork", "digital file management", "cloud storage organization"],
    "manual_reporting": ["spreadsheet data analysis tired", "business analytics dashboard", "financial reports paperwork", "data visualization screen"],
    "wasting_ad_spend": ["money waste advertising", "digital marketing analytics screen", "ad campaign optimization", "business growth chart"],
    "want_builder_not_advisor": ["construction building process", "engineer working blueprint", "team collaboration project", "professional working system"],
    "custom": ["marketing business technology", "office workflow professional", "digital transformation", "business growth success"],
}


def generate_storyboard(pain_point: dict, service: dict, script_path: Path | None = None,
                        case_study: dict | None = None) -> dict:
    """
    Generate a complete storyboard for a YouTube Short video.

    Args:
        pain_point: Pain point dict from data.py.
        service: Service dict from data.py.
        script_path: Optional path to the script markdown file.
        case_study: Optional case study to reference.

    Returns:
        A storyboard dict with scenes, visual cues, CapCut instructions, and thumbnail spec.
    """
    pp_id = pain_point["id"]
    pp_title = pain_point["title"]
    pp_stat = pain_point["stat"]
    svc_name = service["name"]
    svc_short = service["short"]
    svc_deliverable = service["deliverable"]

    # Stock footage queries
    queries = PEXELS_QUERIES.get(pp_id, PEXELS_QUERIES["custom"])

    # Case study reference
    cs = case_study
    if not cs:
        cs_list = case_studies_for_service(service["id"])
        cs = cs_list[0] if cs_list else None

    # ── Scenes ───────────────────────────────────────────────────────────────
    scenes = [
        {
            "scene_number": 1,
            "name": "Hook",
            "timing": {"start": 0, "end": 5, "duration_seconds": 5},
            "visual_cues": {
                "type": "text_overlay",
                "description": f"Bold text on dark/black background — \"{pp_title}\"",
                "text_overlay": pp_title,
                "animation": "Fast zoom-in, dramatic music sting, slight shake effect",
                "stock_footage_queries": queries[0:1],
                "screen_recording": None,
                "pexels_search_url": f"https://www.pexels.com/search/videos/{queries[0].replace(' ', '%20')}/",
            },
            "voiceover": f"{pp_title}.",
            "text_overlay": pp_title,
            "text_position": "center",
            "text_animation": "zoom_in_fast",
            "music": "Dramatic intro sting, then cuts to background track",
        },
        {
            "scene_number": 2,
            "name": "Problem Agitation",
            "timing": {"start": 5, "end": 15, "duration_seconds": 10},
            "visual_cues": {
                "type": "stock_footage_with_overlay",
                "description": "Split screen or quick cuts — messy folders, multiple browser tabs, frustrated person at desk",
                "text_overlay": pp_stat,
                "animation": "Quick cuts every 2-3 seconds, slight desaturation for 'problem' mood",
                "stock_footage_queries": queries[1:3],
                "screen_recording": "Screen recording of messy file folders or disconnected apps (optional)",
                "pexels_search_urls": [f"https://www.pexels.com/search/videos/{q.replace(' ', '%20')}/" for q in queries[1:3]],
            },
            "voiceover": f"{pain_point['summary']} {pp_stat}",
            "text_overlay": pp_stat,
            "text_position": "bottom_third",
            "text_animation": "fade_in",
            "music": "Tense, slightly dissonant background track",
            "color_grading": "Slightly desaturated, cool tones",
        },
        {
            "scene_number": 3,
            "name": "Solution",
            "timing": {"start": 15, "end": 45, "duration_seconds": 30},
            "visual_cues": {
                "type": "screen_recording_and_stock",
                "description": f"Clean dashboard interface, organized asset library, automated workflow diagram. Screen recording of {svc_short} system in action.",
                "text_overlay": svc_deliverable,
                "animation": "Smooth pan across dashboard, zoom into key features, before/after transition",
                "stock_footage_queries": queries[2:4],
                "screen_recording": f"Record {svc_short} dashboard demo — show the actual system working. Use OBS Studio. 15-20 second clip.",
                "pexels_search_urls": [f"https://www.pexels.com/search/videos/{q.replace(' ', '%20')}/" for q in queries[2:4]],
                "before_after": {
                    "before": "Messy, scattered assets / manual posting / no dashboard",
                    "after": f"Clean, organized {svc_short} system — automated, visual, connected",
                },
            },
            "voiceover": f"{service['angle']} {BRAND_NAME} builds {svc_name}. {svc_deliverable}.",
            "text_overlay": svc_deliverable,
            "text_position": "top_third",
            "text_animation": "slide_up_fade",
            "music": "Uplifting, professional background track — more energy",
            "color_grading": "Full color, warm professional tones",
            "case_study_overlay": {
                "text": cs["result_stat"] if cs else None,
                "client": cs["client"] if cs else None,
                "result": cs["result"] if cs else None,
                "animation": "Slide in from right, hold 3 seconds",
            } if cs else None,
        },
        {
            "scene_number": 4,
            "name": "CTA",
            "timing": {"start": 45, "end": 60, "duration_seconds": 15},
            "visual_cues": {
                "type": "logo_and_text",
                "description": f"{BRAND_NAME} logo on dark background with website URL and CTA button",
                "text_overlay": "Book a Free Consultation",
                "url_overlay": WEBSITE_URL,
                "animation": "Logo fades in, text slides up, subtle pulse on CTA",
                "stock_footage_queries": [],
                "screen_recording": None,
            },
            "voiceover": f"Book a free consultation at motinnovation.co.za. We don't build slide decks — we build working systems. Link in the description.",
            "text_overlay": "Book a Free Consultation",
            "text_position": "center",
            "text_animation": "fade_in_pulse",
            "music": "Music swells then resolves on final beat",
        },
    ]

    # ── CapCut assembly instructions ─────────────────────────────────────────
    capcut_instructions = {
        "platform": "CapCut Desktop (free)",
        "aspect_ratio": "9:16 (vertical, 1080x1920 for YouTube Shorts)",
        "total_duration": "60 seconds",
        "fps": "30",
        "steps": [
            {
                "step": 1,
                "action": "Import media",
                "details": f"Download stock footage from Pexels (links in storyboard JSON). Record screen for Solution section using OBS Studio.",
            },
            {
                "step": 2,
                "action": "Add voiceover",
                "details": "Import the generated MP3 voiceover from audio/ directory. Align voiceover to scene timings.",
            },
            {
                "step": 3,
                "action": "Place clips on timeline",
                "details": "Scene 1 (0-5s): Dark background text clip. Scene 2 (5-15s): Problem stock footage. Scene 3 (15-45s): Screen recording + solution stock footage. Scene 4 (45-60s): Logo + CTA card.",
            },
            {
                "step": 4,
                "action": "Add transitions",
                "details": "Scene 1→2: Hard cut. Scene 2→3: Whip pan transition. Scene 3→4: Fade to black then logo fade-in.",
                "transitions": [
                    {"from_scene": 1, "to_scene": 2, "type": "hard_cut"},
                    {"from_scene": 2, "to_scene": 3, "type": "whip_pan"},
                    {"from_scene": 3, "to_scene": 4, "type": "fade_to_black"},
                ],
            },
            {
                "step": 5,
                "action": "Add text overlays",
                "details": f"Scene 1: \"{pp_title}\" (center, large, white on black). Scene 2: \"{pp_stat}\" (bottom third). Scene 3: \"{svc_deliverable}\" (top third). Scene 4: \"Book a Free Consultation\" + URL (center).",
                "text_overlays": [
                    {"scene": 1, "text": pp_title, "position": "center", "font": "Bold Sans", "size": "Large", "color": "#FFFFFF", "bg_color": "#000000"},
                    {"scene": 2, "text": pp_stat, "position": "bottom_third", "font": "Medium Sans", "size": "Medium", "color": "#FFFFFF", "bg_color": "#000000CC"},
                    {"scene": 3, "text": svc_deliverable, "position": "top_third", "font": "Medium Sans", "size": "Medium", "color": "#FFFFFF", "bg_color": "#000000CC"},
                    {"scene": 4, "text": "Book a Free Consultation", "position": "center", "font": "Bold Sans", "size": "Large", "color": "#FFFFFF", "bg_color": "#000000"},
                ],
            },
            {
                "step": 6,
                "action": "Add music",
                "details": "Background track: professional, building energy. Scene 1: dramatic sting. Scene 2: tense. Scene 3: uplifting. Scene 4: resolve. Use CapCut's free audio library or import royalty-free track.",
            },
            {
                "step": 7,
                "action": "Add auto-captions",
                "details": "Use CapCut's Auto Caption feature (free). Set to English. Style: white text with black outline, bottom center. This is critical for faceless content engagement.",
            },
            {
                "step": 8,
                "action": "Export",
                "details": "Export as MP4, 1080x1920, 30fps, H.264. File size target: <100MB for YouTube Shorts upload.",
            },
        ],
    }

    # ── Thumbnail design spec ────────────────────────────────────────────────
    thumbnail_spec = {
        "tool": "Canva (free)",
        "dimensions": "1280x720 (YouTube thumbnail) — also create 1080x1920 version for Shorts cover",
        "template": "Dark monochrome background (trionn-style)",
        "design_elements": [
            {
                "element": "Background",
                "spec": "Dark charcoal (#0a0a0a) with subtle gradient or grain texture",
            },
            {
                "element": "Main text",
                "spec": f"\"{pp_stat}\" — Bold, large, white text, centered. Font: Montserrat Bold or similar.",
            },
            {
                "element": "Secondary text",
                "spec": f"\"{pp_title}\" — Smaller, gray (#999), below main text.",
            },
            {
                "element": "Logo",
                "spec": f"{BRAND_NAME} logo, bottom right corner, small",
            },
            {
                "element": "Accent",
                "spec": "Thin accent line or geometric shape in brand accent color (white or electric blue)",
            },
        ],
        "canva_search": "Search Canva for 'dark minimalist YouTube thumbnail' template",
        "color_palette": ["#0a0a0a", "#FFFFFF", "#999999", "#3B82F6"],
        "style_notes": "Minimalist, high contrast. No clutter. The stat text should be readable at thumbnail size.",
    }

    # ── Full storyboard ───────────────────────────────────────────────────────
    storyboard = {
        "metadata": {
            "title": f"YouTube Short Storyboard — {pp_title}",
            "pain_point_id": pp_id,
            "pain_point": pp_title,
            "service_id": service["id"],
            "service_name": svc_name,
            "case_study": cs["client"] if cs else None,
            "script_path": str(script_path) if script_path else None,
            "generated_at": datetime.now().isoformat(),
            "platform": "YouTube Shorts",
            "duration_seconds": 60,
            "aspect_ratio": "9:16",
        },
        "scenes": scenes,
        "capcut_assembly": capcut_instructions,
        "thumbnail_design": thumbnail_spec,
        "pexels_footage_links": {
            f"scene_{s['scene_number']}": s["visual_cues"].get("pexels_search_urls") or s["visual_cues"].get("pexels_search_url")
            for s in scenes
            if s["visual_cues"].get("pexels_search_urls") or s["visual_cues"].get("pexels_search_url")
        },
    }

    return storyboard


def save_storyboard(storyboard: dict, output_dir: Path | None = None) -> Path:
    """Save a storyboard as JSON. Returns the file path."""
    if output_dir is None:
        output_dir = STORYBOARD_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    pp_id = storyboard["metadata"]["pain_point_id"]
    filename = f"storyboard_{pp_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = output_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(storyboard, f, indent=2, ensure_ascii=False)

    return filepath


# ── CLI ──────────────────────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(
        description="M.O.T Innovation — Video Storyboard Generator"
    )
    parser.add_argument("--script", type=str, default=None,
                        help="Path to a script markdown file to generate storyboard from")
    parser.add_argument("--pain-point", type=str, default=None,
                        help="Pain point ID (generates storyboard directly)")
    parser.add_argument("--service", type=str, default=None,
                        help="Service ID (used with --pain-point)")
    parser.add_argument("--all", action="store_true",
                        help="Generate storyboards for all scripts in scripts/ directory")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Output directory for storyboards (default: storyboards/)")
    args = parser.parse_args()

    print(f"\n{'=' * 60}")
    print(f"VIDEO STORYBOARD GENERATOR — {BRAND_NAME}")
    print(f"{'=' * 60}")

    output_dir = Path(args.output_dir) if args.output_dir else STORYBOARD_DIR

    if args.all:
        # Generate storyboards for all scripts
        scripts_dir = SCRIPTS_DIR
        if not scripts_dir.exists():
            print(f"❌ Scripts directory not found: {scripts_dir}")
            return 1

        script_files = list(scripts_dir.glob("yt_short_*.md"))
        if not script_files:
            print(f"❌ No YouTube Short scripts found in {scripts_dir}")
            return 1

        print(f"📁 Found {len(script_files)} scripts to process\n")
        count = 0
        for script_file in script_files:
            print(f"📋 Processing: {script_file.name}")
            # Try to extract pain point and service from filename
            # Filename: yt_short_<pain_point>_<timestamp>.md
            name_parts = script_file.stem.split("_")
            # Try to match pain point
            pp = None
            for p in PAIN_POINTS:
                if p["id"] in script_file.stem:
                    pp = p
                    break
            if not pp:
                pp = PAIN_POINTS[0]

            svc = None
            for s in SERVICES.values():
                if s["id"] in script_file.stem:
                    svc = s
                    break
            if not svc:
                matched = [s for s in SERVICES.values() if pp["id"] in s["keywords"]]
                svc = matched[0] if matched else SERVICES["dam"]

            storyboard = generate_storyboard(pp, svc, script_file)
            filepath = save_storyboard(storyboard, output_dir)
            print(f"   ✅ Saved: {filepath}\n")
            count += 1

        print(f"✅ Generated {count} storyboard(s) in {output_dir}")
        return 0

    if args.script:
        script_path = Path(args.script)
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            return 1

        # Try to detect pain point and service from script content
        content = script_path.read_text(encoding="utf-8")
        pp = None
        for p in PAIN_POINTS:
            if p["id"] in content or p["title"] in content:
                pp = p
                break
        if not pp:
            pp = PAIN_POINTS[0]

        svc = None
        for s in SERVICES.values():
            if s["id"] in content or s["name"] in content:
                svc = s
                break
        if not svc:
            matched = [s for s in SERVICES.values() if pp["id"] in s["keywords"]]
            svc = matched[0] if matched else SERVICES["dam"]

        print(f"📋 Script: {script_path.name}")
        print(f"   Pain Point: {pp['title']}")
        print(f"   Service: {svc['name']}")

        storyboard = generate_storyboard(pp, svc, script_path)
        filepath = save_storyboard(storyboard, output_dir)
        print(f"\n✅ Storyboard saved: {filepath}")
        return 0

    if args.pain_point:
        pp = get_pain_point(args.pain_point)
        if args.service:
            svc = get_service(args.service)
        else:
            matched = [s for s in SERVICES.values() if pp["id"] in s["keywords"]]
            svc = matched[0] if matched else SERVICES["dam"]

        print(f"   Pain Point: {pp['title']}")
        print(f"   Service: {svc['name']}")

        storyboard = generate_storyboard(pp, svc)
        filepath = save_storyboard(storyboard, output_dir)
        print(f"\n✅ Storyboard saved: {filepath}")
        return 0

    print("Error: provide --script, --pain-point, or --all.")
    return 1


if __name__ == "__main__":
    sys.exit(main())