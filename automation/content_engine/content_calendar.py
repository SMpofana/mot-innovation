#!/usr/bin/env python
"""
content_calendar.py — M.O.T Innovation Content Calendar Generator

Generates a 30-day content calendar with a weekly rotation:
    Mon — LinkedIn pain point post
    Tue — YouTube Short
    Wed — LinkedIn carousel
    Thu — YouTube Short
    Fri — LinkedIn educational post
    Sat — YouTube long-form
    Sun — Rest

Output is a Google Sheets-compatible CSV with columns:
    date, day, platform, content_type, pain_point, service, script_file_path, status

The calendar auto-fills from the existing pain points and case studies.

Usage:
    # Generate a 30-day calendar starting from today
    python content_calendar.py

    # Start from a specific date
    python content_calendar.py --start 2026-01-06

    # Generate and auto-generate scripts for each entry
    python content_calendar.py --generate-scripts

    # Specify output path
    python content_calendar.py --output content_calendar.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from data import (  # noqa: E402
    BRAND_NAME, WEBSITE_URL,
    PAIN_POINTS, SERVICES, CASE_STUDIES,
    get_pain_point, get_service,
)

CALENDAR_DIR = SCRIPT_DIR / "calendar"
CALENDAR_DIR.mkdir(parents=True, exist_ok=True)
SCRIPTS_DIR = SCRIPT_DIR / "scripts"

# Weekly rotation schedule (index = weekday, 0=Monday)
# Sunday is rest day
WEEKLY_SCHEDULE = {
    0: {"day": "Mon", "platform": "LinkedIn", "content_type": "Pain Point Post", "script_type": "linkedin"},
    1: {"day": "Tue", "platform": "YouTube", "content_type": "Short (60s)", "script_type": "short"},
    2: {"day": "Wed", "platform": "LinkedIn", "content_type": "Case Study Carousel", "script_type": "carousel"},
    3: {"day": "Thu", "platform": "YouTube", "content_type": "Short (60s)", "script_type": "short"},
    4: {"day": "Fri", "platform": "LinkedIn", "content_type": "Educational Post", "script_type": "linkedin"},
    5: {"day": "Sat", "platform": "YouTube", "content_type": "Long-form (5min)", "script_type": "short"},
    6: {"day": "Sun", "platform": "Rest", "content_type": "—", "script_type": None},
}

# Educational post topics (rotated weekly)
EDUCATIONAL_TOPICS = [
    {"pain_point_id": "disconnected_tools", "service_id": "dam", "topic": "3 free tools to organize your marketing assets this week"},
    {"pain_point_id": "manual_reporting", "service_id": "tracking", "topic": "How to set up a marketing dashboard in 10 minutes with free tools"},
    {"pain_point_id": "manual_posting", "service_id": "delivery", "topic": "Stop manually posting to 5 platforms — here's the free alternative"},
    {"pain_point_id": "wasting_ad_spend", "service_id": "optimization", "topic": "The A/B testing framework that 2x'd ROAS for a SaaS startup"},
    {"pain_point_id": "scattered_assets", "service_id": "dam", "topic": "Why your team can't find files (and the free fix for it)"},
    {"pain_point_id": "want_builder_not_advisor", "service_id": "dam", "topic": "Why 'marketing consultants' are dead — and what replaced them"},
]


def generate_calendar(start_date: datetime, days: int = 30) -> list[dict]:
    """
    Generate a 30-day content calendar.

    Rotates through pain points and services, matching them to the weekly schedule.
    Each entry has: date, day, platform, content type, pain point, service, script file path, status.
    """
    entries = []
    pp_index = 0  # Rotate through pain points
    cs_index = 0  # Rotate through case studies
    edu_index = 0  # Rotate through educational topics

    for i in range(days):
        date = start_date + timedelta(days=i)
        weekday = date.weekday()  # 0=Monday
        schedule = WEEKLY_SCHEDULE[weekday]

        # Skip Sunday (rest day)
        if schedule["platform"] == "Rest":
            entries.append({
                "date": date.strftime("%Y-%m-%d"),
                "day": schedule["day"],
                "platform": "Rest",
                "content_type": "—",
                "pain_point": "—",
                "service": "—",
                "script_file_path": "",
                "status": "rest",
            })
            continue

        pp = PAIN_POINTS[pp_index % len(PAIN_POINTS)]

        # Match service to pain point
        matched = [s for s in SERVICES.values() if pp["id"] in s["keywords"]]
        svc = matched[0] if matched else SERVICES["dam"]

        # Special handling per day
        script_type = schedule["script_type"]
        script_file = ""

        if weekday == 2:  # Wednesday — carousel
            # Use case study for carousel
            cs = CASE_STUDIES[cs_index % len(CASE_STUDIES)]
            cs_index += 1
            # Check if a script already exists
            safe_title = pp["id"]
            existing = list(SCRIPTS_DIR.glob(f"carousel_{safe_title}_*.json")) if SCRIPTS_DIR.exists() else []
            script_file = str(existing[0]) if existing else ""

        elif weekday == 4:  # Friday — educational
            edu = EDUCATIONAL_TOPICS[edu_index % len(EDUCATIONAL_TOPICS)]
            pp = get_pain_point(edu["pain_point_id"])
            svc = get_service(edu["service_id"])
            edu_index += 1

        elif weekday == 5:  # Saturday — long-form
            # Long-form uses the same pain point but a deeper script
            pass

        # Check if a script already exists for this pain point + service
        if not script_file and SCRIPTS_DIR.exists():
            if script_type == "short":
                existing = list(SCRIPTS_DIR.glob(f"yt_short_*{pp['id']}*.md")) or list(SCRIPTS_DIR.glob(f"yt_short_*{pp['title'][:20].lower().replace(' ', '_')}*.md"))
                script_file = str(existing[0]) if existing else ""
            elif script_type == "linkedin":
                existing = list(SCRIPTS_DIR.glob(f"linkedin_post_*{pp['id']}*.md")) or list(SCRIPTS_DIR.glob(f"linkedin_post_*{pp['title'][:20].lower().replace(' ', '_')}*.md"))
                script_file = str(existing[0]) if existing else ""

        entries.append({
            "date": date.strftime("%Y-%m-%d"),
            "day": schedule["day"],
            "platform": schedule["platform"],
            "content_type": schedule["content_type"],
            "pain_point": pp["title"],
            "service": svc["name"],
            "script_file_path": script_file,
            "status": "published" if script_file else "draft",
        })

        # Advance pain point index (except for educational which has its own rotation)
        if weekday != 4:
            pp_index += 1

    return entries


def save_csv(entries: list[dict], output_path: Path) -> None:
    """Save calendar entries as a Google Sheets-compatible CSV."""
    fieldnames = ["date", "day", "platform", "content_type", "pain_point", "service", "script_file_path", "status"]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)


def save_json(entries: list[dict], output_path: Path) -> None:
    """Save calendar entries as JSON."""
    data = {
        "generated_at": datetime.now().isoformat(),
        "total_entries": len(entries),
        "start_date": entries[0]["date"] if entries else "",
        "end_date": entries[-1]["date"] if entries else "",
        "schedule_rotation": {str(k): v for k, v in WEEKLY_SCHEDULE.items()},
        "entries": entries,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def print_calendar(entries: list[dict]) -> None:
    """Print a formatted calendar to the console."""
    print(f"\n{'=' * 100}")
    print(f"CONTENT CALENDAR — {BRAND_NAME}")
    print(f"{'=' * 100}")
    print(f"{'Date':12s} {'Day':5s} {'Platform':10s} {'Content Type':20s} {'Pain Point':35s} {'Service':25s} {'Status':10s}")
    print(f"{'-' * 100}")

    for entry in entries:
        print(
            f"{entry['date']:12s} "
            f"{entry['day']:5s} "
            f"{entry['platform']:10s} "
            f"{entry['content_type']:20s} "
            f"{entry['pain_point'][:35]:35s} "
            f"{entry['service'][:25]:25s} "
            f"{entry['status']:10s}"
        )

    # Summary
    total = len(entries)
    draft = sum(1 for e in entries if e["status"] == "draft")
    published = sum(1 for e in entries if e["status"] == "published")
    rest = sum(1 for e in entries if e["status"] == "rest")
    print(f"\n📊 Summary: {total} entries ({published} published, {draft} draft, {rest} rest)")


# ── CLI ──────────────────────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(
        description="M.O.T Innovation — Content Calendar Generator"
    )
    parser.add_argument("--start", type=str, default=None,
                        help="Start date (YYYY-MM-DD). Default: next Monday from today.")
    parser.add_argument("--days", type=int, default=30,
                        help="Number of days to generate (default: 30)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output CSV file path (default: calendar/content_calendar.csv)")
    parser.add_argument("--generate-scripts", action="store_true",
                        help="Also generate scripts for each calendar entry")
    parser.add_argument("--print", action="store_true", default=True,
                        help="Print the calendar to console (default: True)")
    args = parser.parse_args()

    print(f"\n{'=' * 60}")
    print(f"CONTENT CALENDAR GENERATOR — {BRAND_NAME}")
    print(f"{'=' * 60}")

    # Determine start date
    if args.start:
        start_date = datetime.strptime(args.start, "%Y-%m-%d")
    else:
        # Default: next Monday from today
        today = datetime.now()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7  # Next Monday, not today if today is Monday
        start_date = today + timedelta(days=days_until_monday)

    print(f"📅 Start date: {start_date.strftime('%Y-%m-%d')} ({start_date.strftime('%A')})")
    print(f"📅 Duration: {args.days} days")

    # Generate calendar
    entries = generate_calendar(start_date, args.days)

    # Save CSV
    csv_path = Path(args.output) if args.output else CALENDAR_DIR / "content_calendar.csv"
    save_csv(entries, csv_path)
    print(f"\n✅ CSV saved: {csv_path}")

    # Save JSON
    json_path = csv_path.with_suffix(".json")
    save_json(entries, json_path)
    print(f"✅ JSON saved: {json_path}")

    # Optionally generate scripts
    if args.generate_scripts:
        print("\n📝 Generating scripts for calendar entries...")
        from script_generator import generate_youtube_short, generate_linkedin_post
        from linkedin_carousel import generate_carousel, save_carousel

        generated = 0
        for entry in entries:
            if entry["status"] == "rest" or entry["script_file_path"]:
                continue

            # Find pain point
            pp = None
            for p in PAIN_POINTS:
                if p["title"] == entry["pain_point"]:
                    pp = p
                    break
            if not pp:
                continue

            # Find service
            svc = None
            for s in SERVICES.values():
                if s["name"] == entry["service"]:
                    svc = s
                    break
            if not svc:
                continue

            if "Short" in entry["content_type"]:
                result = generate_youtube_short(pp, svc)
                entry["script_file_path"] = result["file_path"]
                entry["status"] = "published"
                generated += 1
            elif "Pain Point" in entry["content_type"] or "Educational" in entry["content_type"]:
                result = generate_linkedin_post(pp, svc)
                entry["script_file_path"] = result["file_path"]
                entry["status"] = "published"
                generated += 1
            elif "Carousel" in entry["content_type"]:
                carousel = generate_carousel(pp, svc)
                files = save_carousel(carousel)
                entry["script_file_path"] = str(files[0]) if files else ""
                entry["status"] = "published" if entry["script_file_path"] else "draft"
                generated += 1

        # Re-save CSV with updated paths
        save_csv(entries, csv_path)
        save_json(entries, json_path)
        print(f"   ✅ Generated {generated} scripts")

    # Print calendar
    if args.print:
        print_calendar(entries)

    print(f"\n✅ Content calendar complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())