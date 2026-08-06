#!/usr/bin/env python
"""
Lead Nurturing Sequence — M.O.T Innovation

Manages the automated email sequence for captured leads:
    Day 0:  Welcome + consultation booking confirmation
    Day 1:  Case study (e-commerce 80% time reduction)
    Day 3:  Case study (SaaS 23% conversion improvement)
    Day 7:  Pricing breakdown + "ready to start?" CTA
    Day 14: Final follow-up

Emails are rendered from templates in email_templates/ and written to
../nurturing/ for each lead, ready to be sent via Resend/SendGrid later.

Usage:
    python lead_nurturing.py                             # Process all leads (send due emails)
    python lead_nurturing.py --lead-id lead_xxx          # Process a single lead
    python lead_nurturing.py --verbose                   # Show full email content
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
LEADS_DIR = BASE_DIR / "leads"
TEMPLATES_DIR = SCRIPT_DIR / "email_templates"
NURTURING_DIR = BASE_DIR / "nurturing"

LEADS_JSON = LEADS_DIR / "leads.json"
NURTURING_STATE_FILE = BASE_DIR / "nurturing" / "nurturing_state.json"

# Day offset → template file mapping
SEQUENCE = [
    {"day": 0,  "template": "day0_welcome.txt",                "subject": "Welcome to M.O.T Innovation"},
    {"day": 1,  "template": "day1_case_study_ecommerce.txt",    "subject": "Case Study: 80% time reduction"},
    {"day": 3,  "template": "day3_case_study_saas.txt",         "subject": "Case Study: 23% conversion improvement"},
    {"day": 7,  "template": "day7_pricing_breakdown.txt",       "subject": "Pricing breakdown + ready to start?"},
    {"day": 14, "template": "day14_final_followup.txt",        "subject": "Final follow-up"},
]

NURTURING_DIR.mkdir(parents=True, exist_ok=True)


def load_leads() -> list[dict]:
    if not LEADS_JSON.exists():
        return []
    with open(LEADS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def load_state() -> dict:
    if NURTURING_STATE_FILE.exists():
        with open(NURTURING_STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"leads": {}}


def save_state(state: dict) -> None:
    with open(NURTURING_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def render_template(template_text: str, lead: dict) -> str:
    """Replace {{first_name}} and other placeholders."""
    name = lead.get("name", "there")
    first_name = name.split()[0] if name else "there"
    replacements = {
        "{{first_name}}": first_name,
        "{{name}}": name,
        "{{email}}": lead.get("email", ""),
        "{{business}}": lead.get("business", ""),
        "{{stage}}": lead.get("stage", ""),
    }
    result = template_text
    for key, val in replacements.items():
        result = result.replace(key, val)
    return result


def get_due_emails(lead: dict, state_entry: dict) -> list[dict]:
    """Determine which emails are due for a lead based on capture time."""
    lead_timestamp = lead.get("timestamp", "")
    if not lead_timestamp:
        return []

    try:
        captured = datetime.fromisoformat(lead_timestamp)
    except (ValueError, TypeError):
        return []

    now = datetime.now()
    days_since_capture = (now - captured).days

    sent_days = state_entry.get("sent_emails", [])
    due = []
    for step in SEQUENCE:
        if step["day"] <= days_since_capture and step["day"] not in sent_days:
            due.append(step)
    return due


def write_email_for_lead(lead: dict, step: dict) -> Path:
    """Render an email from template and write it to the nurturing folder."""
    template_path = TEMPLATES_DIR / step["template"]
    if not template_path.exists():
        print(f"  ⚠️  Template not found: {template_path}")
        return template_path

    template_text = template_path.read_text(encoding="utf-8")
    rendered = render_template(template_text, lead)

    # Write to nurturing/{lead_id}/dayN_subject.txt
    lead_nurturing_dir = NURTURING_DIR / lead["id"]
    lead_nurturing_dir.mkdir(parents=True, exist_ok=True)
    safe_subject = step["subject"].replace(" ", "_").replace(":", "").replace("?", "")
    filename = f"day{step['day']}_{safe_subject}.txt"
    output_path = lead_nurturing_dir / filename
    output_path.write_text(rendered, encoding="utf-8")

    return output_path


def process_lead(lead: dict, state: dict) -> list[dict]:
    """Process a single lead — generate all due emails."""
    lead_id = lead["id"]
    if "leads" not in state:
        state["leads"] = {}
    state_entry = state["leads"].get(lead_id, {"sent_emails": []})

    due = get_due_emails(lead, state_entry)
    sent = []
    for step in due:
        output_path = write_email_for_lead(lead, step)
        sent.append({
            "day": step["day"],
            "subject": step["subject"],
            "file": str(output_path),
        })
        state_entry.setdefault("sent_emails", []).append(step["day"])
        print(f"  ✉️  Day {step['day']:>2} → {lead.get('name', lead_id)}: {step['subject']}")
        print(f"      Written: {output_path}")

    state["leads"][lead_id] = state_entry
    return sent


def print_sequence_overview() -> None:
    """Print the full nurturing sequence overview."""
    print("=" * 70)
    print("M.O.T INNOVATION — LEAD NURTURING SEQUENCE")
    print("=" * 70)
    print(f"\nEmail sequence (5 emails over 14 days):\n")
    print(f"{'Day':<5} {'Subject':<50} {'Template'}")
    print("-" * 100)
    for step in SEQUENCE:
        print(f"{step['day']:<5} {step['subject']:<50} {step['template']}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="M.O.T Innovation — Lead Nurturing Sequence"
    )
    parser.add_argument("--lead-id", type=str, help="Process only this lead ID")
    parser.add_argument("--verbose", action="store_true", help="Show full email content")
    args = parser.parse_args()

    print_sequence_overview()

    leads = load_leads()
    if not leads:
        print("⚠️  No leads found. Run lead_capture.py first.")
        return 1

    state = load_state()
    total_sent = 0

    for lead in leads:
        if args.lead_id and lead.get("id") != args.lead_id:
            continue
        sent = process_lead(lead, state)
        total_sent += len(sent)

        if args.verbose and sent:
            for s in sent:
                print(f"\n{'─' * 60}")
                print(f"Day {s['day']}: {s['subject']}")
                print(f"To: {lead.get('email', '')}")
                print(f"{'─' * 60}")
                with open(s["file"], "r", encoding="utf-8") as f:
                    print(f.read())

    save_state(state)
    print(f"\n✅ Processed {len(leads)} leads. {total_sent} emails generated.")
    print(f"📁 Nurturing emails: {NURTURING_DIR}")
    print(f"📁 State file: {NURTURING_STATE_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())