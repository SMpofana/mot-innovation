#!/usr/bin/env python
"""
Lead Capture Automation — M.O.T Innovation

When someone submits the contact form (POST to /api/lead), this script:
1. Logs the lead to CSV + JSON in ../leads/
2. Sends a notification (console log + writes to ../notifications/notifications.json)
3. Triggers the lead scoring script

Usage:
    python lead_capture.py                          # Run interactive demo (sample lead)
    python lead_capture.py --lead '{"name":"Jane","email":"jane@corp.co.za","business":"Corp Ltd","stage":"Enterprise","message":"Need DAM setup"}'
    python lead_capture.py --file leads_batch.json   # Batch import from JSON file

Can also be used as a module:
    from lead_capture import capture_lead
    capture_lead({"name": "Jane", "email": "jane@corp.co.za", ...})
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent  # mot_innovation/
LEADS_DIR = BASE_DIR / "leads"
NOTIFICATIONS_DIR = BASE_DIR / "notifications"
LEADS_CSV = LEADS_DIR / "leads.csv"
LEADS_JSON = LEADS_DIR / "leads.json"
NOTIFICATIONS_FILE = NOTIFICATIONS_DIR / "notifications.json"

# Ensure directories exist
for d in [LEADS_DIR, NOTIFICATIONS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Lead schema ──────────────────────────────────────────────────────────────
CSV_FIELDS = [
    "id", "name", "email", "business", "stage", "message",
    "source", "timestamp", "user_agent", "referrer", "score", "priority"
]

STAGE_RANKING = {
    "enterprise": 4,
    "established": 3,
    "have some systems": 2,
    "just starting": 1,
}
# Acceptable stage variants from the website contact form
STAGE_ALIASES = {
    "enterprise": "Enterprise",
    "established": "Established",
    "have some systems": "Have some systems",
    "just starting": "Just starting",
    "have systems": "Have some systems",
    "some systems": "Have some systems",
    "starting": "Just starting",
    "small": "Just starting",
    "large": "Enterprise",
    "medium": "Established",
}


# ── Core functions ──────────────────────────────────────────────────────────
def normalize_stage(stage: str) -> str:
    """Map any stage input to a canonical stage name."""
    if not stage:
        return "Just starting"
    key = stage.strip().lower()
    if key in STAGE_ALIASES:
        return STAGE_ALIASES[key]
    for alias, canonical in STAGE_ALIASES.items():
        if alias in key:
            return canonical
    return "Just starting"


def score_lead(lead: dict) -> tuple[int, str]:
    """Score a lead and return (score, priority).

    Scoring criteria:
      - Stage: Enterprise (40) > Established (30) > Have some systems (20) > Just starting (10)
      - Has business name: +10
      - Has a message with detail (50+ chars): +10
      - Email is a business domain (not gmail/yahoo/hotmail): +10
      - Source is organic search or direct: +5
    """
    score = 0
    stage = normalize_stage(lead.get("stage", ""))
    score += STAGE_RANKING.get(stage.lower(), 1) * 10

    if lead.get("business") and len(lead["business"].strip()) > 1:
        score += 10

    message = lead.get("message", "") or ""
    if len(message) >= 50:
        score += 10

    email = (lead.get("email") or "").lower()
    personal_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com"]
    if email and not any(d in email for d in personal_domains):
        score += 10

    source = (lead.get("source") or "").lower()
    if "organic" in source or "direct" in source or source == "website-contact-form":
        score += 5

    if score >= 60:
        priority = "HOT"
    elif score >= 40:
        priority = "WARM"
    else:
        priority = "COLD"

    return score, priority


def generate_lead_id() -> str:
    return f"lead_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(2).hex()}"


def append_to_csv(lead: dict) -> None:
    """Append a lead to the CSV file, creating headers if needed."""
    file_exists = LEADS_CSV.exists()
    with open(LEADS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerow(lead)


def append_to_json(lead: dict) -> None:
    """Append a lead to the JSON leads file (array of lead objects)."""
    leads = []
    if LEADS_JSON.exists():
        try:
            with open(LEADS_JSON, "r", encoding="utf-8") as f:
                leads = json.load(f)
        except (json.JSONDecodeError, ValueError):
            leads = []
    leads.append(lead)
    with open(LEADS_JSON, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)


def send_notification(lead: dict) -> dict:
    """Write a notification entry and log to console."""
    notification = {
        "id": lead["id"],
        "type": "new_lead",
        "message": f"🎯 New lead from {lead['name']} ({lead.get('business', 'N/A')}) — Stage: {lead['stage']}, Score: {lead['score']}, Priority: {lead['priority']}",
        "lead_email": lead["email"],
        "lead_score": lead["score"],
        "lead_priority": lead["priority"],
        "timestamp": lead["timestamp"],
    }

    # Console log
    print("=" * 60)
    print(f"🔔 NOTIFICATION: {notification['message']}")
    print("=" * 60)

    # Write to notifications file
    notifications = []
    if NOTIFICATIONS_FILE.exists():
        try:
            with open(NOTIFICATIONS_FILE, "r", encoding="utf-8") as f:
                notifications = json.load(f)
        except (json.JSONDecodeError, ValueError):
            notifications = []
    notifications.append(notification)
    with open(NOTIFICATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(notifications, f, indent=2, ensure_ascii=False)

    return notification


def capture_lead(raw_lead: dict) -> dict:
    """Full lead capture pipeline: validate, score, log, notify.

    Args:
        raw_lead: Dict with keys: name, email, business, stage, message, source,
                  user_agent, referrer

    Returns:
        The enriched lead dict (with id, score, priority, timestamp)
    """
    # Validate required fields
    if not raw_lead.get("name") or not raw_lead.get("email"):
        raise ValueError("Lead capture requires at least 'name' and 'email'")

    # Enrich the lead
    lead = {
        "id": generate_lead_id(),
        "name": raw_lead["name"],
        "email": raw_lead["email"],
        "business": raw_lead.get("business", ""),
        "stage": normalize_stage(raw_lead.get("stage", "")),
        "message": raw_lead.get("message", ""),
        "source": raw_lead.get("source", "website-contact-form"),
        "timestamp": datetime.now().isoformat(),
        "user_agent": raw_lead.get("user_agent", ""),
        "referrer": raw_lead.get("referrer", ""),
    }

    # Score
    lead["score"], lead["priority"] = score_lead(lead)

    # Log to CSV + JSON
    append_to_csv(lead)
    append_to_json(lead)

    # Notify
    send_notification(lead)

    print(f"\n✅ Lead captured: {lead['name']} | Score: {lead['score']} | Priority: {lead['priority']}")
    print(f"   CSV:  {LEADS_CSV}")
    print(f"   JSON: {LEADS_JSON}")
    print(f"   Notif: {NOTIFICATIONS_FILE}")

    return lead


def capture_batch(leads: list[dict]) -> list[dict]:
    """Capture multiple leads at once."""
    results = []
    for raw in leads:
        try:
            results.append(capture_lead(raw))
        except (ValueError, KeyError) as e:
            print(f"⚠️  Skipping invalid lead: {e}")
    return results


# ── CLI ──────────────────────────────────────────────────────────────────────
def _demo_lead() -> dict:
    """Return a sample lead for demo/testing."""
    return {
        "name": "Test Lead",
        "email": "test@business.co.za",
        "business": "Test Business Ltd",
        "stage": "Established",
        "message": "We need help setting up our marketing infrastructure — currently using spreadsheets for everything.",
        "source": "demo-run",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="M.O.T Innovation — Lead Capture Automation"
    )
    parser.add_argument(
        "--lead", type=str,
        help="JSON string with lead data (name, email, business, stage, message, source)"
    )
    parser.add_argument(
        "--file", type=str,
        help="Path to a JSON file containing an array of lead objects for batch import"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("M.O.T INNOVATION — LEAD CAPTURE AUTOMATION")
    print("=" * 60)

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return 1
        with open(file_path, "r", encoding="utf-8") as f:
            leads = json.load(f)
        if not isinstance(leads, list):
            leads = [leads]
        print(f"\n📥 Batch import: {len(leads)} leads\n")
        captured = capture_batch(leads)
        print(f"\n✅ Captured {len(captured)}/{len(leads)} leads")
        return 0

    if args.lead:
        try:
            raw = json.loads(args.lead)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return 1
        capture_lead(raw)
        return 0

    # Demo mode
    print("\n🧪 Running in demo mode (sample lead)...\n")
    capture_lead(_demo_lead())
    return 0


if __name__ == "__main__":
    sys.exit(main())