#!/usr/bin/env python
"""
linkedin_carousel.py — M.O.T Innovation LinkedIn Carousel Generator

Generates LinkedIn carousel slide content as:
    1. JSON with slide-by-slide text (6 slides: stat, problem, what others try, what we do, result, CTA)
    2. Canva-compatible format (slide dimensions, text positions, background colors)
    3. PDF-ready markdown for export

LinkedIn carousels are uploaded as PDFs — native carousel format.

Usage:
    # Generate a carousel from a pain point
    python linkedin_carousel.py --pain-point disconnected_tools --service dam

    # Generate from a case study
    python linkedin_carousel.py --case-study ecommerce

    # Generate carousels for all pain points
    python linkedin_carousel.py --all

    # Export as PDF-ready markdown
    python linkedin_carousel.py --pain-point manual_reporting --service tracking --format markdown
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
    BRAND_NAME, WEBSITE_URL, BOOKING_URL,
    PAIN_POINTS, SERVICES, CASE_STUDIES,
    get_pain_point, get_service, get_case_study, case_studies_for_service,
)

CAROUSEL_DIR = SCRIPT_DIR / "carousels"
CAROUSEL_DIR.mkdir(parents=True, exist_ok=True)

# LinkedIn carousel slide dimensions (1080x1080 for square, 1080x1350 for portrait)
SLIDE_WIDTH = 1080
SLIDE_HEIGHT = 1350  # Portrait — recommended for LinkedIn carousels

# Brand colors (monochrome, trionn-style)
COLORS = {
    "bg_dark": "#0a0a0a",
    "bg_accent": "#1a1a1a",
    "text_white": "#FFFFFF",
    "text_gray": "#999999",
    "accent_blue": "#3B82F6",
    "accent_green": "#22C55E",
    "accent_red": "#EF4444",
}


def generate_carousel(pain_point: dict, service: dict, case_study: dict | None = None) -> dict:
    """
    Generate a 6-slide LinkedIn carousel.

    Slides:
        1. Stat hook
        2. Problem
        3. What others try (and why it fails)
        4. What we do differently
        5. Result (case study proof)
        6. CTA

    Returns a dict with the carousel content and Canva-compatible design spec.
    """
    pp_title = pain_point["title"]
    pp_stat = pain_point["stat"]
    pp_summary = pain_point["summary"]
    svc_name = service["name"]
    svc_angle = service["angle"]
    svc_deliverable = service["deliverable"]
    svc_hashtags = " ".join(service["hashtags"])

    # Case study
    cs = case_study
    if not cs:
        cs_list = case_studies_for_service(service["id"])
        cs = cs_list[0] if cs_list else CASE_STUDIES[0]

    utm_link = (
        f"{WEBSITE_URL}/contact"
        f"?utm_source=content_engine"
        f"&utm_medium=linkedin_carousel"
        f"&utm_campaign={pain_point['id']}"
        f"&utm_content={service['id']}"
    )

    # ── 6 slides ──────────────────────────────────────────────────────────────
    slides = [
        {
            "slide_number": 1,
            "type": "stat_hook",
            "title": "Stat Hook",
            "headline": pp_stat,
            "subheadline": pp_title,
            "body": None,
            "design": {
                "background_color": COLORS["bg_dark"],
                "text_color": COLORS["text_white"],
                "accent_color": COLORS["accent_blue"],
                "text_positions": {
                    "headline": {"x": "center", "y": "40%", "font_size": 72, "font_weight": "bold"},
                    "subheadline": {"x": "center", "y": "60%", "font_size": 36, "font_weight": "normal", "color": COLORS["text_gray"]},
                },
                "elements": [
                    {"type": "slide_number", "position": "top_right", "text": "1/6", "color": COLORS["text_gray"]},
                    {"type": "accent_bar", "position": "top", "width": "100%", "height": "8px", "color": COLORS["accent_blue"]},
                ],
            },
        },
        {
            "slide_number": 2,
            "type": "problem",
            "title": "The Problem",
            "headline": "The Problem",
            "subheadline": None,
            "body": pp_summary,
            "design": {
                "background_color": COLORS["bg_dark"],
                "text_color": COLORS["text_white"],
                "accent_color": COLORS["accent_red"],
                "text_positions": {
                    "headline": {"x": "center", "y": "20%", "font_size": 48, "font_weight": "bold", "color": COLORS["accent_red"]},
                    "body": {"x": "center", "y": "50%", "font_size": 32, "font_weight": "normal", "max_width": "80%"},
                },
                "elements": [
                    {"type": "slide_number", "position": "top_right", "text": "2/6", "color": COLORS["text_gray"]},
                ],
            },
        },
        {
            "slide_number": 3,
            "type": "what_others_try",
            "title": "What Others Try",
            "headline": "What Most Businesses Try",
            "subheadline": None,
            "body": "❌ More tools (that don't talk to each other)\n❌ Manual workarounds and spreadsheets\n❌ Hiring more people instead of building systems\n❌ Another consultant with a slide deck",
            "design": {
                "background_color": COLORS["bg_accent"],
                "text_color": COLORS["text_white"],
                "accent_color": COLORS["accent_red"],
                "text_positions": {
                    "headline": {"x": "center", "y": "15%", "font_size": 42, "font_weight": "bold"},
                    "body": {"x": "center", "y": "50%", "font_size": 30, "font_weight": "normal", "line_height": 1.8, "max_width": "80%"},
                },
                "elements": [
                    {"type": "slide_number", "position": "top_right", "text": "3/6", "color": COLORS["text_gray"]},
                ],
            },
        },
        {
            "slide_number": 4,
            "type": "what_we_do",
            "title": "What We Do Differently",
            "headline": "What We Do",
            "subheadline": svc_name,
            "body": f"✅ {svc_angle}\n✅ {svc_deliverable}\n✅ We build the actual system, not a recommendation\n✅ You own everything. We train your team. We hand over the keys.",
            "design": {
                "background_color": COLORS["bg_dark"],
                "text_color": COLORS["text_white"],
                "accent_color": COLORS["accent_green"],
                "text_positions": {
                    "headline": {"x": "center", "y": "12%", "font_size": 42, "font_weight": "bold"},
                    "subheadline": {"x": "center", "y": "22%", "font_size": 28, "font_weight": "normal", "color": COLORS["accent_blue"]},
                    "body": {"x": "center", "y": "50%", "font_size": 28, "font_weight": "normal", "line_height": 1.8, "max_width": "80%"},
                },
                "elements": [
                    {"type": "slide_number", "position": "top_right", "text": "4/6", "color": COLORS["text_gray"]},
                ],
            },
        },
        {
            "slide_number": 5,
            "type": "result",
            "title": "The Result",
            "headline": "The Result",
            "subheadline": cs["result_stat"],
            "body": f"Client: {cs['client']}\n\nChallenge: {cs['challenge'][:150]}...\n\nSolution: {cs['solution'][:150]}...\n\nResult: {cs['result']}",
            "design": {
                "background_color": COLORS["bg_accent"],
                "text_color": COLORS["text_white"],
                "accent_color": COLORS["accent_green"],
                "text_positions": {
                    "headline": {"x": "center", "y": "10%", "font_size": 42, "font_weight": "bold"},
                    "subheadline": {"x": "center", "y": "20%", "font_size": 36, "font_weight": "bold", "color": COLORS["accent_green"]},
                    "body": {"x": "center", "y": "50%", "font_size": 24, "font_weight": "normal", "line_height": 1.6, "max_width": "85%", "color": COLORS["text_gray"]},
                },
                "elements": [
                    {"type": "slide_number", "position": "top_right", "text": "5/6", "color": COLORS["text_gray"]},
                ],
            },
        },
        {
            "slide_number": 6,
            "type": "cta",
            "title": "Call to Action",
            "headline": "Book a Free Consultation",
            "subheadline": None,
            "body": f"We don't build slide decks.\nWe build working systems.\n\n{WEBSITE_URL}",
            "design": {
                "background_color": COLORS["bg_dark"],
                "text_color": COLORS["text_white"],
                "accent_color": COLORS["accent_blue"],
                "text_positions": {
                    "headline": {"x": "center", "y": "30%", "font_size": 56, "font_weight": "bold"},
                    "body": {"x": "center", "y": "60%", "font_size": 32, "font_weight": "normal", "line_height": 1.8, "color": COLORS["text_gray"]},
                },
                "elements": [
                    {"type": "logo", "position": "center", "y": "85%", "text": BRAND_NAME, "color": COLORS["text_white"]},
                    {"type": "slide_number", "position": "top_right", "text": "6/6", "color": COLORS["text_gray"]},
                    {"type": "accent_bar", "position": "bottom", "width": "100%", "height": "8px", "color": COLORS["accent_blue"]},
                ],
            },
        },
    ]

    carousel = {
        "metadata": {
            "title": f"LinkedIn Carousel — {pp_title}",
            "pain_point_id": pain_point["id"],
            "pain_point": pp_title,
            "service_id": service["id"],
            "service_name": svc_name,
            "case_study": cs["client"],
            "utm_link": utm_link,
            "hashtags": f"{svc_hashtags} #MOTInnovation #MarketingCarousel",
            "generated_at": datetime.now().isoformat(),
            "platform": "LinkedIn",
            "format": "PDF carousel (6 slides)",
        },
        "canva_spec": {
            "tool": "Canva (free)",
            "slide_dimensions": {"width": SLIDE_WIDTH, "height": SLIDE_HEIGHT, "unit": "px"},
            "template_search": "Search Canva for 'dark minimalist LinkedIn carousel' or 'carousel presentation'",
            "export_format": "PDF (for LinkedIn native carousel upload)",
            "color_palette": list(COLORS.values()),
            "font_recommendation": "Montserrat or Inter — clean sans-serif",
            "design_notes": [
                "Keep text minimal — slides should be scannable in 2-3 seconds each",
                "Use the same layout pattern across all slides for consistency",
                "Slide numbers (1/6, 2/6, etc.) in top-right corner",
                "Accent bar at top or bottom for visual continuity",
                "Dark background (#0a0a0a) with white text — trionn-style monochrome",
            ],
        },
        "slides": slides,
    }

    return carousel


def carousel_to_markdown(carousel: dict) -> str:
    """
    Convert a carousel dict to PDF-ready markdown.

    Each slide is formatted as a section that can be printed/exported to PDF.
    """
    meta = carousel["metadata"]
    lines = [
        f"# {meta['title']}",
        "",
        f"**Pain Point:** {meta['pain_point']}  ",
        f"**Service:** {meta['service_name']}  ",
        f"**Case Study:** {meta['case_study']}  ",
        f"**Hashtags:** {meta['hashtags']}  ",
        f"**UTM Link:** {meta['utm_link']}  ",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
        "## Canva Design Spec",
        "",
        f"- **Slide dimensions:** {SLIDE_WIDTH}×{SLIDE_HEIGHT}px (portrait)",
        f"- **Export format:** PDF for LinkedIn carousel upload",
        f"- **Template:** Search Canva for 'dark minimalist LinkedIn carousel'",
        f"- **Font:** Montserrat or Inter (clean sans-serif)",
        f"- **Color palette:** Dark bg (#0a0a0a), white text (#FFFFFF), gray (#999999), blue accent (#3B82F6), green accent (#22C55E)",
        "",
        "### Design Notes",
        "",
        "1. Keep text minimal — slides should be scannable in 2-3 seconds each",
        "2. Use the same layout pattern across all slides for consistency",
        "3. Slide numbers (1/6, 2/6, etc.) in top-right corner",
        "4. Accent bar at top or bottom for visual continuity",
        "5. Dark background with white text — trionn-style monochrome",
        "",
        "---",
        "",
    ]

    for slide in carousel["slides"]:
        lines.extend([
            f"## Slide {slide['slide_number']}/6 — {slide['title']}",
            "",
        ])

        if slide.get("headline"):
            lines.append(f"**Headline:** {slide['headline']}")
            lines.append("")

        if slide.get("subheadline"):
            lines.append(f"**Subheadline:** {slide['subheadline']}")
            lines.append("")

        if slide.get("body"):
            lines.append(f"**Body:**")
            lines.append("")
            lines.append("```")
            lines.append(slide["body"])
            lines.append("```")
            lines.append("")

        design = slide.get("design", {})
        lines.extend([
            "**Design spec:**",
            f"- Background: {design.get('background_color', '#0a0a0a')}",
            f"- Text: {design.get('text_color', '#FFFFFF')}",
            f"- Accent: {design.get('accent_color', '#3B82F6')}",
            "",
        ])

        if design.get("text_positions"):
            lines.append("**Text positions:**")
            for elem, pos in design["text_positions"].items():
                font_size = pos.get("font_size", "—")
                font_weight = pos.get("font_weight", "normal")
                x = pos.get("x", "center")
                y = pos.get("y", "center")
                lines.append(f"  - {elem}: {x} / {y} — {font_size}px {font_weight}")
            lines.append("")

        lines.extend([
            "---",
            "",
        ])

    lines.extend([
        "## LinkedIn Post Caption (to accompany carousel)",
        "",
        f"{meta['pain_point']} — here's how we fix it.",
        "",
        "Swipe through to see the problem, what others try, and what we do differently.",
        "",
        f"Book a free consultation → {meta['utm_link']}",
        "",
        f"{meta['hashtags']}",
        "",
    ])

    return "\n".join(lines)


def save_carousel(carousel: dict, output_dir: Path | None = None, format: str = "json") -> list[Path]:
    """
    Save a carousel as JSON and optionally as markdown.

    Returns list of saved file paths.
    """
    if output_dir is None:
        output_dir = CAROUSEL_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    pp_id = carousel["metadata"]["pain_point_id"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = re.sub(r"[^a-z0-9]+", "_", pp_id.lower()).strip("_")

    saved_files = []

    if format in ("json", "both"):
        json_path = output_dir / f"carousel_{safe_title}_{timestamp}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(carousel, f, indent=2, ensure_ascii=False)
        saved_files.append(json_path)

    if format in ("markdown", "both"):
        md_path = output_dir / f"carousel_{safe_title}_{timestamp}.md"
        md_content = carousel_to_markdown(carousel)
        md_path.write_text(md_content, encoding="utf-8")
        saved_files.append(md_path)

    return saved_files


# ── CLI ──────────────────────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(
        description="M.O.T Innovation — LinkedIn Carousel Generator"
    )
    parser.add_argument("--pain-point", type=str, default=None,
                        help="Pain point ID")
    parser.add_argument("--service", type=str, default=None,
                        help="Service ID")
    parser.add_argument("--case-study", type=str, default=None,
                        help="Case study ID (optional)")
    parser.add_argument("--all", action="store_true",
                        help="Generate carousels for all pain points")
    parser.add_argument("--format", choices=["json", "markdown", "both"], default="both",
                        help="Output format (default: both)")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Output directory (default: carousels/)")
    args = parser.parse_args()

    print(f"\n{'=' * 60}")
    print(f"LINKEDIN CAROUSEL GENERATOR — {BRAND_NAME}")
    print(f"{'=' * 60}")

    output_dir = Path(args.output_dir) if args.output_dir else CAROUSEL_DIR

    if args.all:
        print(f"\n📁 Generating carousels for all {len(PAIN_POINTS)} pain points...\n")
        count = 0
        for pp in PAIN_POINTS:
            # Auto-match service
            matched = [s for s in SERVICES.values() if pp["id"] in s["keywords"]]
            svc = matched[0] if matched else SERVICES["dam"]

            carousel = generate_carousel(pp, svc)
            files = save_carousel(carousel, output_dir, args.format)
            print(f"   ✅ {pp['title']}")
            for f in files:
                print(f"      → {f}")
            count += 1

        print(f"\n✅ Generated {count} carousel(s) in {output_dir}")
        return 0

    if args.pain_point:
        pp = get_pain_point(args.pain_point)
    else:
        print("Error: provide --pain-point ID or use --all.")
        return 1

    if args.service:
        svc = get_service(args.service)
    else:
        matched = [s for s in SERVICES.values() if pp["id"] in s["keywords"]]
        svc = matched[0] if matched else SERVICES["dam"]

    cs = get_case_study(args.case_study) if args.case_study else None

    print(f"\n   Pain Point: {pp['title']}")
    print(f"   Service:   {svc['name']}")

    carousel = generate_carousel(pp, svc, cs)
    files = save_carousel(carousel, output_dir, args.format)

    print(f"\n✅ Carousel saved:")
    for f in files:
        print(f"   → {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())