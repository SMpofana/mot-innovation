#!/usr/bin/env python
"""
youtube_upload.py — M.O.T Innovation YouTube Upload Script

Uploads videos to YouTube via the Data API v3 with OAuth2 authentication.

First run: opens a browser for OAuth consent, saves token to
    automation/publishing/youtube_token.json
Subsequent runs: loads the saved token.

Functions:
    upload_video(video_path, title, description, tags, category_id=22,
                 privacy_status='public')
    set_thumbnail(video_id, thumbnail_path)

Quota: The YouTube Data API v3 has a default limit of 10,000 units/day.
Each upload costs ~1,600 units. This script handles quota errors gracefully.

Usage:
    # Upload a video
    python youtube_upload.py --video path/to/video.mp4 \\
        --title "Disconnected marketing tools — How We Fix It" \\
        --description "..." --tags marketing,automation --privacy public

    # Upload as a Short (adds #shorts hashtag, category 22)
    python youtube_upload.py --video path/to/short.mp4 --short \\
        --title "..." --description "..."

    # Set a custom thumbnail
    python youtube_upload.py --set-thumbnail VIDEO_ID --thumbnail path/to/thumb.jpg

    # Authenticate only (get OAuth token)
    python youtube_upload.py --auth-only
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# ── Configuration ───────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # mot_innovation/

# Load .env.local from the project root
ENV_PATH = PROJECT_ROOT / ".env.local"
load_dotenv(ENV_PATH)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")

# OAuth2 scopes for YouTube upload
SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube"]

# Token file path (saved after first OAuth flow)
TOKEN_FILE = SCRIPT_DIR / "youtube_token.json"

# OAuth client secrets file (generated from env vars)
CLIENT_SECRETS_FILE = SCRIPT_DIR / "client_secrets.json"

# API quota constants
DAILY_QUOTA_LIMIT = 10_000
UPLOAD_COST_UNITS = 1_600  # approx cost per upload
THUMBNAIL_COST_UNITS = 50  # approx cost per thumbnail set


# ── OAuth2 Authentication ──────────────────────────────────────────────────────

def _generate_client_secrets() -> dict[str, Any]:
    """
    Generate the client_secrets.json structure from environment variables.
    Required by google-auth-oauthlib.
    """
    return {
        "installed": {
            "client_id": YOUTUBE_CLIENT_ID,
            "client_secret": YOUTUBE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": ["http://localhost"],
        }
    }


def _write_client_secrets() -> Path:
    """Write the client secrets JSON file from env vars. Returns the path."""
    secrets = _generate_client_secrets()
    CLIENT_SECRETS_FILE.write_text(json.dumps(secrets, indent=2), encoding="utf-8")
    return CLIENT_SECRETS_FILE


def get_authenticated_service():
    """
    Authenticate with YouTube API using OAuth2.

    First run: opens browser for consent, saves token to youtube_token.json
    Subsequent runs: loads saved token

    Returns an authenticated YouTube API service object.
    """
    _check_credentials()

    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None

    # Try to load saved token
    if TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(None)
                _save_token(creds)
        except Exception as e:
            print(f"   ⚠️  Could not load saved token: {e}")
            creds = None

    # If no valid credentials, run OAuth flow
    if not creds or not creds.valid:
        print("   🔐 No valid credentials found — opening browser for OAuth consent...")
        _write_client_secrets()
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS_FILE), SCOPES)
        creds = flow.run_local_server(port=0)
        _save_token(creds)
        print(f"   ✅ Token saved to {TOKEN_FILE}")

    # Build the YouTube API service
    youtube = build("youtube", "v3", credentials=creds)
    return youtube


def _save_token(creds) -> None:
    """Save OAuth credentials to the token file."""
    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }
    TOKEN_FILE.write_text(json.dumps(token_data, indent=2), encoding="utf-8")


def _check_credentials() -> None:
    """Raise a clear error if YouTube credentials are missing."""
    missing = []
    if not YOUTUBE_CLIENT_ID:
        missing.append("YOUTUBE_CLIENT_ID")
    if not YOUTUBE_CLIENT_SECRET:
        missing.append("YOUTUBE_CLIENT_SECRET")
    if missing:
        raise ValueError(
            f"Missing YouTube credentials: {', '.join(missing)}. "
            f"Add them to {ENV_PATH}."
        )


# ── Upload functions ──────────────────────────────────────────────────────────

def upload_video(
    video_path: str | Path,
    title: str,
    description: str,
    tags: list[str] | str | None = None,
    category_id: int = 22,
    privacy_status: str = "public",
    is_short: bool = False,
) -> dict[str, Any]:
    """
    Upload a video to YouTube.

    Args:
        video_path:    Path to the video file (.mp4, .mov, etc.)
        title:         Video title (max 100 chars)
        description:   Video description (max 5000 chars)
        tags:          List of tag strings, or comma-separated string
        category_id:   YouTube category ID (22 = People & Blogs, default)
        privacy_status: 'public', 'unlisted', or 'private'
        is_short:      If True, adds #shorts to description and uses category 22

    Returns:
        Dict with video_id, status, and response data.
        On quota error, returns dict with 'error' key and 'quota_exceeded' True.
    """
    from googleapiclient.http import MediaFileUpload

    video_path = Path(video_path)
    if not video_path.exists():
        return {"error": f"Video file not found: {video_path}", "quota_exceeded": False}

    # Normalize tags
    if tags is None:
        tags = []
    elif isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    # For Shorts: add #shorts to description
    if is_short:
        if "#shorts" not in description.lower():
            description = f"{description}\n\n#shorts"
        category_id = 22  # People & Blogs

    # Truncate fields to YouTube limits
    title = title[:100]
    description = description[:5000]
    tags = tags[:500]  # max 500 tags

    print(f"   📤 Uploading: {video_path.name}")
    print(f"      Title: {title}")
    print(f"      Category: {category_id} | Privacy: {privacy_status} | Short: {is_short}")

    try:
        youtube = get_authenticated_service()

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": str(category_id),
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(
            str(video_path),
            mimetype="video/*",
            resumable=True,
        )

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        # Resumable upload with progress
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"      📊 Upload progress: {int(status.progress() * 100)}%")

        video_id = response.get("id", "")
        print(f"      ✅ Uploaded! Video ID: {video_id}")
        print(f"      🔗 https://www.youtube.com/watch?v={video_id}")

        return {
            "video_id": video_id,
            "video_url": f"https://www.youtube.com/watch?v={video_id}",
            "status": "uploaded",
            "title": title,
            "response": response,
        }

    except Exception as e:
        error_str = str(e).lower()
        # Check for quota exceeded
        if "quota" in error_str or "exceeded" in error_str or "403" in error_str:
            print(f"      ❌ QUOTA EXCEEDED: {e}")
            print(f"      💡 Daily limit is {DAILY_QUOTA_LIMIT:,} units. "
                  f"Each upload costs ~{UPLOAD_COST_UNITS} units.")
            return {
                "error": str(e),
                "quota_exceeded": True,
                "daily_limit": DAILY_QUOTA_LIMIT,
                "upload_cost": UPLOAD_COST_UNITS,
            }
        print(f"      ❌ Upload failed: {e}")
        return {"error": str(e), "quota_exceeded": False}


def set_thumbnail(video_id: str, thumbnail_path: str | Path) -> dict[str, Any]:
    """
    Set a custom thumbnail for a YouTube video.

    Requires the video to be owned by the authenticated channel.
    Custom thumbnails require channel verification.

    Args:
        video_id:       YouTube video ID
        thumbnail_path: Path to the thumbnail image (.jpg, .png, max 2MB)

    Returns:
        Dict with status and response data.
    """
    from googleapiclient.http import MediaFileUpload

    thumbnail_path = Path(thumbnail_path)
    if not thumbnail_path.exists():
        return {"error": f"Thumbnail file not found: {thumbnail_path}"}

    print(f"   🖼️  Setting thumbnail for video {video_id}: {thumbnail_path.name}")

    try:
        youtube = get_authenticated_service()

        media = MediaFileUpload(
            str(thumbnail_path),
            mimetype="image/jpeg",
        )

        response = youtube.thumbnails().set(
            videoId=video_id,
            media_body=media,
        ).execute()

        print(f"      ✅ Thumbnail set!")
        return {"status": "thumbnail_set", "video_id": video_id, "response": response}

    except Exception as e:
        error_str = str(e).lower()
        if "quota" in error_str or "exceeded" in error_str:
            print(f"      ❌ QUOTA EXCEEDED: {e}")
            return {
                "error": str(e),
                "quota_exceeded": True,
            }
        print(f"      ❌ Thumbnail set failed: {e}")
        return {"error": str(e), "quota_exceeded": False}


def check_quota_usage() -> dict[str, Any]:
    """
    Estimate remaining quota based on today's uploads.

    Note: YouTube API doesn't expose quota usage directly. This is an estimate
    based on the number of uploads performed today (tracked locally).
    """
    # We could track uploads in a local file, but for now just return the limits
    return {
        "daily_limit": DAILY_QUOTA_LIMIT,
        "upload_cost": UPLOAD_COST_UNITS,
        "max_uploads_per_day": DAILY_QUOTA_LIMIT // UPLOAD_COST_UNITS,
        "thumbnail_cost": THUMBNAIL_COST_UNITS,
        "note": "YouTube API does not expose quota usage. "
                f"Max ~{DAILY_QUOTA_LIMIT // UPLOAD_COST_UNITS} uploads/day.",
    }


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="M.O.T Innovation — YouTube Upload Script"
    )
    parser.add_argument(
        "--video", type=str, default=None,
        help="Path to the video file to upload",
    )
    parser.add_argument(
        "--title", type=str, default="Untitled Video",
        help="Video title (max 100 chars)",
    )
    parser.add_argument(
        "--description", type=str, default="",
        help="Video description (max 5000 chars)",
    )
    parser.add_argument(
        "--tags", type=str, default="",
        help="Comma-separated tags (e.g. marketing,automation)",
    )
    parser.add_argument(
        "--category-id", type=int, default=22,
        help="YouTube category ID (default: 22 = People & Blogs)",
    )
    parser.add_argument(
        "--privacy", type=str, default="public",
        choices=["public", "unlisted", "private"],
        help="Privacy status (default: public)",
    )
    parser.add_argument(
        "--short", action="store_true",
        help="Mark as YouTube Short (adds #shorts, category 22)",
    )
    parser.add_argument(
        "--set-thumbnail", type=str, default=None,
        help="Video ID to set a thumbnail for",
    )
    parser.add_argument(
        "--thumbnail", type=str, default=None,
        help="Path to the thumbnail image file",
    )
    parser.add_argument(
        "--auth-only", action="store_true",
        help="Only run the OAuth authentication flow and save the token",
    )
    parser.add_argument(
        "--quota-info", action="store_true",
        help="Show quota limit information",
    )
    args = parser.parse_args()

    print(f"\n{'=' * 60}")
    print(f"M.O.T INNOVATION — YOUTUBE UPLOAD")
    print(f"{'=' * 60}")

    if args.quota_info:
        info = check_quota_usage()
        print("── Quota Information ──")
        print(json.dumps(info, indent=2))
        return 0

    if args.auth_only:
        print("🔐 Running OAuth authentication flow...")
        try:
            youtube = get_authenticated_service()
            print(f"   ✅ Authentication successful! Token saved to {TOKEN_FILE}")
        except Exception as e:
            print(f"   ❌ Authentication failed: {e}")
            return 1
        return 0

    if args.set_thumbnail:
        if not args.thumbnail:
            print("❌ --set-thumbnail requires --thumbnail path")
            return 1
        result = set_thumbnail(args.set_thumbnail, args.thumbnail)
        if "error" in result:
            return 1
        return 0

    if args.video:
        result = upload_video(
            video_path=args.video,
            title=args.title,
            description=args.description,
            tags=args.tags,
            category_id=args.category_id,
            privacy_status=args.privacy,
            is_short=args.short,
        )
        if "error" in result:
            return 1
        return 0

    # No arguments — print help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())