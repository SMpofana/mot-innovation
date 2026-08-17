#!/usr/bin/env python
"""
script_generator.py — M.O.T Innovation Content Script Generator

Generates YouTube Short scripts (60s) and LinkedIn posts from pain points
using the PAS formula (Problem-Agitate-Solution). Template-based generation
requires no API key.

Each script is saved as a markdown file with:
    - Title, description, tags (for YouTube SEO)
    - Visual cues (what appears on screen)
    - Voiceover text (what the AI voice says)
    - CTA (call to action with UTM-tracked link)
    - Metadata block for downstream tools

Usage:
    # Generate a YouTube Short script
    python script_generator.py --pain-point disconnected_tools --service dam --type short

    # Generate a LinkedIn post
    python script_generator.py --pain-point manual_posting --service delivery --type linkedin

    # Generate both (default)
    python script_generator.py --pain-point scattered_assets --service dam

    # List available pain points and services
    python script_generator.py --list

    # Generate from a custom pain point string
    python script_generator.py --custom "My team wastes hours on manual reporting" --service tracking
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Make the package importable when run as a script
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from data import (  # noqa: E402
    BRAND_NAME, WEBSITE_URL, BOOKING_URL,
    PAIN_POINTS, SERVICES, CASE_STUDIES,
    get_pain_point, get_service, case_studies_for_service,
)

# AI enhancement (falls back to templates if no API key)
try:
    from gemini_enhancer import (
        enhance_hook, enhance_problem, enhance_solution, enhance_linkedin_post, check_api
    )
    GEMINI_AVAILABLE = check_api()
except ImportError:
    GEMINI_AVAILABLE = False

OUTPUT_DIR = SCRIPT_DIR / "scripts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ── UTM link builder ──────────────────────────────────────────────────────────
def build_utm_link(content_type: str, pain_point_id: str, service_id: str) -> str:
    """Build a UTM-tracked link for the given content piece."""
    utm = (
        f"{WEBSITE_URL}/contact"
        f"?utm_source=content_engine"
        f"&utm_medium={content_type}"
        f"&utm_campaign={pain_point_id}"
        f"&utm_content={service_id}"
    )
    return utm


# ── YouTube Short (60s) script ────────────────────────────────────────────────
def generate_youtube_short(pain_point: dict, service: dict, case_study: dict | None = None) -> dict:
    """
    Generate a 60-second YouTube Short script using the PAS formula.

    Structure:
        0-5s   — Hook (aggressive pain point statement)
        5-15s  — Problem agitation (stat + emotional trigger)
        15-45s — Solution (how M.O.T Innovation solves it)
        45-60s — CTA (book a free consultation)

    Returns a dict with all script data and metadata.
    """
    pp_title = pain_point["title"]
    pp_stat = pain_point["stat"]
    pp_summary = pain_point["summary"]
    svc_name = service["name"]
    svc_angle = service["angle"]
    svc_deliverable = service["deliverable"]
    svc_hashtags = " ".join(service["hashtags"])

    utm_link = build_utm_link("youtube_short", pain_point["id"], service["id"])

    # Case study reference if available
    cs_text = ""
    if case_study:
        cs_text = f" Like {case_study['client']}: {case_study['result']}"
    elif case_studies_for_service(service["id"]):
        cs = case_studies_for_service(service["id"])[0]
        cs_text = f" Like {cs['client']}: {cs['result']}"

    # AI-enhanced content (falls back to templates if Gemini unavailable)
    hook_vo = f"{pp_title}. Every week you stay stuck, it costs you time and money."
    problem_vo = f"{pp_summary} {pp_stat} That's hours lost and budget wasted — every single week you don't fix it."
    solution_vo = f"{svc_angle} {BRAND_NAME} builds {svc_name}. {service['description'][:120]} {cs_text}"

    if GEMINI_AVAILABLE:
        ai_hook = enhance_hook(pp_title, pp_stat)
        if ai_hook:
            hook_vo = ai_hook
        ai_problem = enhance_problem(pp_title, pp_stat, pp_summary)
        if ai_problem:
            problem_vo = ai_problem
        ai_solution = enhance_solution(svc_name, service['description'][:120], svc_angle, cs_text)
        if ai_solution:
            solution_vo = ai_solution

    script_sections = [
        {
            "section": "Hook",
            "timing": "0-5s",
            "visual": f"[VISUAL: Bold text on dark background — \"{pp_title}\"]\n[VISUAL: Fast zoom-in effect, dramatic music sting]\n[VISUAL: Animated counter ticking up — hours/money lost]",
            "voiceover": hook_vo,
        },
        {
            "section": "Problem Agitation",
            "timing": "5-15s",
            "visual": f"[VISUAL: Split screen — messy folders / multiple browser tabs / frustrated person]\n[VISUAL: Text overlay — \"{pp_stat}\"]\n[VISUAL: Animated red X over scattered tools, clock spinning — time bleeding away]",
            "voiceover": problem_vo,
        },
        {
            "section": "Solution",
            "timing": "15-45s",
            "visual": f"[VISUAL: Clean dashboard interface, organized asset library, automated workflow diagram]\n[VISUAL: Screen recording of {service['short']} system in action]\n[VISUAL: Text overlay — \"{svc_deliverable}\"]\n[VISUAL: Animated green checkmarks connecting tools, clock slowing to a stop]" + (f"\n[VISUAL: Text overlay — \"{case_study['result_stat']}\"]" if case_study else ""),
            "voiceover": solution_vo,
        },
        {
            "section": "CTA",
            "timing": "45-60s",
            "visual": f"[VISUAL: Logo — {BRAND_NAME}]\n[VISUAL: Text overlay — \"Book a Free Consultation\"]\n[VISUAL: URL on screen — {utm_link}]\n[VISUAL: Animated arrow pointing to the CTA button]",
            "voiceover": f"Book a free consultation at motinnovation.co.za. We don't build slide decks — we build working systems. Link in the description.",
        },
    ]

    # Build full script markdown
    md_lines = [
        f"# YouTube Short Script — {pp_title}",
        "",
        f"**Pain Point:** {pp_title}",
        f"**Service:** {svc_name}",
        f"**Duration:** 60 seconds",
        f"**Formula:** PAS (Problem-Agitate-Solution)",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
    ]

    full_voiceover = []
    for s in script_sections:
        md_lines.extend([
            f"## {s['section']} ({s['timing']})",
            "",
            f"**Visual:**",
            f"```",
            s["visual"],
            f"```",
            "",
            f"**Voiceover:**",
            f"```",
            s["voiceover"],
            f"```",
            "",
        ])
        full_voiceover.append(s["voiceover"])

    md_lines.extend([
        "---",
        "",
        "## Full Voiceover Text (for TTS)",
        "",
        " ".join(full_voiceover),
        "",
        "---",
        "",
        "## Metadata",
        "",
        f"**Title:** {pp_title} — How We Fix It | {BRAND_NAME}",
        f"**Description:** {pp_summary} {svc_angle} Book a free consultation at {utm_link}",
        f"**Tags:** marketing, marketing automation, {service['short'].lower()}, {pain_point['id'].replace('_', ' ')}, marketing infrastructure, faceless content",
        f"**Hashtags:** {svc_hashtags} #MOTInnovation #MarketingShorts",
        f"**UTM Link:** {utm_link}",
        f"**Category:** Education",
        f"**Privacy:** Public",
        "",
    ])

    script_md = "\n".join(md_lines)

    # Title for filename
    safe_title = re.sub(r"[^a-z0-9]+", "_", pp_title.lower()).strip("_")
    filename = f"yt_short_{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = OUTPUT_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(script_md)

    return {
        "type": "youtube_short",
        "pain_point_id": pain_point["id"],
        "pain_point": pp_title,
        "service_id": service["id"],
        "service_name": svc_name,
        "title": f"{pp_title} — How We Fix It | {BRAND_NAME}",
        "description": f"{pp_summary} {svc_angle} Book a free consultation at {utm_link}",
        "tags": f"marketing, marketing automation, {service['short'].lower()}, {pain_point['id'].replace('_', ' ')}, marketing infrastructure, faceless content",
        "hashtags": svc_hashtags + " #MOTInnovation #MarketingShorts",
        "utm_link": utm_link,
        "voiceover_text": " ".join(full_voiceover),
        "sections": script_sections,
        "script_markdown": script_md,
        "file_path": str(filepath),
        "generated_at": datetime.now().isoformat(),
    }


# ── LinkedIn post ─────────────────────────────────────────────────────────────
def generate_linkedin_post(pain_point: dict, service: dict, case_study: dict | None = None) -> dict:
    """
    Generate a LinkedIn post from a pain point using the PAS formula.

    Returns a dict with the post content and metadata.
    """
    pp_title = pain_point["title"]
    pp_stat = pain_point["stat"]
    pp_summary = pain_point["summary"]
    svc_name = service["name"]
    svc_angle = service["angle"]
    svc_deliverable = service["deliverable"]
    svc_hashtags = " ".join(service["hashtags"])

    utm_link = build_utm_link("linkedin_post", pain_point["id"], service["id"])

    # Case study reference
    cs = case_study or (case_studies_for_service(service["id"])[0] if case_studies_for_service(service["id"]) else None)
    cs_text = ""
    if cs:
        cs_text = f"\n\nResult for {cs['client']}: {cs['result']}"

    post_content = f"""{pp_stat}

{pp_summary}

Every week you stay stuck, that's hours lost and budget wasted — money you'll never get back.

The fix isn't more tools. It's better infrastructure.

{svc_angle}

{BRAND_NAME} builds {svc_name} that makes this a solved problem.
{svc_deliverable}.{cs_text}

We don't build slide decks. We build working systems.
You own everything we build. We train your team. Then we hand over the keys.

Book a free consultation → {utm_link}

{svc_hashtags} #MOTInnovation"""

    md_lines = [
        f"# LinkedIn Post — {pp_title}",
        "",
        f"**Pain Point:** {pp_title}",
        f"**Service:** {svc_name}",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
        "## Post Content",
        "",
        "```",
        post_content,
        "```",
        "",
        "---",
        "",
        "## Metadata",
        "",
        f"**UTM Link:** {utm_link}",
        f"**Hashtags:** {svc_hashtags} #MOTInnovation",
        f"**Target Audience:** Marketing leaders, business owners, startup founders",
        f"**Funnel Stage:** Awareness → Consideration",
        "",
    ]

    script_md = "\n".join(md_lines)

    safe_title = re.sub(r"[^a-z0-9]+", "_", pp_title.lower()).strip("_")
    filename = f"linkedin_post_{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = OUTPUT_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(script_md)

    return {
        "type": "linkedin_post",
        "pain_point_id": pain_point["id"],
        "pain_point": pp_title,
        "service_id": service["id"],
        "service_name": svc_name,
        "post_content": post_content,
        "utm_link": utm_link,
        "hashtags": svc_hashtags + " #MOTInnovation",
        "script_markdown": script_md,
        "file_path": str(filepath),
        "generated_at": datetime.now().isoformat(),
    }


# ── CLI ──────────────────────────────────────────────────────────────────────
def list_options() -> None:
    """Print available pain points and services."""
    print("\n=== Pain Points ===")
    for pp in PAIN_POINTS:
        print(f"  {pp['id']:30s} — {pp['title']}")
    print("\n=== Services ===")
    for sid, svc in SERVICES.items():
        print(f"  {sid:15s} — {svc['name']}")
    print(f"\n=== Case Studies ===")
    for cs in CASE_STUDIES:
        print(f"  {cs['id']:20s} — {cs['client']}: {cs['result_stat']}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="M.O.T Innovation — Content Script Generator (PAS formula)"
    )
    parser.add_argument("--pain-point", type=str, default=None,
                        help="Pain point ID (see --list)")
    parser.add_argument("--service", type=str, default=None,
                        help="Service ID (see --list)")
    parser.add_argument("--case-study", type=str, default=None,
                        help="Case study ID to reference (optional)")
    parser.add_argument("--type", choices=["short", "linkedin", "both"], default="both",
                        help="Type of content to generate (default: both)")
    parser.add_argument("--custom", type=str, default=None,
                        help="Custom pain point text (instead of --pain-point ID)")
    parser.add_argument("--list", action="store_true",
                        help="List available pain points, services, and case studies")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Output directory for scripts (default: scripts/)")
    args = parser.parse_args()

    if args.list:
        list_options()
        return 0

    global OUTPUT_DIR
    if args.output_dir:
        OUTPUT_DIR = Path(args.output_dir)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Determine pain point
    if args.custom:
        pain_point = {
            "id": "custom",
            "title": args.custom[:80],
            "summary": args.custom,
            "stat": "",
            "subreddit_keywords": [],
        }
    elif args.pain_point:
        pain_point = get_pain_point(args.pain_point)
    else:
        print("Error: provide --pain-point ID or --custom text, or use --list to see options.")
        return 1

    # Determine service
    if args.service:
        service = get_service(args.service)
    else:
        # Auto-match: find the first service that addresses this pain point
        matched = [s for s in SERVICES.values() if pain_point["id"] in s["keywords"]]
        service = matched[0] if matched else SERVICES["dam"]

    # Determine case study
    case_study = None
    if args.case_study:
        from data import get_case_study
        case_study = get_case_study(args.case_study)
    else:
        cs_list = case_studies_for_service(service["id"])
        if cs_list:
            case_study = cs_list[0]

    print(f"\n{'=' * 60}")
    print(f"CONTENT SCRIPT GENERATOR — {BRAND_NAME}")
    print(f"{'=' * 60}")
    print(f"Pain Point:  {pain_point['title']}")
    print(f"Service:     {service['name']}")
    if case_study:
        print(f"Case Study:  {case_study['client']}")
    print()

    results = []

    if args.type in ("short", "both"):
        print("📝 Generating YouTube Short script...")
        result = generate_youtube_short(pain_point, service, case_study)
        results.append(result)
        print(f"   ✅ Saved: {result['file_path']}")
        print(f"   📎 Title: {result['title']}")

    if args.type in ("linkedin", "both"):
        print("📝 Generating LinkedIn post...")
        result = generate_linkedin_post(pain_point, service, case_study)
        results.append(result)
        print(f"   ✅ Saved: {result['file_path']}")

    # Save a manifest JSON alongside scripts
    manifest_path = OUTPUT_DIR / f"manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "pain_point": pain_point["title"],
            "service": service["name"],
            "results": results,
        }, f, indent=2, ensure_ascii=False)
    print(f"\n📋 Manifest: {manifest_path}")
    print(f"\n✅ Done! Generated {len(results)} script(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())