#!/usr/bin/env python
"""
run_content_engine.py — M.O.T Innovation Master Content Engine Runner

Orchestrates the full faceless content pipeline:
    1. Scan Reddit for new pain points (or use existing knowledge base)
    2. Generate scripts for the week (YouTube Shorts + LinkedIn posts)
    3. Generate voiceovers from scripts
    4. Generate video storyboards from scripts
    5. Generate LinkedIn carousels from pain points
    6. Update the content calendar
    7. Output a summary of everything created

Usage:
    # Full pipeline run (one week of content)
    python run_content_engine.py

    # Scan Reddit first, then run pipeline
    python run_content_engine.py --scan-reddit

    # Generate for a specific pain point
    python run_content_engine.py --pain-point disconnected_tools --service dam

    # Skip voiceover generation (if edge-tts/ElevenLabs not available)
    python run_content_engine.py --skip-voiceover

    # Dry run — show what would be generated without creating files
    python run_content_engine.py --dry-run

    # Verbose output
    python run_content_engine.py --verbose
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from data import (  # noqa: E402
    BRAND_NAME, WEBSITE_URL,
    PAIN_POINTS, SERVICES, CASE_STUDIES,
    get_pain_point, get_service, case_studies_for_service,
)

# Import pipeline modules
from script_generator import generate_youtube_short, generate_linkedin_post  # noqa: E402
from video_storyboard import generate_storyboard, save_storyboard  # noqa: E402
from linkedin_carousel import generate_carousel, save_carousel  # noqa: E402
from content_calendar import generate_calendar, save_csv, save_json, print_calendar  # noqa: E402

# Output directories (all relative to content_engine/)
SCRIPTS_DIR = SCRIPT_DIR / "scripts"
AUDIO_DIR = SCRIPT_DIR / "audio"
STORYBOARDS_DIR = SCRIPT_DIR / "storyboards"
CAROUSELS_DIR = SCRIPT_DIR / "carousels"
CALENDAR_DIR = SCRIPT_DIR / "calendar"
SUMMARY_DIR = SCRIPT_DIR / "summaries"

for d in [SCRIPTS_DIR, AUDIO_DIR, STORYBOARDS_DIR, CAROUSELS_DIR, CALENDAR_DIR, SUMMARY_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ── Reddit scanning ───────────────────────────────────────────────────────────
def scan_reddit_pain_points() -> list[dict]:
    """
    Scan Reddit for marketing pain points using the existing content_pipeline.py.

    Falls back to the built-in PAIN_POINTS if scanning fails.
    """
    print("── Step 1: Scanning for pain points ──")

    # Try importing the existing content pipeline
    try:
        content_pipeline_path = SCRIPT_DIR.parent / "content_pipeline.py"
        if content_pipeline_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("content_pipeline", content_pipeline_path)
            cp = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cp)

            print("   📡 Scanning Reddit RSS feeds...")
            reddit_posts = cp.scan_reddit()
            existing = cp.load_existing_painpoints()
            all_pp = reddit_posts + existing

            if all_pp:
                print(f"   ✅ Found {len(all_pp)} pain points from Reddit/existing pipeline")

                # Match to services
                matched = cp.match_posts_to_services(all_pp)
                return matched

    except Exception as e:
        print(f"   ⚠️  Reddit scan failed: {e}")

    # Fallback to built-in pain points
    print(f"   📁 Using built-in knowledge base ({len(PAIN_POINTS)} pain points)")
    return [{"id": pp["id"], "title": pp["title"], "summary": pp["summary"],
             "stat": pp["stat"], "matched_service": "general"} for pp in PAIN_POINTS]


# ── Pipeline steps ───────────────────────────────────────────────────────────
def step_generate_scripts(pain_points: list[dict], verbose: bool = False) -> list[dict]:
    """Generate YouTube Short scripts and LinkedIn posts for each pain point."""
    print("\n── Step 2: Generating scripts ──")

    results = []

    for pp_data in pain_points:
        # Find the matching pain point from our knowledge base
        pp = None
        for p in PAIN_POINTS:
            if p["id"] == pp_data.get("id") or p["title"] == pp_data.get("title"):
                pp = p
                break
        if not pp:
            # Create a pain point dict from Reddit data
            pp = {
                "id": pp_data.get("id", "custom"),
                "title": pp_data.get("title", "Marketing challenge"),
                "summary": pp_data.get("summary", pp_data.get("excerpt", "")),
                "stat": pp_data.get("stat", ""),
                "subreddit_keywords": [],
            }

        # Find matching service
        svc_id = pp_data.get("matched_service", "")
        if svc_id and svc_id in SERVICES:
            svc = SERVICES[svc_id]
        else:
            matched = [s for s in SERVICES.values() if pp["id"] in s["keywords"]]
            svc = matched[0] if matched else SERVICES["dam"]

        # Find case study
        cs_list = case_studies_for_service(svc["id"])
        cs = cs_list[0] if cs_list else None

        print(f"   📝 {pp['title']} → {svc['name']}")

        # Generate YouTube Short
        try:
            yt_result = generate_youtube_short(pp, svc, cs)
            results.append(yt_result)
            print(f"      ✅ Short: {yt_result['file_path']}")
            if verbose:
                print(f"         Title: {yt_result['title']}")
        except Exception as e:
            print(f"      ❌ Short failed: {e}")

        # Generate LinkedIn post
        try:
            li_result = generate_linkedin_post(pp, svc, cs)
            results.append(li_result)
            print(f"      ✅ LinkedIn: {li_result['file_path']}")
        except Exception as e:
            print(f"      ❌ LinkedIn failed: {e}")

    print(f"\n   📊 Generated {len(results)} scripts")
    return results


def step_generate_voiceovers(scripts: list[dict], verbose: bool = False) -> list[dict]:
    """Generate voiceovers for YouTube Short scripts."""
    print("\n── Step 3: Generating voiceovers ──")

    from voiceover_generator import generate_from_script

    results = []
    yt_scripts = [s for s in scripts if s.get("type") == "youtube_short"]

    if not yt_scripts:
        print("   ⚠️  No YouTube Short scripts found — skipping voiceover")
        return results

    for script in yt_scripts:
        script_path = Path(script["file_path"])
        print(f"   🎙️  {script_path.name}")

        try:
            audio_path = generate_from_script(script_path)
            if audio_path:
                results.append({
                    "script_file": str(script_path),
                    "audio_file": audio_path,
                    "pain_point": script.get("pain_point"),
                })
                print(f"      ✅ {audio_path}")
            else:
                print(f"      ❌ Voiceover generation failed")
        except Exception as e:
            print(f"      ❌ Error: {e}")

    print(f"\n   📊 Generated {len(results)} voiceovers")
    return results


def step_generate_storyboards(scripts: list[dict], verbose: bool = False) -> list[dict]:
    """Generate video storyboards for YouTube Short scripts."""
    print("\n── Step 4: Generating storyboards ──")

    results = []
    yt_scripts = [s for s in scripts if s.get("type") == "youtube_short"]

    for script in yt_scripts:
        script_path = Path(script["file_path"])

        # Find pain point and service
        pp = get_pain_point(script.get("pain_point_id", PAIN_POINTS[0]["id"]))
        svc = get_service(script.get("service_id", "dam"))
        cs_list = case_studies_for_service(svc["id"])
        cs = cs_list[0] if cs_list else None

        print(f"   🎬 {pp['title']}")

        try:
            storyboard = generate_storyboard(pp, svc, script_path, cs)
            filepath = save_storyboard(storyboard)
            results.append({
                "script_file": str(script_path),
                "storyboard_file": str(filepath),
                "pain_point": pp["title"],
            })
            print(f"      ✅ {filepath}")
        except Exception as e:
            print(f"      ❌ Error: {e}")

    print(f"\n   📊 Generated {len(results)} storyboards")
    return results


def step_generate_carousels(pain_points: list[dict], verbose: bool = False) -> list[dict]:
    """Generate LinkedIn carousels for each pain point."""
    print("\n── Step 5: Generating LinkedIn carousels ──")

    results = []

    # Use up to 3 pain points for carousels (one per case study)
    for i, cs in enumerate(CASE_STUDIES):
        # Find a pain point that matches this case study's services
        pp = None
        svc = None
        for s_id in cs["services"]:
            for p in PAIN_POINTS:
                if s_id in [svc["id"] for svc in SERVICES.values() if p["id"] in svc["keywords"]]:
                    pp = p
                    svc = SERVICES[s_id]
                    break
            if pp:
                break

        if not pp:
            pp = PAIN_POINTS[i % len(PAIN_POINTS)]
            matched = [s for s in SERVICES.values() if pp["id"] in s["keywords"]]
            svc = matched[0] if matched else SERVICES["dam"]

        print(f"   🎠 {pp['title']} → {cs['client']}")

        try:
            carousel = generate_carousel(pp, svc, cs)
            files = save_carousel(carousel)
            results.append({
                "carousel_files": [str(f) for f in files],
                "pain_point": pp["title"],
                "case_study": cs["client"],
            })
            for f in files:
                print(f"      ✅ {f}")
        except Exception as e:
            print(f"      ❌ Error: {e}")

    print(f"\n   📊 Generated {len(results)} carousels")
    return results


def step_update_calendar(scripts: list[dict], verbose: bool = False) -> dict:
    """Generate/update the 30-day content calendar."""
    print("\n── Step 6: Updating content calendar ──")

    # Start from next Monday
    today = datetime.now()
    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    start_date = today + timedelta(days=days_until_monday)

    entries = generate_calendar(start_date, 30)

    # Update with generated script paths
    for entry in entries:
        if entry["status"] == "rest":
            continue
        # Try to find a matching script
        for script in scripts:
            if script.get("pain_point") == entry["pain_point"]:
                if "Short" in entry["content_type"] and script.get("type") == "youtube_short":
                    entry["script_file_path"] = script["file_path"]
                    entry["status"] = "published"
                elif "LinkedIn" in entry["platform"] and script.get("type") == "linkedin_post":
                    entry["script_file_path"] = script["file_path"]
                    entry["status"] = "published"

    # Save
    csv_path = CALENDAR_DIR / "content_calendar.csv"
    json_path = CALENDAR_DIR / "content_calendar.json"
    save_csv(entries, csv_path)
    save_json(entries, json_path)

    print(f"   ✅ CSV:  {csv_path}")
    print(f"   ✅ JSON: {json_path}")

    if verbose:
        print_calendar(entries)

    return {"csv_path": str(csv_path), "json_path": str(json_path), "entries": entries}


# ── Summary ──────────────────────────────────────────────────────────────────
def save_summary(summary: dict) -> Path:
    """Save the pipeline summary as JSON."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = SUMMARY_DIR / f"summary_{timestamp}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    return filepath


def print_summary(summary: dict) -> None:
    """Print a formatted summary of the pipeline run."""
    print(f"\n{'=' * 60}")
    print(f"CONTENT ENGINE — PIPELINE SUMMARY")
    print(f"{'=' * 60}")
    print(f"Run time:      {summary['run_time']}")
    print(f"Pain points:   {summary['pain_points_count']}")
    print(f"Scripts:       {summary['scripts_count']}")
    print(f"Voiceovers:    {summary['voiceovers_count']}")
    print(f"Storyboards:   {summary['storyboards_count']}")
    print(f"Carousels:     {summary['carousels_count']}")
    print(f"Calendar:      {summary['calendar']['csv_path']}")
    print()
    print("Files created:")
    for f in summary.get("all_files", []):
        print(f"  → {f}")
    print(f"\n{'=' * 60}")
    print(f"✅ Content engine run complete!")
    print(f"{'=' * 60}")


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(
        description="M.O.T Innovation — Master Content Engine Runner"
    )
    parser.add_argument("--scan-reddit", action="store_true",
                        help="Scan Reddit for new pain points before generating")
    parser.add_argument("--pain-point", type=str, default=None,
                        help="Generate for a specific pain point ID only")
    parser.add_argument("--service", type=str, default=None,
                        help="Service ID to use (with --pain-point)")
    parser.add_argument("--skip-voiceover", action="store_true",
                        help="Skip voiceover generation")
    parser.add_argument("--skip-storyboard", action="store_true",
                        help="Skip storyboard generation")
    parser.add_argument("--skip-carousel", action="store_true",
                        help="Skip carousel generation")
    parser.add_argument("--skip-calendar", action="store_true",
                        help="Skip content calendar update")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be generated without creating files")
    parser.add_argument("--verbose", action="store_true",
                        help="Verbose output")
    args = parser.parse_args()

    start_time = time.time()

    print(f"\n{'=' * 60}")
    print(f"M.O.T INNOVATION — CONTENT ENGINE")
    print(f"{'=' * 60}")
    print(f"Run started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if args.dry_run:
        print("🔥 DRY RUN — no files will be created\n")
        # Show what would be generated
        pp_list = [get_pain_point(args.pain_point)] if args.pain_point else PAIN_POINTS
        print(f"Would process {len(pp_list)} pain points:")
        for pp in pp_list:
            matched = [s for s in SERVICES.values() if pp["id"] in s["keywords"]]
            svc = matched[0] if matched else SERVICES["dam"]
            cs_list = case_studies_for_service(svc["id"])
            print(f"  • {pp['title']} → {svc['name']}" + (f" (case study: {cs_list[0]['client']})" if cs_list else ""))
            print(f"    Would generate: YouTube Short script, LinkedIn post, voiceover, storyboard, carousel")
        print(f"\nWould generate content calendar for 30 days")
        return 0

    all_files = []

    # Step 1: Pain points
    if args.pain_point:
        pp = get_pain_point(args.pain_point)
        pain_points = [{"id": pp["id"], "title": pp["title"], "summary": pp["summary"], "stat": pp["stat"]}]
        if args.service:
            pain_points[0]["matched_service"] = args.service
        else:
            matched = [s for s in SERVICES.values() if pp["id"] in s["keywords"]]
            pain_points[0]["matched_service"] = matched[0]["id"] if matched else "dam"
        print(f"\n── Step 1: Using specified pain point: {pp['title']} ──")
    elif args.scan_reddit:
        pain_points = scan_reddit_pain_points()
    else:
        # Use built-in pain points
        print("\n── Step 1: Using built-in knowledge base ──")
        pain_points = [
            {"id": pp["id"], "title": pp["title"], "summary": pp["summary"],
             "stat": pp["stat"], "matched_service": ([s for s in SERVICES if pp["id"] in SERVICES[s]["keywords"]] or ["dam"])[0]}
            for pp in PAIN_POINTS
        ]
        print(f"   📁 {len(pain_points)} pain points loaded")

    # Step 2: Generate scripts
    scripts = step_generate_scripts(pain_points, args.verbose)
    for s in scripts:
        all_files.append(s["file_path"])

    # Step 3: Generate voiceovers
    voiceovers = []
    if not args.skip_voiceover:
        voiceovers = step_generate_voiceovers(scripts, args.verbose)
        for v in voiceovers:
            all_files.append(v["audio_file"])

    # Step 4: Generate storyboards
    storyboards = []
    if not args.skip_storyboard:
        storyboards = step_generate_storyboards(scripts, args.verbose)
        for sb in storyboards:
            all_files.append(sb["storyboard_file"])

    # Step 5: Generate carousels
    carousels = []
    if not args.skip_carousel:
        carousels = step_generate_carousels(pain_points, args.verbose)
        for c in carousels:
            all_files.extend(c["carousel_files"])

    # Step 6: Update calendar
    calendar = {"csv_path": "", "json_path": "", "entries": []}
    if not args.skip_calendar:
        calendar = step_update_calendar(scripts, args.verbose)
        all_files.append(calendar["csv_path"])
        all_files.append(calendar["json_path"])

    # Summary
    elapsed = time.time() - start_time
    summary = {
        "run_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
        "pain_points_count": len(pain_points),
        "scripts_count": len(scripts),
        "voiceovers_count": len(voiceovers),
        "storyboards_count": len(storyboards),
        "carousels_count": len(carousels),
        "calendar": calendar,
        "all_files": all_files,
    }

    summary_path = save_summary(summary)
    all_files.append(str(summary_path))

    print_summary(summary)
    print(f"\n📋 Summary saved: {summary_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())