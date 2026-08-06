#!/usr/bin/env python
"""
sanity_cms.py — M.O.T Innovation Sanity CMS Integration

Creates and queries documents in Sanity CMS via their HTTP API.

Schema types created:
    - youtube_scripts   : YouTube Short scripts
    - linkedin_posts    : LinkedIn posts
    - carousels         : LinkedIn carousel content
    - content_calendar  : Calendar entries

Each document has: title, content, platform, pain_point, service,
                   status (draft/published), created_at, utm_link

Authentication: Bearer token (SANITY_API_TOKEN from .env.local)

Usage:
    # Create a YouTube script document from a markdown file
    python sanity_cms.py --create-script scripts/yt_short_disconnected_tools_20260804.md

    # Create a LinkedIn post document
    python sanity_cms.py --create-post scripts/linkedin_post_disconnected_tools_20260804.md

    # Create a carousel document from a carousel JSON file
    python sanity_cms.py --create-carousel carousels/carousel_disconnected_tools_20260804.json

    # Query all published YouTube scripts
    python sanity_cms.py --query "*[ _type == 'youtube_scripts' && status == 'published']"

    # Query by pain point
    python sanity_cms.py --query-pain-point disconnected_tools
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

# ── Configuration ───────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # mot_innovation/

# Load .env.local from the project root
ENV_PATH = PROJECT_ROOT / ".env.local"
load_dotenv(ENV_PATH)

SANITY_API_TOKEN = os.getenv("SANITY_API_TOKEN", "")
SANITY_PROJECT_ID = os.getenv("SANITY_PROJECT_ID", "mot_innovation")
SANITY_DATASET = os.getenv("SANITY_DATASET", "production")
SANITY_API_VERSION = os.getenv("SANITY_API_VERSION", "2024-01-01")

# API endpoints
MUTATE_URL = (
    f"https://{SANITY_PROJECT_ID}.api.sanity.io"
    f"/v{SANITY_API_VERSION}/data/mutate/{SANITY_DATASET}"
)
QUERY_URL = (
    f"https://{SANITY_PROJECT_ID}.api.sanity.io"
    f"/v{SANITY_API_VERSION}/data/query/{SANITY_DATASET}"
)


# ── Sanity schema definitions (for reference / documentation) ─────────────────
SANITY_SCHEMAS = {
    "youtube_scripts": {
        "type": "document",
        "name": "youtube_scripts",
        "title": "YouTube Scripts",
        "fields": [
            {"name": "title", "type": "string", "description": "Script title"},
            {"name": "content", "type": "text", "description": "Full script markdown"},
            {"name": "platform", "type": "string", "description": "YouTube"},
            {"name": "pain_point", "type": "string", "description": "Pain point ID/title"},
            {"name": "service", "type": "string", "description": "Service ID/name"},
            {"name": "status", "type": "string", "description": "draft or published"},
            {"name": "created_at", "type": "datetime", "description": "ISO timestamp"},
            {"name": "utm_link", "type": "string", "description": "UTM-tracked link"},
            {"name": "voiceover_text", "type": "text", "description": "TTS-ready voiceover text"},
            {"name": "tags", "type": "string", "description": "Comma-separated tags"},
            {"name": "hashtags", "type": "string", "description": "Hashtags"},
            {"name": "file_path", "type": "string", "description": "Local file path"},
        ],
    },
    "linkedin_posts": {
        "type": "document",
        "name": "linkedin_posts",
        "title": "LinkedIn Posts",
        "fields": [
            {"name": "title", "type": "string", "description": "Post title"},
            {"name": "content", "type": "text", "description": "Full post markdown"},
            {"name": "platform", "type": "string", "description": "LinkedIn"},
            {"name": "pain_point", "type": "string", "description": "Pain point ID/title"},
            {"name": "service", "type": "string", "description": "Service ID/name"},
            {"name": "status", "type": "string", "description": "draft or published"},
            {"name": "created_at", "type": "datetime", "description": "ISO timestamp"},
            {"name": "utm_link", "type": "string", "description": "UTM-tracked link"},
            {"name": "hashtags", "type": "string", "description": "Hashtags"},
            {"name": "file_path", "type": "string", "description": "Local file path"},
        ],
    },
    "carousels": {
        "type": "document",
        "name": "carousels",
        "title": "LinkedIn Carousels",
        "fields": [
            {"name": "title", "type": "string", "description": "Carousel title"},
            {"name": "content", "type": "text", "description": "Full carousel JSON/markdown"},
            {"name": "platform", "type": "string", "description": "LinkedIn"},
            {"name": "pain_point", "type": "string", "description": "Pain point ID/title"},
            {"name": "service", "type": "string", "description": "Service ID/name"},
            {"name": "status", "type": "string", "description": "draft or published"},
            {"name": "created_at", "type": "datetime", "description": "ISO timestamp"},
            {"name": "utm_link", "type": "string", "description": "UTM-tracked link"},
            {"name": "slides", "type": "array", "description": "Slide data"},
            {"name": "file_path", "type": "string", "description": "Local file path"},
        ],
    },
    "content_calendar": {
        "type": "document",
        "name": "content_calendar",
        "title": "Content Calendar Entries",
        "fields": [
            {"name": "title", "type": "string", "description": "Entry title"},
            {"name": "content", "type": "text", "description": "Entry content/description"},
            {"name": "platform", "type": "string", "description": "Platform name"},
            {"name": "pain_point", "type": "string", "description": "Pain point"},
            {"name": "service", "type": "string", "description": "Service"},
            {"name": "status", "type": "string", "description": "draft, published, rest"},
            {"name": "created_at", "type": "datetime", "description": "ISO timestamp"},
            {"name": "utm_link", "type": "string", "description": "UTM link"},
            {"name": "date", "type": "date", "description": "Scheduled date"},
            {"name": "day", "type": "string", "description": "Day of week"},
            {"name": "content_type", "type": "string", "description": "Type of content"},
            {"name": "script_file_path", "type": "string", "description": "Path to script file"},
        ],
    },
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _headers() -> dict[str, str]:
    """Return HTTP headers with Bearer auth."""
    return {
        "Authorization": f"Bearer {SANITY_API_TOKEN}",
        "Content-Type": "application/json",
    }


def _check_token() -> None:
    """Raise a clear error if the API token is missing."""
    if not SANITY_API_TOKEN:
        raise ValueError(
            "SANITY_API_TOKEN not found. "
            f"Add it to {ENV_PATH} or set it as an environment variable."
        )


def _gen_doc_id(prefix: str) -> str:
    """Generate a unique Sanity document ID."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _parse_youtube_script(md_content: str, file_path: str) -> dict[str, Any]:
    """
    Parse a YouTube Short script markdown file into a Sanity document.

    Extracts metadata fields from the markdown header and metadata section.
    """
    lines = md_content

    # Extract title from the first line (# YouTube Short Script — ...)
    title_match = re.search(r"^# .*$", lines, re.MULTILINE)
    title = title_match.group(0).replace("# YouTube Short Script —", "").strip() if title_match else "Untitled Script"

    # Extract pain point
    pp_match = re.search(r"\*\*Pain Point:\*\*\s*(.+)", lines)
    pain_point = pp_match.group(1).strip() if pp_match else ""

    # Extract service
    svc_match = re.search(r"\*\*Service:\*\*\s*(.+)", lines)
    service = svc_match.group(1).strip() if svc_match else ""

    # Extract description from metadata
    desc_match = re.search(r"\*\*Description:\*\*\s*(.+)", lines)
    description = desc_match.group(1).strip() if desc_match else ""

    # Extract tags
    tags_match = re.search(r"\*\*Tags:\*\*\s*(.+)", lines)
    tags = tags_match.group(1).strip() if tags_match else ""

    # Extract hashtags
    hashtags_match = re.search(r"\*\*Hashtags:\*\*\s*(.+)", lines)
    hashtags = hashtags_match.group(1).strip() if hashtags_match else ""

    # Extract UTM link
    utm_match = re.search(r"\*\*UTM Link:\*\*\s*(.+)", lines)
    utm_link = utm_match.group(1).strip() if utm_match else ""

    # Extract full voiceover text
    vo_match = re.search(
        r"## Full Voiceover Text \(for TTS\)\s*\n+(.*?)(?:\n---|\Z)",
        lines, re.DOTALL,
    )
    voiceover_text = ""
    if vo_match:
        voiceover_text = re.sub(r"\[VISUAL:.*?\]", "", vo_match.group(1))
        voiceover_text = re.sub(r"\*\*(.+?)\*\*", r"\1", voiceover_text)
        voiceover_text = voiceover_text.strip()

    return {
        "title": title,
        "content": lines,
        "platform": "YouTube",
        "pain_point": pain_point,
        "service": service,
        "status": "draft",
        "created_at": datetime.now().isoformat() + "Z",
        "utm_link": utm_link,
        "voiceover_text": voiceover_text,
        "tags": tags,
        "hashtags": hashtags,
        "file_path": file_path,
    }


def _parse_linkedin_post(md_content: str, file_path: str) -> dict[str, Any]:
    """
    Parse a LinkedIn post markdown file into a Sanity document.

    Extracts post content from the '## Post Content' code block.
    """
    lines = md_content

    # Extract title from first line
    title_match = re.search(r"^# .*$", lines, re.MULTILINE)
    title = title_match.group(0).replace("# LinkedIn Post —", "").strip() if title_match else "Untitled Post"

    # Extract pain point
    pp_match = re.search(r"\*\*Pain Point:\*\*\s*(.+)", lines)
    pain_point = pp_match.group(1).strip() if pp_match else ""

    # Extract service
    svc_match = re.search(r"\*\*Service:\*\*\s*(.+)", lines)
    service = svc_match.group(1).strip() if svc_match else ""

    # Extract post content from code block
    post_match = re.search(r"## Post Content\s*\n+\`\`\`\s*\n(.*?)\n\`\`\`", lines, re.DOTALL)
    post_content = post_match.group(1).strip() if post_match else ""

    # Extract UTM link from metadata
    utm_match = re.search(r"\*\*UTM Link:\*\*\s*(.+)", lines)
    utm_link = utm_match.group(1).strip() if utm_match else ""

    # Extract hashtags from metadata
    hashtags_match = re.search(r"\*\*Hashtags:\*\*\s*(.+)", lines)
    hashtags = hashtags_match.group(1).strip() if hashtags_match else ""

    return {
        "title": title,
        "content": post_content,
        "platform": "LinkedIn",
        "pain_point": pain_point,
        "service": service,
        "status": "draft",
        "created_at": datetime.now().isoformat() + "Z",
        "utm_link": utm_link,
        "hashtags": hashtags,
        "file_path": file_path,
    }


def _parse_carousel_json(json_content: dict, file_path: str) -> dict[str, Any]:
    """
    Parse a carousel JSON file into a Sanity document.
    """
    metadata = json_content.get("metadata", {})

    return {
        "title": metadata.get("title", "Untitled Carousel"),
        "content": json.dumps(json_content, indent=2, ensure_ascii=False),
        "platform": "LinkedIn",
        "pain_point": metadata.get("pain_point", ""),
        "service": metadata.get("service_name", ""),
        "status": "draft",
        "created_at": datetime.now().isoformat() + "Z",
        "utm_link": metadata.get("utm_link", ""),
        "slides": json_content.get("slides", []),
        "file_path": file_path,
    }


# ── Core API functions ─────────────────────────────────────────────────────────

def _mutate_create(document: dict) -> dict[str, Any]:
    """
    Send a create mutation to Sanity.
    Returns the API response JSON.
    """
    _check_token()

    payload = {
        "mutations": [
            {"create": document}
        ]
    }

    response = requests.post(
        MUTATE_URL,
        headers=_headers(),
        json=payload,
        params={"returnIds": "true"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def create_script_doc(
    title: str,
    content: str,
    pain_point: str = "",
    service: str = "",
    utm_link: str = "",
    voiceover_text: str = "",
    tags: str = "",
    hashtags: str = "",
    file_path: str = "",
    status: str = "draft",
) -> dict[str, Any]:
    """
    Create a YouTube script document in Sanity.

    Returns the Sanity API response containing the document ID.
    """
    doc_id = _gen_doc_id("yt_script")

    document = {
        "_id": doc_id,
        "_type": "youtube_scripts",
        "title": title,
        "content": content,
        "platform": "YouTube",
        "pain_point": pain_point,
        "service": service,
        "status": status,
        "created_at": datetime.now().isoformat() + "Z",
        "utm_link": utm_link,
        "voiceover_text": voiceover_text,
        "tags": tags,
        "hashtags": hashtags,
        "file_path": file_path,
    }

    return _mutate_create(document)


def create_post_doc(
    title: str,
    content: str,
    pain_point: str = "",
    service: str = "",
    utm_link: str = "",
    hashtags: str = "",
    file_path: str = "",
    status: str = "draft",
) -> dict[str, Any]:
    """
    Create a LinkedIn post document in Sanity.

    Returns the Sanity API response containing the document ID.
    """
    doc_id = _gen_doc_id("li_post")

    document = {
        "_id": doc_id,
        "_type": "linkedin_posts",
        "title": title,
        "content": content,
        "platform": "LinkedIn",
        "pain_point": pain_point,
        "service": service,
        "status": status,
        "created_at": datetime.now().isoformat() + "Z",
        "utm_link": utm_link,
        "hashtags": hashtags,
        "file_path": file_path,
    }

    return _mutate_create(document)


def create_carousel_doc(
    title: str,
    content: str,
    pain_point: str = "",
    service: str = "",
    utm_link: str = "",
    slides: list | None = None,
    file_path: str = "",
    status: str = "draft",
) -> dict[str, Any]:
    """
    Create a LinkedIn carousel document in Sanity.

    Returns the Sanity API response containing the document ID.
    """
    doc_id = _gen_doc_id("carousel")

    document = {
        "_id": doc_id,
        "_type": "carousels",
        "title": title,
        "content": content,
        "platform": "LinkedIn",
        "pain_point": pain_point,
        "service": service,
        "status": status,
        "created_at": datetime.now().isoformat() + "Z",
        "utm_link": utm_link,
        "slides": slides or [],
        "file_path": file_path,
    }

    return _mutate_create(document)


def create_calendar_doc(
    title: str,
    content: str,
    platform: str = "",
    pain_point: str = "",
    service: str = "",
    status: str = "draft",
    utm_link: str = "",
    date: str = "",
    day: str = "",
    content_type: str = "",
    script_file_path: str = "",
) -> dict[str, Any]:
    """
    Create a content calendar entry document in Sanity.

    Returns the Sanity API response containing the document ID.
    """
    doc_id = _gen_doc_id("cal")

    document = {
        "_id": doc_id,
        "_type": "content_calendar",
        "title": title,
        "content": content,
        "platform": platform,
        "pain_point": pain_point,
        "service": service,
        "status": status,
        "created_at": datetime.now().isoformat() + "Z",
        "utm_link": utm_link,
        "date": date,
        "day": day,
        "content_type": content_type,
        "script_file_path": script_file_path,
    }

    return _mutate_create(document)


def query_content(groq_query: str) -> dict[str, Any]:
    """
    Query Sanity content using GROQ (GraphQL-Object Query language).

    Example queries:
        "*[ _type == 'youtube_scripts' && status == 'published']"
        "*[ _type == 'linkedin_posts' && pain_point == 'Disconnected marketing tools']"
        "*[ _type == 'carousels']{title, pain_point, service}"

    Returns the Sanity query response JSON.
    """
    _check_token()

    response = requests.get(
        QUERY_URL,
        headers=_headers(),
        params={"query": groq_query},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


# ── Convenience functions for file-based creation ──────────────────────────────

def create_script_from_file(md_path: Path) -> dict[str, Any]:
    """Read a YouTube Short script markdown file and create a Sanity document."""
    md_content = md_path.read_text(encoding="utf-8")
    parsed = _parse_youtube_script(md_content, str(md_path))

    return create_script_doc(
        title=parsed["title"],
        content=parsed["content"],
        pain_point=parsed["pain_point"],
        service=parsed["service"],
        utm_link=parsed["utm_link"],
        voiceover_text=parsed["voiceover_text"],
        tags=parsed["tags"],
        hashtags=parsed["hashtags"],
        file_path=parsed["file_path"],
        status="draft",
    )


def create_post_from_file(md_path: Path) -> dict[str, Any]:
    """Read a LinkedIn post markdown file and create a Sanity document."""
    md_content = md_path.read_text(encoding="utf-8")
    parsed = _parse_linkedin_post(md_content, str(md_path))

    return create_post_doc(
        title=parsed["title"],
        content=parsed["content"],
        pain_point=parsed["pain_point"],
        service=parsed["service"],
        utm_link=parsed["utm_link"],
        hashtags=parsed["hashtags"],
        file_path=parsed["file_path"],
        status="draft",
    )


def create_carousel_from_file(json_path: Path) -> dict[str, Any]:
    """Read a carousel JSON file and create a Sanity document."""
    json_content = json.loads(json_path.read_text(encoding="utf-8"))
    parsed = _parse_carousel_json(json_content, str(json_path))

    return create_carousel_doc(
        title=parsed["title"],
        content=parsed["content"],
        pain_point=parsed["pain_point"],
        service=parsed["service"],
        utm_link=parsed["utm_link"],
        slides=parsed["slides"],
        file_path=parsed["file_path"],
        status="draft",
    )


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="M.O.T Innovation — Sanity CMS Integration"
    )
    parser.add_argument(
        "--create-script", type=str, default=None,
        help="Path to a YouTube Short script markdown file to upload to Sanity",
    )
    parser.add_argument(
        "--create-post", type=str, default=None,
        help="Path to a LinkedIn post markdown file to upload to Sanity",
    )
    parser.add_argument(
        "--create-carousel", type=str, default=None,
        help="Path to a carousel JSON file to upload to Sanity",
    )
    parser.add_argument(
        "--query", type=str, default=None,
        help="Run a GROQ query against Sanity (e.g. \"*[ _type == 'youtube_scripts']\")",
    )
    parser.add_argument(
        "--query-pain-point", type=str, default=None,
        help="Query all content for a specific pain point title",
    )
    parser.add_argument(
        "--list-schemas", action="store_true",
        help="Print the Sanity schema definitions",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Parse files and show the document that would be created, but don't POST",
    )
    args = parser.parse_args()

    print(f"\n{'=' * 60}")
    print(f"M.O.T INNOVATION — SANITY CMS INTEGRATION")
    print(f"{'=' * 60}")
    print(f"Project:  {SANITY_PROJECT_ID}")
    print(f"Dataset:  {SANITY_DATASET}")
    print(f"API ver:  {SANITY_API_VERSION}")
    print(f"Token:    {'✅ Found' if SANITY_API_TOKEN else '❌ Missing'}")
    print(f"Env file:  {ENV_PATH}")
    print()

    if args.list_schemas:
        print("── Sanity Schema Definitions ──\n")
        print(json.dumps(SANITY_SCHEMAS, indent=2))
        return 0

    if args.dry_run:
        _check_token()
        print("🔍 Dry run mode — showing parsed documents without POSTing\n")

        if args.create_script:
            path = Path(args.create_script)
            if not path.exists():
                print(f"❌ File not found: {path}")
                return 1
            parsed = _parse_youtube_script(path.read_text(encoding="utf-8"), str(path))
            print(f"YouTube Script Document:")
            print(json.dumps(parsed, indent=2))

        if args.create_post:
            path = Path(args.create_post)
            if not path.exists():
                print(f"❌ File not found: {path}")
                return 1
            parsed = _parse_linkedin_post(path.read_text(encoding="utf-8"), str(path))
            print(f"\nLinkedIn Post Document:")
            print(json.dumps(parsed, indent=2))

        if args.create_carousel:
            path = Path(args.create_carousel)
            if not path.exists():
                print(f"❌ File not found: {path}")
                return 1
            json_content = json.loads(path.read_text(encoding="utf-8"))
            parsed = _parse_carousel_json(json_content, str(path))
            print(f"\nCarousel Document:")
            print(json.dumps(parsed, indent=2, ensure_ascii=False))

        return 0

    # Create operations
    if args.create_script:
        path = Path(args.create_script)
        if not path.is_absolute():
            path = SCRIPT_DIR / path
        if not path.exists():
            print(f"❌ File not found: {path}")
            return 1

        print(f"📝 Creating YouTube script document from: {path.name}")
        try:
            response = create_script_from_file(path)
            print(f"   ✅ Created! Response: {json.dumps(response, indent=2)}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return 1

    if args.create_post:
        path = Path(args.create_post)
        if not path.is_absolute():
            path = SCRIPT_DIR / path
        if not path.exists():
            print(f"❌ File not found: {path}")
            return 1

        print(f"📝 Creating LinkedIn post document from: {path.name}")
        try:
            response = create_post_from_file(path)
            print(f"   ✅ Created! Response: {json.dumps(response, indent=2)}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return 1

    if args.create_carousel:
        path = Path(args.create_carousel)
        if not path.is_absolute():
            path = SCRIPT_DIR / path
        if not path.exists():
            print(f"❌ File not found: {path}")
            return 1

        print(f"📝 Creating carousel document from: {path.name}")
        try:
            response = create_carousel_from_file(path)
            print(f"   ✅ Created! Response: {json.dumps(response, indent=2)}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return 1

    # Query operations
    if args.query:
        print(f"🔍 Running GROQ query: {args.query}")
        try:
            response = query_content(args.query)
            print(f"   ✅ Results: {json.dumps(response, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return 1

    if args.query_pain_point:
        pp = args.query_pain_point
        # Try to match pain point title
        groq = (
            f'*[_type in ["youtube_scripts", "linkedin_posts", "carousels"] '
            f'&& pain_point match "*{pp}*"]{{_id, _type, title, pain_point, status}}'
        )
        print(f"🔍 Querying content for pain point: {pp}")
        try:
            response = query_content(groq)
            print(f"   ✅ Results: {json.dumps(response, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return 1

    if not any([
        args.create_script, args.create_post, args.create_carousel,
        args.query, args.query_pain_point, args.list_schemas, args.dry_run,
    ]):
        parser.print_help()
        return 0

    print(f"\n{'=' * 60}")
    print("✅ Sanity CMS operation complete!")
    print(f"{'=' * 60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())