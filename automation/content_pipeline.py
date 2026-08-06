#!/usr/bin/env python
"""
Social Media Content Pipeline — M.O.T Innovation

Connects to the existing agent-team Reddit RSS pipeline to:
1. Pull pain points from Reddit (via the painpoint_scanner infrastructure)
2. Generate social media posts about M.O.T Innovation services
3. Schedule them (output to a content calendar file)

This script can work standalone (using Reddit's public RSS feeds directly)
or integrate with the existing agent-team pipeline at C:\\Users\\mpofa\\agent-team\\

Usage:
    python content_pipeline.py                          # Full pipeline run
    python content_pipeline.py --scan-only              # Only scan Reddit for pain points
    python content_pipeline.py --generate-only          # Only generate posts from existing pain points
    python content_pipeline.py --schedule-only           # Only generate calendar from existing posts
    python content_pipeline.py --verbose                # Show full post content
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus
from urllib.request import urlopen, Request
from xml.etree import ElementTree

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
CONTENT_CALENDAR_DIR = BASE_DIR / "content_calendar"

# Existing agent-team paths (optional enrichment — only used if the files exist).
# Make overridable via env so the pipeline runs identically on any machine/CI.
# Default: look for a sibling "agent-team" dir relative to this repo, then fall
# back to the repo-relative store used when this script runs inside agent-team.
import os as _os
_AGENT_TEAM_DIR = _os.environ.get("AGENT_TEAM_DIR", "")
if not _AGENT_TEAM_DIR:
    _candidate = BASE_DIR.parents[1] / "store" / "painpoints.json"
    if _candidate.exists():
        _AGENT_TEAM_DIR = str(BASE_DIR.parents[1])
    else:
        _AGENT_TEAM_DIR = str(SCRIPT_DIR.parent.parent)
AGENT_TEAM_DIR = Path(_AGENT_TEAM_DIR)
EXISTING_PAINPOINTS_FILE = AGENT_TEAM_DIR / "store" / "painpoints.json"
EXISTING_MOT_PAINPOINTS = AGENT_TEAM_DIR / "store" / "mot_innovation" / "leads.json"

CONTENT_CALENDAR_DIR.mkdir(parents=True, exist_ok=True)

# Output files
PAINPOINTS_FILE = BASE_DIR / "content_calendar" / "painpoints.json"
POSTS_FILE = BASE_DIR / "content_calendar" / "social_posts.json"
CALENDAR_FILE = BASE_DIR / "content_calendar" / "content_calendar.md"
CALENDAR_JSON = BASE_DIR / "content_calendar" / "content_calendar.json"

# Reddit subreddits to scan for marketing pain points
SUBREDDITS = [
    "marketing", "digitalmarketing", "smallbusiness", "entrepreneur",
    "advertising", "socialmedia", "emarketing", "AskMarketing",
]

SCAN_QUERIES = [
    "frustrating OR struggling OR confusing",
    "hate OR terrible OR overwhelming",
    "don't know OR can't figure out OR impossible",
    "scattered OR messy OR disorganized",
    "too slow OR takes too long OR wasting time",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

# M.O.T Innovation service mappings
SERVICES = {
    "dam": {
        "name": "Digital Marketing Infrastructure",
        "keywords": ["files", "assets", "photos", "images", "messy", "scattered",
                     "disorganized", "storage", "google drive", "dropbox", "find",
                     "lost", "naming", "organized", "folder"],
        "hashtags": ["#DAM", "#DigitalAssets", "#MarketingInfrastructure"],
        "angle": "Stop hunting for files. A proper DAM system means finding any asset in seconds, not hours.",
    },
    "delivery": {
        "name": "Multi-Endpoint Delivery",
        "keywords": ["platforms", "channels", "posting", "social media", "scheduling",
                     "instagram", "linkedin", "tiktok", "facebook", "twitter",
                     "multiple", "everywhere", "cross", "publishing"],
        "hashtags": ["#SocialMediaManagement", "#ContentDistribution", "#MultiChannel"],
        "angle": "One content source, every channel served. Stop posting manually to each platform.",
    },
    "tracking": {
        "name": "Performance Tracking & Reporting",
        "keywords": ["don't know", "dashboard", "track", "tracking", "reporting",
                     "report", "analytics", "data", "metrics", "kpi", "roi",
                     "performance", "measure", "results", "numbers"],
        "hashtags": ["#MarketingAnalytics", "#Dashboards", "#KPI"],
        "angle": "If you can't measure it, you can't improve it. Unified dashboards that tell you what's actually working.",
    },
    "optimization": {
        "name": "Campaign Optimization",
        "keywords": ["ads", "ad spend", "budget", "roas", "campaign", "ppc",
                     "google ads", "meta ads", "facebook ads", "optimize",
                     "a/b test", "creative", "conversion", "cpa", "cpl"],
        "hashtags": ["#AdOptimization", "#PPC", "#ROAS"],
        "angle": "Stop wasting ad budget. Proper optimization and A/B testing can 2-3x your ROAS.",
    },
    "general": {
        "name": "Marketing Intelligence Infrastructure",
        "keywords": ["marketing", "strategy", "growth", "scale", "system",
                     "infrastructure", "automation", "tools"],
        "hashtags": ["#MarketingIntelligence", "#MOTInnovation", "#MarketingStrategy"],
        "angle": "Your marketing infrastructure should work FOR you, not against you.",
    },
}


# ── Reddit RSS scanning ─────────────────────────────────────────────────────
def fetch_reddit_rss(url: str, timeout: int = 15) -> str | None:
    """Fetch Reddit RSS feed (XML)."""
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return None
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def parse_reddit_rss(xml_text: str, subreddit: str) -> list[dict]:
    """Parse Reddit RSS XML and extract posts."""
    entries = []
    try:
        root = ElementTree.fromstring(xml_text)
        # RSS 2.0: /rss/channel/item
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for item in root.findall(".//item"):
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            date_el = item.find("pubDate")

            title = title_el.text if title_el is not None else ""
            link = link_el.text if link_el is not None else ""
            desc = desc_el.text if desc_el is not None else ""
            date = date_el.text if date_el is not None else ""

            entries.append({
                "source": "reddit",
                "subreddit": subreddit,
                "title": title,
                "url": link,
                "excerpt": desc[:200] if desc else "",
                "date": date,
            })
    except ElementTree.ParseError:
        pass
    return entries


def scan_reddit() -> list[dict]:
    """Scan Reddit for marketing pain points using RSS feeds."""
    print("── Scanning Reddit for pain points ──")
    all_posts = []

    for sub in SUBREDDITS:
        for query in SCAN_QUERIES:
            url = (
                f"https://www.reddit.com/r/{sub}/search.rss"
                f"?q={quote_plus(query)}"
                f"&restrict_sr=1&sort=new&limit=10&t=month"
            )
            print(f"  🔍 r/{sub}: {query[:40]}...")
            xml = fetch_reddit_rss(url)
            if xml:
                posts = parse_reddit_rss(xml, sub)
                all_posts.extend(posts)
            time.sleep(1.0)  # Rate limit

    # Deduplicate by URL
    seen = set()
    unique = []
    for p in all_posts:
        if p["url"] and p["url"] not in seen:
            seen.add(p["url"])
            unique.append(p)

    print(f"\n  📊 Found {len(all_posts)} posts ({len(unique)} unique)")
    return unique


def load_existing_painpoints() -> list[dict]:
    """Load pain points from the existing agent-team pipeline if available."""
    if EXISTING_PAINPOINTS_FILE.exists():
        with open(EXISTING_PAINPOINTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        themes = data.get("themes", [])
        print(f"  📁 Loaded {len(themes)} themes from existing agent-team pipeline")
        # Convert to our format
        return [
            {
                "source": "agent-team",
                "theme": t.get("theme", ""),
                "mentions": t.get("mentions", 0),
                "severity": t.get("severity", "med"),
                "sample_complaints": t.get("sample_complaints", []),
            }
            for t in themes
        ]
    return []


def _post_id(post: dict) -> str:
    """Get a unique identifier for a pain point entry (url, theme, or generated)."""
    return post.get("url", "") or post.get("theme", "") or post.get("title", "") or str(id(post))


def match_posts_to_services(posts: list[dict]) -> list[dict]:
    """Match pain point entries (Reddit posts or agent-team themes) to M.O.T services."""
    matched = []
    for post in posts:
        text = " ".join([
            post.get("title", ""),
            post.get("excerpt", ""),
            post.get("theme", ""),
            " ".join(post.get("sample_complaints", []) if isinstance(post.get("sample_complaints"), list) else []),
        ]).lower()
        pid = _post_id(post)
        matched_service = None
        for service_key, service in SERVICES.items():
            if service_key == "general":
                continue
            for kw in service["keywords"]:
                if kw.lower() in text:
                    matched_service = service_key
                    matched.append({
                        **post,
                        "url": post.get("url", ""),  # ensure url key exists
                        "matched_service": service_key,
                        "service_name": service["name"],
                        "matched_keyword": kw,
                    })
                    break
            if matched_service:
                break

    # If no specific match, tag as general
    matched_ids = {_post_id(m) for m in matched}
    for post in posts:
        if _post_id(post) not in matched_ids:
            matched.append({
                **post,
                "url": post.get("url", ""),
                "matched_service": "general",
                "service_name": SERVICES["general"]["name"],
                "matched_keyword": "",
            })

    return matched


def generate_social_posts(pain_points: list[dict]) -> list[dict]:
    """Generate social media posts from matched pain points."""
    print("── Generating social media posts ──")
    posts = []

    # Group pain points by service
    by_service: dict[str, list[dict]] = {}
    for pp in pain_points:
        service = pp.get("matched_service", "general")
        by_service.setdefault(service, []).append(pp)

    for service_key, service_painpoints in by_service.items():
        service = SERVICES.get(service_key, SERVICES["general"])
        # Generate up to 3 posts per service
        for i, pp in enumerate(service_painpoints[:3]):
            post = _create_post(service_key, service, pp, i)
            posts.append(post)

    # Also create general brand posts
    brand_posts = _create_brand_posts()
    posts.extend(brand_posts)

    print(f"  ✍️  Generated {len(posts)} social media posts")
    return posts


def _create_post(service_key: str, service: dict, pain_point: dict, variant: int) -> dict:
    """Create a single social media post for a service/pain point."""
    title = pain_point.get("title", "")
    subreddit = pain_point.get("subreddit", "")
    angle = service["angle"]
    hashtags = " ".join(service["hashtags"])

    templates = [
        f"We keep seeing this in r/{subreddit}: \"{title[:80]}...\"\n\n"
        f"You're not alone. {angle}\n\n"
        f"M.O.T Innovation builds the infrastructure that makes this a solved problem.\n\n"
        f"Book a free consult → motinnovation.co.za\n{hashtags}",

        f"🧵 Pain point we see again and again:\n\n"
        f"{title[:100]}\n\n"
        f"The fix isn't more tools — it's better infrastructure.\n"
        f"{service['name']} from M.O.T Innovation.\n\n"
        f"Free consultation → motinnovation.co.za\n{hashtags}",

        f"Hot take: {angle}\n\n"
        f"Saw this today — \"{title[:80]}...\"\n\n"
        f"This is exactly what we fix at M.O.T Innovation.\n"
        f"We don't build slide decks. We build working systems.\n\n"
        f"motinnovation.co.za | {hashtags}",
    ]

    return {
        "id": f"post_{service_key}_{variant}_{datetime.now().strftime('%Y%m%d%H%M')}",
        "service": service_key,
        "service_name": service["name"],
        "platform": "linkedin",  # Default platform
        "content": templates[variant % len(templates)],
        "hashtags": service["hashtags"],
        "source_painpoint": title[:100],
        "source_subreddit": subreddit,
        "source_url": pain_point.get("url", ""),
        "generated_at": datetime.now().isoformat(),
    }


def _create_brand_posts() -> list[dict]:
    """Create general brand awareness posts."""
    brand_content = [
        {
            "content": "Marketing intelligence isn't about more tools. It's about making the tools you have work together.\n\n"
                       "DAM → Delivery → Tracking → Optimization\n\n"
                       "One system. One source of truth. That's what we build at M.O.T Innovation.\n\n"
                       "Book a free consult → motinnovation.co.za\n#MarketingIntelligence #MOTInnovation",
            "platform": "linkedin",
            "service": "general",
        },
        {
            "content": "We don't build slide decks. We build working systems. 🚀\n\n"
                       "Marketing intelligence infrastructure that your team actually uses.\n"
                       "You own everything we build. We train your team. Then we hand over the keys.\n\n"
                       "motinnovation.co.za\n#MarketingInfrastructure #MarketingOps",
            "platform": "twitter",
            "service": "general",
        },
        {
            "content": "How much time does your team waste:\n\n"
                       "❌ Searching for files across Google Drive, Dropbox, and laptops\n"
                       "❌ Manually posting to each social platform\n"
                       "❌ Building reports nobody reads\n\n"
                       "If the answer is 'a lot' — we should talk.\n"
                       "M.O.T Innovation builds the infrastructure that fixes this.\n\n"
                       "Free consult → motinnovation.co.za\n#MarketingEfficiency",
            "platform": "linkedin",
            "service": "general",
        },
        {
            "content": "80% reduction in content production time.\n23% improvement in conversion rate.\n\n"
                       "Those aren't marketing claims. Those are results from proper marketing intelligence infrastructure.\n\n"
                       "What could we do for you?\n\n"
                       "motinnovation.co.za\n#MarketingIntelligence #CaseStudy",
            "platform": "instagram",
            "service": "general",
        },
    ]

    posts = []
    for i, bc in enumerate(brand_content):
        posts.append({
            "id": f"post_brand_{i}_{datetime.now().strftime('%Y%m%d%H%M')}",
            "service": bc["service"],
            "service_name": "Marketing Intelligence Infrastructure",
            "platform": bc["platform"],
            "content": bc["content"],
            "hashtags": ["#MarketingIntelligence", "#MOTInnovation"],
            "source_painpoint": "brand-awareness",
            "source_subreddit": "",
            "source_url": "",
            "generated_at": datetime.now().isoformat(),
        })
    return posts


def schedule_posts(posts: list[dict]) -> dict:
    """Schedule posts into a content calendar (next 30 days)."""
    print("── Scheduling posts into content calendar ──")

    # Distribute posts across platforms and days
    platform_rotation = ["linkedin", "twitter", "instagram", "facebook"]
    start_date = datetime.now() + timedelta(days=1)

    scheduled = []
    for i, post in enumerate(posts):
        day_offset = i // 2  # 2 posts per day
        post_date = start_date + timedelta(days=day_offset)
        platform = platform_rotation[i % len(platform_rotation)]

        post["platform"] = platform
        post["scheduled_date"] = post_date.strftime("%Y-%m-%d")
        post["scheduled_time"] = f"{9 + (i % 8):02d}:00"  # Spread across 9am-4pm
        post["status"] = "scheduled"

        scheduled.append({
            "id": post["id"],
            "date": post["scheduled_date"],
            "time": post["scheduled_time"],
            "platform": platform,
            "service": post["service"],
            "preview": post["content"][:80] + "...",
            "status": "scheduled",
        })

    calendar_data = {
        "generated_at": datetime.now().isoformat(),
        "total_posts": len(scheduled),
        "date_range": {
            "start": scheduled[0]["date"] if scheduled else "",
            "end": scheduled[-1]["date"] if scheduled else "",
        },
        "platforms": list(platform_rotation),
        "schedule": scheduled,
    }

    # Write JSON calendar
    with open(CALENDAR_JSON, "w", encoding="utf-8") as f:
        json.dump(calendar_data, f, indent=2, ensure_ascii=False)

    # Write markdown calendar
    lines = [
        "# M.O.T Innovation — Content Calendar",
        "",
        f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_",
        f"_Total posts: {len(scheduled)} | Date range: {calendar_data['date_range']['start']} → {calendar_data['date_range']['end']}_",
        "",
        "---",
        "",
        "| Date | Time | Platform | Service | Preview | Status |",
        "|------|------|----------|---------|---------|--------|",
    ]
    for s in scheduled:
        preview = s["preview"].replace("|", "/")
        lines.append(f"| {s['date']} | {s['time']} | {s['platform']} | {s['service']} | {preview} | {s['status']} |")

    lines.extend([
        "",
        "---",
        "",
        "## Full Post Content",
        "",
    ])

    for post in posts:
        lines.extend([
            f"### {post['id']} — {post['platform'].title()} — {post['scheduled_date']} at {post['scheduled_time']}",
            f"**Service:** {post['service_name']}",
            f"**Source:** {post.get('source_painpoint', 'brand')}",
            "",
            "```",
            post["content"],
            "```",
            "",
        ])

    CALENDAR_FILE.write_text("\n".join(lines), encoding="utf-8")

    print(f"  📅 Scheduled {len(scheduled)} posts")
    print(f"  📄 Calendar (MD):  {CALENDAR_FILE}")
    print(f"  📄 Calendar (JSON): {CALENDAR_JSON}")
    return calendar_data


def main() -> int:
    parser = argparse.ArgumentParser(
        description="M.O.T Innovation — Social Media Content Pipeline"
    )
    parser.add_argument("--scan-only", action="store_true",
                        help="Only scan Reddit for pain points")
    parser.add_argument("--generate-only", action="store_true",
                        help="Only generate posts from existing pain points")
    parser.add_argument("--schedule-only", action="store_true",
                        help="Only generate calendar from existing posts")
    parser.add_argument("--verbose", action="store_true",
                        help="Show full post content")
    args = parser.parse_args()

    print("=" * 60)
    print("M.O.T INNOVATION — SOCIAL MEDIA CONTENT PIPELINE")
    print("=" * 60)

    # Step 1: Scan Reddit for pain points
    pain_points_data = []
    if not args.generate_only and not args.schedule_only:
        print("\n📥 Step 1: Scanning for pain points")
        reddit_posts = scan_reddit()
        existing = load_existing_painpoints()
        pain_points_data = reddit_posts + existing

        # Save pain points
        with open(PAINPOINTS_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "scanned_at": datetime.now().isoformat(),
                "total_pain_points": len(pain_points_data),
                "reddit_posts": len(reddit_posts),
                "existing_themes": len(existing),
                "pain_points": pain_points_data,
            }, f, indent=2, ensure_ascii=False)
        print(f"  💾 Saved to {PAINPOINTS_FILE}")

        if args.scan_only:
            return 0

    # Step 2: Match pain points to services and generate posts
    posts = []
    if not args.schedule_only:
        print("\n📝 Step 2: Generating social media posts")
        if not pain_points_data:
            # Load from file
            if PAINPOINTS_FILE.exists():
                with open(PAINPOINTS_FILE, "r", encoding="utf-8") as f:
                    pain_points_data = json.load(f).get("pain_points", [])

        if pain_points_data:
            matched = match_posts_to_services(pain_points_data)
            posts = generate_social_posts(matched)
        else:
            print("  ⚠️  No pain points found — generating brand posts only")
            posts = _create_brand_posts()

        # Save posts
        with open(POSTS_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "total_posts": len(posts),
                "posts": posts,
            }, f, indent=2, ensure_ascii=False)
        print(f"  💾 Saved to {POSTS_FILE}")

        if args.verbose:
            print(f"\n{'─' * 60}")
            for post in posts:
                print(f"\n📝 {post['id']} [{post['platform']}]")
                print(f"   Service: {post['service_name']}")
                print(f"   Source: {post.get('source_painpoint', 'brand')}")
                print(f"{'─' * 40}")
                print(post["content"])
                print()

        if args.generate_only:
            return 0

    # Step 3: Schedule posts
    print("\n📅 Step 3: Scheduling posts")
    if not posts:
        if POSTS_FILE.exists():
            with open(POSTS_FILE, "r", encoding="utf-8") as f:
                posts = json.load(f).get("posts", [])

    if posts:
        schedule_posts(posts)
    else:
        print("  ⚠️  No posts to schedule")

    print(f"\n✅ Content pipeline complete!")
    print(f"📁 Pain points: {PAINPOINTS_FILE}")
    print(f"📁 Social posts: {POSTS_FILE}")
    print(f"📁 Calendar:     {CALENDAR_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())