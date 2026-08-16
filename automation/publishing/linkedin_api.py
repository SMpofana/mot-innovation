#!/usr/bin/env python
"""
linkedin_api.py — Direct LinkedIn posting via the UGC Posts API.

Replaces the Make.com webhook with direct LinkedIn API calls. Uses OAuth2
(authorization code flow) with the w_member_social scope.

Flow:
    1. --auth: open the authorization URL, user approves, LinkedIn redirects
       to the redirect URI with a ?code= param. Paste the code back.
    2. Exchange the code for an access token (saved to linkedin_token.json).
    3. --post: post text + optional image to the member's feed.

Requires a LinkedIn developer app with:
    - w_member_social scope (approved)
    - A redirect URI configured in the app (e.g. http://localhost:8080/callback)

Usage:
    python linkedin_api.py --auth
    python linkedin_api.py --post --text "Hello world" --image-url https://...
    python linkedin_api.py --post --from-file scripts/linkedin_post_*.md
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import webbrowser
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # mot_innovation/
ENV_PATH = PROJECT_ROOT / ".env.local"
load_dotenv(ENV_PATH)

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8080/callback")
TOKEN_FILE = SCRIPT_DIR / "linkedin_token.json"

AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
API_BASE = "https://api.linkedin.com/v2"
SCOPES = "w_member_social"


def _check_creds() -> None:
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError(
            "LINKEDIN_CLIENT_ID / LINKEDIN_CLIENT_SECRET not set. "
            f"Add them to {ENV_PATH}."
        )


def get_auth_url() -> str:
    """Return the LinkedIn OAuth authorization URL."""
    _check_creds()
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
    }
    return f"{AUTH_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"


def exchange_code(code: str) -> dict[str, Any]:
    """Exchange an authorization code for an access token."""
    _check_creds()
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    r = requests.post(TOKEN_URL, data=data, timeout=30)
    r.raise_for_status()
    token = r.json()
    TOKEN_FILE.write_text(json.dumps(token, indent=2), encoding="utf-8")
    return token


def _load_token() -> dict[str, Any]:
    if not TOKEN_FILE.exists():
        raise ValueError(
            f"No token at {TOKEN_FILE}. Run 'python linkedin_api.py --auth' first."
        )
    return json.loads(TOKEN_FILE.read_text(encoding="utf-8"))


def get_access_token() -> str:
    return _load_token()["access_token"]


def get_member_urn() -> str:
    """Get the authenticated member's URN (person)."""
    token = get_access_token()
    r = requests.get(
        f"{API_BASE}/userinfo",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    sub = data.get("sub", "")
    return f"urn:li:person:{sub}"


def post_text(text: str, image_url: str | None = None) -> dict[str, Any]:
    """Post text (and optional image) to the member's LinkedIn feed."""
    token = get_access_token()
    author = get_member_urn()

    if image_url:
        # Upload the image first, get a URN, then post with media.
        image_urn = _upload_image(token, image_url)
        body = {
            "author": author,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "IMAGE",
                    "media": [{"status": "READY", "media": image_urn}],
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }
    else:
        body = {
            "author": author,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }

    r = requests.post(
        f"{API_BASE}/ugcPosts",
        json=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
        timeout=30,
    )
    if r.status_code not in (200, 201):
        return {"error": r.text, "status_code": r.status_code}
    return {"status": "posted", "response": r.json(), "status_code": r.status_code}


def _upload_image(token: str, image_url: str) -> str:
    """Register an image upload, upload the bytes, return the image URN."""
    author = get_member_urn()
    # 1. Request an upload URL
    init = requests.post(
        f"{API_BASE}/images?action=initializeUpload",
        json={
            "initializeUploadRequest": {
                "owner": author,
            }
        },
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
        timeout=30,
    )
    init.raise_for_status()
    init_data = init.json()["value"]
    upload_url = init_data["uploadUrl"]
    image_urn = init_data["image"]

    # 2. Download the image bytes and upload them
    img_resp = requests.get(image_url, timeout=30)
    img_resp.raise_for_status()
    up = requests.put(upload_url, data=img_resp.content, timeout=60)
    up.raise_for_status()

    return image_urn


def main() -> int:
    parser = argparse.ArgumentParser(description="Direct LinkedIn posting via UGC API")
    parser.add_argument("--auth", action="store_true", help="Run OAuth flow")
    parser.add_argument("--code", type=str, default=None, help="OAuth code from redirect")
    parser.add_argument("--post", action="store_true", help="Post to LinkedIn")
    parser.add_argument("--text", type=str, default=None, help="Post text")
    parser.add_argument("--image-url", type=str, default=None, help="Image URL to attach")
    parser.add_argument("--from-file", type=str, default=None, help="LinkedIn post markdown file")
    args = parser.parse_args()

    print("=" * 60)
    print("M.O.T INNOVATION — DIRECT LINKEDIN POSTING (UGC API)")
    print("=" * 60)

    if args.auth:
        url = get_auth_url()
        print(f"\n🔗 Open this URL in your browser and authorize:\n\n{url}\n")
        webbrowser.open(url)
        print("\nAfter authorizing, LinkedIn redirects to your redirect URI with a")
        print("?code=... parameter. Copy that code and run:")
        print(f"  python linkedin_api.py --code <CODE>")
        return 0

    if args.code:
        token = exchange_code(args.code)
        print(f"\n✅ Token saved to {TOKEN_FILE}")
        print(f"   Access token: {token.get('access_token', '')[:20]}...")
        print(f"   Expires in: {token.get('expires_in')}s")
        return 0

    if args.post:
        text = args.text
        image_url = args.image_url
        if args.from_file:
            sys.path.insert(0, str(SCRIPT_DIR))
            from linkedin_post import parse_linkedin_post_file
            parsed = parse_linkedin_post_file(Path(args.from_file))
            text = parsed["text"]
            if not image_url:
                image_url = parsed.get("image_url", "")
        if not text:
            print("❌ No post text. Use --text or --from-file.")
            return 1
        result = post_text(text, image_url)
        print(f"\n📤 Posting to LinkedIn...")
        print(f"   Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        return 0 if result.get("status") == "posted" else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
