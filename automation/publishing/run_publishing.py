#!/usr/bin/env python
"""
run_publishing.py — M.O.T Innovation Master Publishing Pipeline

Orchestrates the full publishing workflow:
    1. Reads new content from content_engine/scripts/ directory
    2. Creates documents in Sanity CMS
    3. For YouTube: pairs script + voiceover MP3, uploads to YouTube
    4. For LinkedIn: creates webhook payload for Make.com
    5. Updates content_calendar.csv to mark entries as 'published'
    6. Logs what was published

This script bridges the content generation pipeline (content_engine) with
the publishing layer (YouTube + LinkedIn + Sanity CMS).

Usage:
    # Full publishing run (process all new content)
    python run_publishing.py

    # Process only YouTube content
    python run_publishing.py --youtube-only

    # Process only LinkedIn content
    python run_publishing.py --linkedin-only

    # Process only Sanity CMS sync (no uploads)
    python run_publishing.py --sanity-only

    # Dry run — show what would be published without uploading
    python run_publishing.py --dry-run

    # Specify a Make.com webhook URL for LinkedIn
    python run_publishing.py --webhook-url https://hook.us1.make.com/xxx

    # Limit to N items per platform
    python run_publishing.py --limit 3

    # Process specific script file only
    python run_publishing.py --file scripts/yt_short_disconnected_tools_20260804.md
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# ── Paths ──────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent          # automation/publishing/
PROJECT_ROOT = SCRIPT_DIR.parent.parent                 # mot_innovation/
CONTENT_ENGINE_DIR = SCRIPT_DIR.parent / "content_engine"  # automation/content_engine/

SCRIPTS_DIR = CONTENT_ENGINE_DIR / "scripts"
AUDIO_DIR = CONTENT_ENGINE_DIR / "audio"
CAROUSELS_DIR = CONTENT_ENGINE_DIR / "carousels"
CALENDAR_DIR = CONTENT_ENGINE_DIR / "calendar"
SUMMARY_DIR = CONTENT_ENGINE_DIR / "summaries"

PUBLISHING_LOG = SCRIPT_DIR / "publishing_log.json"

# Load .env.local from the project root
ENV_PATH = PROJECT_ROOT / ".env.local"
load_dotenv(ENV_PATH)

# ── Import publishing modules ──────────────────────────────────────────────────

# Add content_engine to path so we can import sanity_cms
sys.path.insert(0, str(CONTENT_ENGINE_DIR))

try:
    from sanity_cms import (
        create_script_doc, create_post_doc, create_carousel_doc,
        create_calendar_doc, query_content,
        create_script_from_file, create_post_from_file, create_carousel_from_file,
        _parse_youtube_script, _parse_linkedin_post,
    )
    SANITY_AVAILABLE = True
except Exception as e:
    SANITY_AVAILABLE = False
    print(f"⚠️  Sanity CMS module not available: {e}")

try:
    from youtube_upload import upload_video, set_thumbnail, DAILY_QUOTA_LIMIT, UPLOAD_COST_UNITS
    YOUTUBE_AVAILABLE = True
except Exception as e:
    YOUTUBE_AVAILABLE = False
    print(f"⚠️  YouTube upload module not available: {e}")

try:
    from linkedin_post import create_webhook_payload, send_to_webhook, parse_linkedin_post_file
    LINKEDIN_AVAILABLE = True
except Exception as e:
    LINKEDIN_AVAILABLE = False
    print(f"⚠️  LinkedIn posting module not available: {e}")


# ── Logging ────────────────────────────────────────────────────────────────────

def load_publishing_log() -> list[dict[str, Any]]:
    """Load the publishing log of past published items."""
    if PUBLISHING_LOG.exists():
        try:
            return json.loads(PUBLISHING_LOG.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_publishing_log(log: list[dict[str, Any]]) -> None:
    """Save the publishing log."""
    PUBLISHING_LOG.write_text(
        json.dumps(log, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def add_to_log(entry: dict[str, Any]) -> None:
    """Add an entry to the publishing log."""
    log = load_publishing_log()
    log.append(entry)
    save_publishing_log(log)


# ── Content discovery ──────────────────────────────────────────────────────────

def find_new_scripts() -> list[Path]:
    """Find all script files in the scripts directory."""
    if not SCRIPTS_DIR.exists():
        return []
    return sorted(SCRIPTS_DIR.glob("*.md"))


def find_new_carousels() -> list[Path]:
    """Find all carousel JSON files in the carousels directory."""
    if not CAROUSELS_DIR.exists():
        return []
    return sorted(CAROUSELS_DIR.glob("*.json"))


def find_audio_for_script(script_path: Path) -> Path | None:
    """
    Find the voiceover MP3 that matches a YouTube script file.

    Script: yt_short_disconnected_marketing_tools_20260804_220511.md
    Audio:  yt_short_disconnected_marketing_tools_20260804_220511.mp3
    """
    stem = script_path.stem  # e.g. yt_short_disconnected_marketing_tools_20260804_220511
    if not AUDIO_DIR.exists():
        return None
    audio_file = AUDIO_DIR / f"{stem}.mp3"
    return audio_file if audio_file.exists() else None


def find_video_for_script(script_path: Path) -> Path | None:
    """
    Find a video file that matches a script.

    For now, this checks for .mp4 files matching the script stem.
    If no actual video exists, we fall back to the audio MP3
    (for testing — YouTube requires actual video).
    """
    stem = script_path.stem
    for ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
        video_file = AUDIO_DIR / f"{stem}{ext}"
        if video_file.exists():
            return video_file
    return None


def get_published_filenames() -> set[str]:
    """Get the set of filenames already ACTUALLY published to a platform.

    Only entries with an upload/webhook action (youtube_upload, linkedin_webhook)
    count as "published". Sanity-sync entries must NOT be treated as published —
    a doc synced to Sanity still needs to be uploaded to YouTube/LinkedIn.
    """
    log = load_publishing_log()
    return {
        entry.get("file_name", "")
        for entry in log
        if entry.get("action") in ("youtube_upload", "linkedin_webhook")
    }


# ── Calendar update ────────────────────────────────────────────────────────────

def update_calendar_csv(published_entries: list[dict[str, Any]]) -> None:
    """
    Update the content_calendar.csv to mark entries as 'published'.

    published_entries: list of dicts with at least 'date' and 'platform' keys.
    """
    csv_path = CALENDAR_DIR / "content_calendar.csv"
    if not csv_path.exists():
        print("   ⚠️  content_calendar.csv not found — skipping calendar update")
        return

    # Read the CSV
    rows = []
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or [
            "date", "day", "platform", "content_type",
            "pain_point", "service", "script_file_path", "status",
        ]
        rows = list(reader)

    # Build a set of (date, platform) pairs to mark as published
    published_pairs = {
        (entry.get("date", ""), entry.get("platform", ""))
        for entry in published_entries
        if entry.get("date")
    }

    # Update matching rows
    updated_count = 0
    for row in rows:
        date = row.get("date", "")
        platform = row.get("platform", "")
        if (date, platform) in published_pairs and row.get("status") != "rest":
            row["status"] = "published"
            updated_count += 1

    # Write the updated CSV
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"   ✅ Calendar updated — {updated_count} entries marked as 'published'")


def update_calendar_json(published_entries: list[dict[str, Any]]) -> None:
    """Update content_calendar.json to mark entries as 'published'."""
    json_path = CALENDAR_DIR / "content_calendar.json"
    if not json_path.exists():
        return

    data = json.loads(json_path.read_text(encoding="utf-8"))
    entries = data.get("entries", [])

    published_pairs = {
        (entry.get("date", ""), entry.get("platform", ""))
        for entry in published_entries
        if entry.get("date")
    }

    for entry in entries:
        date = entry.get("date", "")
        platform = entry.get("platform", "")
        if (date, platform) in published_pairs and entry.get("status") != "rest":
            entry["status"] = "published"

    json_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# ── Publishing steps ──────────────────────────────────────────────────────────

def publish_to_sanity(
    script_path: Path,
    content_type: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Create a Sanity CMS document for a content piece.

    Args:
        script_path: Path to the script/markdown file
        content_type: 'youtube_short', 'linkedin_post', or 'carousel'

    Returns dict with success status and Sanity response.
    """
    if not SANITY_AVAILABLE:
        return {"error": "Sanity CMS module not available"}

    try:
        if content_type == "youtube_short":
            if dry_run:
                parsed = _parse_youtube_script(
                    script_path.read_text(encoding="utf-8"), str(script_path)
                )
                return {"status": "dry_run", "document": parsed, "doc_id": "dry_run"}
            response = create_script_from_file(script_path)
        elif content_type == "linkedin_post":
            if dry_run:
                parsed = _parse_linkedin_post(
                    script_path.read_text(encoding="utf-8"), str(script_path)
                )
                return {"status": "dry_run", "document": parsed, "doc_id": "dry_run"}
            response = create_post_from_file(script_path)
        elif content_type == "carousel":
            if dry_run:
                json_content = json.loads(script_path.read_text(encoding="utf-8"))
                return {
                    "status": "dry_run",
                    "document": {"title": json_content.get("metadata", {}).get("title", "")},
                    "doc_id": "dry_run",
                }
            response = create_carousel_from_file(script_path)
        else:
            return {"error": f"Unknown content type: {content_type}"}

        return {"status": "created", "response": response}

    except Exception as e:
        return {"error": str(e)}


def publish_to_youtube(
    script_path: Path,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Upload a YouTube Short: pairs script + voiceover/video MP3/MP4.

    Reads metadata (title, description, tags) from the script markdown file,
    finds the matching audio/video file, and uploads to YouTube.

    Returns dict with upload status and video_id.
    """
    if not YOUTUBE_AVAILABLE:
        return {"error": "YouTube upload module not available"}

    md_content = script_path.read_text(encoding="utf-8")

    # Extract metadata from the script file
    title_match = re.search(r"\*\*Title:\*\*\s*(.+)", md_content)
    title = title_match.group(1).strip() if title_match else script_path.stem

    desc_match = re.search(r"\*\*Description:\*\*\s*(.+)", md_content)
    description = desc_match.group(1).strip() if desc_match else ""

    tags_match = re.search(r"\*\*Tags:\*\*\s*(.+)", md_content)
    tags_str = tags_match.group(1).strip() if tags_match else ""
    tags = [t.strip() for t in tags_str.split(",") if t.strip()]

    # Find the video or audio file
    video_file = find_video_for_script(script_path)
    audio_file = find_audio_for_script(script_path)

    if not video_file and not audio_file:
        return {
            "error": f"No video or audio file found for {script_path.name}. "
                     f"Looked in {AUDIO_DIR}",
        }

    # Assemble a cartoon animated video (flat-vector scenes + Ken Burns +
    # crossfades + progress bar) from the script + audio. Prefer the cartoon
    # generator; fall back to the text-animated generator, then static, then
    # audio-only.
    if audio_file and not dry_run:
        try:
            sys.path.insert(0, str(SCRIPT_DIR.parent / "content_engine"))
            from cartoon_video import assemble_cartoon
            assembled = assemble_cartoon(script_path, audio_file)
            if assembled:
                upload_file = assembled
                is_short = True
            else:
                upload_file = audio_file
        except Exception as e:
            print(f"      ⚠️  Cartoon assembly failed ({e}), falling back to animated")
            try:
                from animated_video import assemble_animated
                assembled = assemble_animated(script_path, audio_file)
                upload_file = assembled or audio_file
            except Exception as e2:
                print(f"      ⚠️  Animated assembly failed ({e2}), falling back to static")
                try:
                    from video_assembler import assemble_from_files
                    assembled = assemble_from_files(script_path, audio_file)
                    upload_file = assembled or audio_file
                except Exception as e3:
                    print(f"      ⚠️  Static assembly failed ({e3}), uploading audio only")
                    upload_file = audio_file
    else:
        upload_file = video_file or audio_file
    is_short = "yt_short" in script_path.name

    if dry_run:
        return {
            "status": "dry_run",
            "title": title,
            "upload_file": str(upload_file),
            "is_short": is_short,
            "tags": tags,
        }

    # Upload to YouTube
    result = upload_video(
        video_path=upload_file,
        title=title,
        description=description,
        tags=tags,
        category_id=22,
        privacy_status="public",
        is_short=is_short,
    )

    return result


def _find_carousel_cover(script_path: Path) -> str:
    """Find and free-host a carousel cover image matching a LinkedIn post.

    Matches the post's pain point to a carousel's metadata.pain_point, renders
    its first slide if needed, uploads to catbox.moe, and returns the public
    URL. Returns "" if no match or upload fails (post still sends text-only).
    """
    try:
        import re as _re
        md = script_path.read_text(encoding="utf-8")
        pp_match = _re.search(r"\*\*Pain Point:\*\*\s*(.+)", md)
        if not pp_match:
            return ""
        pain_point = pp_match.group(1).strip()

        carousel_dir = CONTENT_ENGINE_DIR / "carousels"
        for cj in sorted(carousel_dir.glob("carousel_*.json")):
            try:
                meta = json.loads(cj.read_text(encoding="utf-8")).get("metadata", {})
            except Exception:
                continue
            if meta.get("pain_point", "").strip() == pain_point:
                sys.path.insert(0, str(CONTENT_ENGINE_DIR))
                from image_host import upload_carousel_cover
                return upload_carousel_cover(cj)
    except Exception as e:
        print(f"      ⚠️  Carousel cover attach failed ({e}), posting text-only")
    return ""


def publish_to_linkedin(
    script_path: Path,
    webhook_url: str = "",
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Send a LinkedIn post via Make.com webhook.

    Reads the post content from the markdown file, creates a webhook payload,
    and sends it to the Make.com webhook URL.

    Returns dict with send status.
    """
    if not LINKEDIN_AVAILABLE:
        return {"error": "LinkedIn posting module not available"}

    # Parse the LinkedIn post file
    parsed = parse_linkedin_post_file(script_path)
    text = parsed["text"]
    link = parsed["link"]

    # Attach a matching carousel cover image (free-hosted) so the post has
    # both text AND an image. Match by pain point.
    image_url = _find_carousel_cover(script_path)

    # Create the webhook payload
    payload = create_webhook_payload(text, image_url=image_url, link=link)

    if dry_run:
        return {
            "status": "dry_run",
            "payload": payload,
            "webhook_url": webhook_url or "(not set)",
        }

    if not webhook_url:
        return {
            "error": "No webhook URL provided. Use --webhook-url or set "
                     "LINKEDIN_MAKE_WEBHOOK_URL in .env.local",
            "payload": payload,
        }

    # Send to Make.com webhook
    result = send_to_webhook(webhook_url, payload)
    return result


# ── Main pipeline ──────────────────────────────────────────────────────────────

def run_pipeline(
    youtube_only: bool = False,
    linkedin_only: bool = False,
    sanity_only: bool = False,
    dry_run: bool = False,
    webhook_url: str = "",
    limit: int = 0,
    single_file: str = "",
) -> int:
    """Run the master publishing pipeline."""
    import os
    webhook_url = webhook_url or os.getenv("LINKEDIN_MAKE_WEBHOOK_URL", "")

    print(f"\n{'=' * 60}")
    print(f"M.O.T INNOVATION — MASTER PUBLISHING PIPELINE")
    print(f"{'=' * 60}")
    print(f"Run time:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Dry run:    {dry_run}")
    print(f"YouTube:    {'✅' if YOUTUBE_AVAILABLE else '❌'}")
    print(f"LinkedIn:   {'✅' if LINKEDIN_AVAILABLE else '❌'}")
    print(f"Sanity CMS: {'✅' if SANITY_AVAILABLE else '❌'}")
    print(f"Webhook:    {'✅' if webhook_url else '⚠️  Not set'}")
    print()

    published_log: list[dict[str, Any]] = []
    already_published = get_published_filenames()

    # ── Single file mode ──
    if single_file:
        file_path = Path(single_file)
        if not file_path.is_absolute():
            # Try relative to current working directory first, then scripts dir
            if file_path.exists():
                file_path = file_path.resolve()
            elif (SCRIPTS_DIR / file_path).exists():
                file_path = SCRIPTS_DIR / file_path
            elif (CONTENT_ENGINE_DIR / file_path).exists():
                file_path = CONTENT_ENGINE_DIR / file_path
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return 1

        is_yt = "yt_short" in file_path.name
        is_li = "linkedin_post" in file_path.name

        if is_yt:
            print(f"── Processing single YouTube script: {file_path.name} ──")
            if not sanity_only:
                print("\n📤 YouTube Upload:")
                yt_result = publish_to_youtube(file_path, dry_run)
                print(f"   {json.dumps(yt_result, indent=2, ensure_ascii=False)}")
                if yt_result.get("status") != "dry_run":
                    published_log.append({
                        "file_name": file_path.name,
                        "platform": "YouTube",
                        "type": "youtube_short",
                        "result": yt_result,
                        "timestamp": datetime.now().isoformat(),
                    })

            print("\n📝 Sanity CMS:")
            san_result = publish_to_sanity(file_path, "youtube_short", dry_run)
            print(f"   {json.dumps(san_result, indent=2, ensure_ascii=False)}")

        elif is_li:
            print(f"── Processing single LinkedIn post: {file_path.name} ──")
            if not sanity_only:
                print("\n📤 LinkedIn Post:")
                li_result = publish_to_linkedin(file_path, webhook_url, dry_run)
                print(f"   {json.dumps(li_result, indent=2, ensure_ascii=False)}")
                if li_result.get("status") != "dry_run":
                    published_log.append({
                        "file_name": file_path.name,
                        "platform": "LinkedIn",
                        "type": "linkedin_post",
                        "result": li_result,
                        "timestamp": datetime.now().isoformat(),
                    })

            print("\n📝 Sanity CMS:")
            san_result = publish_to_sanity(file_path, "linkedin_post", dry_run)
            print(f"   {json.dumps(san_result, indent=2, ensure_ascii=False)}")

        if published_log:
            for entry in published_log:
                add_to_log(entry)
        update_calendar_csv(published_log)
        update_calendar_json(published_log)
        print(f"\n✅ Done!")
        return 0

    # ── Full pipeline mode ──
    all_scripts = find_new_scripts()
    yt_scripts = [f for f in all_scripts if f.name.startswith("yt_short_")]
    li_scripts = [f for f in all_scripts if f.name.startswith("linkedin_post_")]
    carousels = find_new_carousels()

    # Filter out already published
    yt_scripts = [f for f in yt_scripts if f.name not in already_published]
    li_scripts = [f for f in li_scripts if f.name not in already_published]

    # Apply limit
    if limit > 0:
        yt_scripts = yt_scripts[:limit]
        li_scripts = li_scripts[:limit]
        carousels = carousels[:limit]

    print(f"── Content Discovery ──")
    print(f"   YouTube scripts:    {len(yt_scripts)}")
    print(f"   LinkedIn posts:     {len(li_scripts)}")
    print(f"   Carousels:          {len(carousels)}")
    print(f"   Already published:  {len(already_published)}")
    print()

    # ── Step 1: Sanity CMS sync ──
    if not youtube_only and not linkedin_only or sanity_only:
        print("── Step 1: Syncing to Sanity CMS ──")

        for script in yt_scripts:
            print(f"   📝 YouTube: {script.name}")
            result = publish_to_sanity(script, "youtube_short", dry_run)
            if "error" in result:
                print(f"      ❌ {result['error']}")
            else:
                print(f"      ✅ {'Dry run' if dry_run else 'Created in Sanity'}")
                published_log.append({
                    "file_name": script.name,
                    "platform": "YouTube",
                    "type": "youtube_short",
                    "action": "sanity_sync",
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                })

        for script in li_scripts:
            print(f"   📝 LinkedIn: {script.name}")
            result = publish_to_sanity(script, "linkedin_post", dry_run)
            if "error" in result:
                print(f"      ❌ {result['error']}")
            else:
                print(f"      ✅ {'Dry run' if dry_run else 'Created in Sanity'}")
                published_log.append({
                    "file_name": script.name,
                    "platform": "LinkedIn",
                    "type": "linkedin_post",
                    "action": "sanity_sync",
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                })

        for carousel in carousels:
            print(f"   📝 Carousel: {carousel.name}")
            result = publish_to_sanity(carousel, "carousel", dry_run)
            if "error" in result:
                print(f"      ❌ {result['error']}")
            else:
                print(f"      ✅ {'Dry run' if dry_run else 'Created in Sanity'}")
                published_log.append({
                    "file_name": carousel.name,
                    "platform": "LinkedIn",
                    "type": "carousel",
                    "action": "sanity_sync",
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                })

        print()

    # ── Step 2: YouTube uploads ──
    if not linkedin_only and not sanity_only:
        print("── Step 2: Uploading to YouTube ──")

        quota_used = 0
        for script in yt_scripts:
            if quota_used + UPLOAD_COST_UNITS > DAILY_QUOTA_LIMIT:
                print("   ⚠️  YouTube daily quota would be exceeded — skipping remaining uploads")
                break

            print(f"   📤 YouTube: {script.name}")
            result = publish_to_youtube(script, dry_run)

            if "error" in result:
                print(f"      ❌ {result['error']}")
            elif result.get("status") == "dry_run":
                print(f"      🔄 Dry run — would upload: {result.get('upload_file')}")
                print(f"         Title: {result.get('title')}")
            elif result.get("quota_exceeded"):
                print(f"      ❌ QUOTA EXCEEDED — stopping YouTube uploads")
                quota_used = DAILY_QUOTA_LIMIT
                break
            else:
                print(f"      ✅ Uploaded! Video ID: {result.get('video_id', '')}")
                quota_used += UPLOAD_COST_UNITS
                published_log.append({
                    "file_name": script.name,
                    "platform": "YouTube",
                    "type": "youtube_short",
                    "action": "youtube_upload",
                    "video_id": result.get("video_id", ""),
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                })

        print()

    # ── Step 3: LinkedIn posts ──
    if not youtube_only and not sanity_only:
        print("── Step 3: Posting to LinkedIn (via Make.com webhook) ──")

        for script in li_scripts:
            print(f"   📤 LinkedIn: {script.name}")
            result = publish_to_linkedin(script, webhook_url, dry_run)

            if "error" in result:
                print(f"      ❌ {result['error']}")
                if "payload" in result:
                    print(f"      💡 Payload created but not sent (no webhook URL)")
            elif result.get("status") == "dry_run":
                print(f"      🔄 Dry run — payload created")
            elif result.get("status") == "sent":
                print(f"      ✅ Sent to Make.com webhook!")
                published_log.append({
                    "file_name": script.name,
                    "platform": "LinkedIn",
                    "type": "linkedin_post",
                    "action": "linkedin_webhook",
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                })
            else:
                print(f"      ⚠️  Unexpected: {result.get('status', 'unknown')}")

        print()

    # ── Step 4: Update calendar ──
    if not dry_run:
        print("── Step 4: Updating content calendar ──")
        update_calendar_csv(published_log)
        update_calendar_json(published_log)
        print()

    # ── Step 5: Log ──
    print("── Step 5: Logging ──")

    # Only persist entries that were ACTUALLY published (not dry runs).
    # A dry run should never write to the publishing log, otherwise the
    # filenames get marked "already published" and real runs skip them.
    real_entries = [
        e for e in published_log
        if e.get("result", {}).get("status") not in ("dry_run",)
    ]

    # Add new entries to the log
    if real_entries:
        for entry in real_entries:
            add_to_log(entry)
        print(f"   ✅ {len(real_entries)} entries logged to {PUBLISHING_LOG}")
    else:
        print("   ℹ️  Nothing new to log")

    # Print summary
    print(f"\n{'=' * 60}")
    print("PUBLISHING PIPELINE SUMMARY")
    print(f"{'=' * 60}")
    print(f"YouTube scripts processed:  {len(yt_scripts)}")
    print(f"LinkedIn posts processed:   {len(li_scripts)}")
    print(f"Carousels processed:        {len(carousels)}")
    print(f"Published (logged):         {len(real_entries)}")
    print(f"Log file:                   {PUBLISHING_LOG}")
    print(f"\n✅ Publishing pipeline complete!")
    print(f"{'=' * 60}")

    return 0


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="M.O.T Innovation — Master Publishing Pipeline"
    )
    parser.add_argument(
        "--youtube-only", action="store_true",
        help="Only process YouTube content (skip LinkedIn and Sanity sync)",
    )
    parser.add_argument(
        "--linkedin-only", action="store_true",
        help="Only process LinkedIn content (skip YouTube and Sanity sync)",
    )
    parser.add_argument(
        "--sanity-only", action="store_true",
        help="Only sync to Sanity CMS (skip YouTube and LinkedIn uploads)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be published without actually uploading",
    )
    parser.add_argument(
        "--webhook-url", type=str, default="",
        help="Make.com webhook URL for LinkedIn posting",
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Maximum number of items to process per platform (0 = no limit)",
    )
    parser.add_argument(
        "--file", type=str, default="",
        help="Process a single script file only",
    )
    args = parser.parse_args()

    return run_pipeline(
        youtube_only=args.youtube_only,
        linkedin_only=args.linkedin_only,
        sanity_only=args.sanity_only,
        dry_run=args.dry_run,
        webhook_url=args.webhook_url,
        limit=args.limit,
        single_file=args.file,
    )


if __name__ == "__main__":
    sys.exit(main())