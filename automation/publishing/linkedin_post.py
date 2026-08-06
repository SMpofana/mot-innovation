#!/usr/bin/env python
"""
linkedin_post.py — M.O.T Innovation LinkedIn Posting Script

Posts to LinkedIn via a Make.com webhook. Direct LinkedIn API posting requires
developer app approval and the UGC Posts API with specific scopes
(w_member_social, r_member_social), which takes weeks to get approved.

This module uses a Make.com webhook as a fallback:
    1. Create a Make.com scenario with a webhook trigger
    2. Make.com receives the payload and posts to LinkedIn via its connector
    3. This script sends the payload to the webhook URL

Functions:
    create_webhook_payload(text, image_url=None, link=None) → JSON payload
    send_to_webhook(webhook_url, payload) → POSTs to Make.com

NOTE: LinkedIn API requires developer app approval for direct posting.
      See: https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/posting/
      To use the direct API (once approved), you'll need:
          - A LinkedIn Developer app with the w_member_social scope
          - OAuth2 access token for the posting member
          - Use the UGC Posts API endpoint:
            POST https://api.linkedin.com/v2/ugcPosts
      The Make.com webhook approach works immediately without app review.

Usage:
    # Create a webhook payload
    python linkedin_post.py --create-payload --text "My post text" --link "https://..."

    # Send a post to Make.com webhook
    python linkedin_post.py --webhook-url https://hook.us1.make.com/xxx \\
        --text "My post text" --link "https://motinnovation.co.za"

    # Send from a generated LinkedIn post markdown file
    python linkedin_post.py --webhook-url https://hook.us1.make.com/xxx \\
        --from-file scripts/linkedin_post_disconnected_tools_20260804.md
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
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

# Optional: LinkedIn Make.com webhook URL (can be set in .env.local or passed as arg)
LINKEDIN_WEBHOOK_URL = os.getenv("LINKEDIN_MAKE_WEBHOOK_URL", "")


# ── Webhook payload creation ──────────────────────────────────────────────────

def create_webhook_payload(
    text: str,
    image_url: str | None = None,
    link: str | None = None,
) -> dict[str, Any]:
    """
    Create a JSON payload for the Make.com LinkedIn webhook.

    Args:
        text:      The post text content (LinkedIn post body)
        image_url: Optional URL of an image to attach to the post
        link:      Optional URL to include in the post (appears as a link card)

    Returns:
        JSON-serializable dict with the payload for Make.com.

    The Make.com scenario should be configured to:
        1. Receive this webhook
        2. Use the LinkedIn connector to create a post with the text
        3. Optionally attach the image or link
    """
    payload: dict[str, Any] = {
        "text": text,
        "timestamp": datetime.now().isoformat(),
        "source": "mot_innovation_content_engine",
    }

    if image_url:
        payload["image_url"] = image_url

    if link:
        payload["link"] = link

    # Extract hashtags from the text for LinkedIn's hashtag field
    hashtags = re.findall(r"#\w+", text)
    if hashtags:
        payload["hashtags"] = hashtags

    return payload


def send_to_webhook(webhook_url: str, payload: dict[str, Any]) -> dict[str, Any]:
    """
    POST the payload to a Make.com webhook URL.

    Args:
        webhook_url: The Make.com webhook URL
        payload:     The JSON payload (from create_webhook_payload)

    Returns:
        Dict with status, status_code, and response text.
    """
    if not webhook_url:
        return {"error": "No webhook URL provided"}

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        return {
            "status": "sent" if response.status_code in (200, 201, 202) else "failed",
            "status_code": response.status_code,
            "response": response.text,
            "webhook_url": webhook_url,
        }

    except requests.exceptions.Timeout:
        return {"error": "Request timed out (30s)", "status": "timeout"}
    except requests.exceptions.ConnectionError as e:
        return {"error": f"Connection error: {e}", "status": "connection_error"}
    except Exception as e:
        return {"error": str(e), "status": "error"}


# ── Parse generated LinkedIn post markdown ────────────────────────────────────

def parse_linkedin_post_file(md_path: Path) -> dict[str, str]:
    """
    Parse a generated LinkedIn post markdown file.

    Extracts the post content text from the '## Post Content' code block
    and the UTM link from the metadata.

    Returns a dict with 'text' and 'link' keys.
    """
    md_content = md_path.read_text(encoding="utf-8")

    # Extract post content from code block
    post_match = re.search(
        r"## Post Content\s*\n+\`\`\`\s*\n(.*?)\n\`\`\`",
        md_content, re.DOTALL,
    )
    text = post_match.group(1).strip() if post_match else md_content

    # Extract UTM link from metadata
    utm_match = re.search(r"\*\*UTM Link:\*\*\s*(.+)", md_content)
    link = utm_match.group(1).strip() if utm_match else ""

    return {"text": text, "link": link}


# ── Direct LinkedIn API (stub for future use) ─────────────────────────────────
# NOTE: LinkedIn API requires developer app approval for direct posting.
# See: https://learn.microsoft.com/en-us/linkedin/shared/api-guide/concepts/posting/
#
# Once you have app approval, implement the UGC Posts API:
#
# def post_to_linkedin_api(text, access_token, author_urn, image_urn=None):
#     """Post directly via LinkedIn UGC Posts API (requires app approval)."""
#     url = "https://api.linkedin.com/v2/ugcPosts"
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json",
#         "X-Restli-Protocol-Version": "2.0.0",
#     }
#     body = {
#         "author": author_urn,  # e.g. "urn:li:person:XXXX"
#         "lifecycleState": "PUBLISHED",
#         "specificContent": {
#             "com.linkedin.ugc.ShareContent": {
#                 "shareCommentary": {"text": text},
#                 "shareMediaCategory": "NONE",
#             }
#         },
#         "visibility": {
#             "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
#         }
#     }
#     if image_urn:
#         body["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
#         body["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
#             {"status": "READY", "media": image_urn}
#         ]
#     response = requests.post(url, json=body, headers=headers, timeout=30)
#     return response.json()


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="M.O.T Innovation — LinkedIn Posting via Make.com Webhook"
    )
    parser.add_argument(
        "--webhook-url", type=str, default=None,
        help="Make.com webhook URL (or set LINKEDIN_MAKE_WEBHOOK_URL in .env.local)",
    )
    parser.add_argument(
        "--text", type=str, default=None,
        help="LinkedIn post text content",
    )
    parser.add_argument(
        "--image-url", type=str, default=None,
        help="Optional image URL to attach to the post",
    )
    parser.add_argument(
        "--link", type=str, default=None,
        help="Optional link to include in the post",
    )
    parser.add_argument(
        "--from-file", type=str, default=None,
        help="Path to a generated LinkedIn post markdown file",
    )
    parser.add_argument(
        "--create-payload", action="store_true",
        help="Only create and print the webhook payload (don't send)",
    )
    parser.add_argument(
        "--save-payload", type=str, default=None,
        help="Save the webhook payload to this JSON file",
    )
    args = parser.parse_args()

    print(f"\n{'=' * 60}")
    print(f"M.O.T INNOVATION — LINKEDIN POSTING (Make.com Webhook)")
    print(f"{'=' * 60}")

    # Determine post text and link
    text = args.text
    link = args.link

    if args.from_file:
        path = Path(args.from_file)
        if not path.exists():
            print(f"❌ File not found: {path}")
            return 1

        print(f"📄 Parsing LinkedIn post: {path.name}")
        parsed = parse_linkedin_post_file(path)
        text = parsed["text"]
        if not link:
            link = parsed["link"]
        print(f"   ✅ Parsed ({len(text)} chars)")

    if not text:
        print("❌ No post text provided. Use --text or --from-file.")
        return 1

    # Create the webhook payload
    payload = create_webhook_payload(text, image_url=args.image_url, link=link)

    print(f"\n📋 Webhook Payload:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    # Save payload if requested
    if args.save_payload:
        save_path = Path(args.save_payload)
        save_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\n💾 Payload saved to: {save_path}")

    # If only creating payload, stop here
    if args.create_payload:
        print("\n✅ Payload created (not sent — --create-payload mode)")
        return 0

    # Determine webhook URL
    webhook_url = args.webhook_url or LINKEDIN_WEBHOOK_URL
    if not webhook_url:
        print(
            "\n❌ No webhook URL provided. Use --webhook-url or set "
            "LINKEDIN_MAKE_WEBHOOK_URL in .env.local"
        )
        print("   The payload has been created above — you can send it manually.")
        return 1

    # Send to Make.com webhook
    print(f"\n📤 Sending to Make.com webhook...")
    print(f"   URL: {webhook_url[:60]}...")

    result = send_to_webhook(webhook_url, payload)

    print(f"\n   Status: {result.get('status', 'unknown')}")
    print(f"   HTTP:   {result.get('status_code', 'N/A')}")

    if "error" in result:
        print(f"   ❌ Error: {result['error']}")
        return 1
    elif result.get("status") == "sent":
        print(f"   ✅ Post sent to Make.com! LinkedIn will post it shortly.")
        return 0
    else:
        print(f"   ⚠️  Unexpected response: {result.get('response', '')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())