#!/usr/bin/env python
"""
Client Onboarding Automation — M.O.T Innovation

When a client signs up, this script:
1. Auto-generates a project folder structure
2. Creates a checklist file with onboarding steps
3. Generates a welcome packet (markdown template)
4. Creates a project config file

Usage:
    python client_onboarding.py                                            # Demo: onboards a sample client
    python client_onboarding.py --client-name "Acme Corp" --service-tier "Intelligence Build"
    python client_onboarding.py --client-name "Acme Corp" --service-tier "Infrastructure Audit" --client-email "ceo@acme.com"
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
ONBOARDING_DIR = BASE_DIR / "onboarding"

# Service tiers
TIERS = {
    "Infrastructure Audit": {
        "price": "$500",
        "weeks": 1,
        "description": "Deep audit of your entire marketing stack",
    },
    "Intelligence Build": {
        "price": "$2,500–$5,000",
        "weeks": 4,
        "description": "Full build: DAM, delivery, dashboards, optimization",
    },
    "Intelligence Partner": {
        "price": "$1,000+/month",
        "weeks": 0,  # Ongoing
        "description": "Continuous monitoring, optimization, and reporting",
    },
}

ONBOARDING_STEPS = [
    {"step": 1, "title": "Welcome Call (30 min)",
     "description": "Understand business, goals, current marketing stack, and pain points",
     "deliverable": "Onboarding brief", "days": 1},
    {"step": 2, "title": "Infrastructure Audit",
     "description": "Full audit of digital assets, channels, tracking, and campaigns",
     "deliverable": "Infrastructure map + gap analysis report", "days": 3},
    {"step": 3, "title": "Architecture Design",
     "description": "Design the marketing intelligence system tailored to their needs",
     "deliverable": "Architecture blueprint document", "days": 5},
    {"step": 4, "title": "Build & Integrate",
     "description": "Build DAM, delivery pipelines, dashboards, and optimization rules",
     "deliverable": "Working marketing intelligence infrastructure", "days": 10},
    {"step": 5, "title": "Team Training & Handover",
     "description": "Train the team on the new system and hand over all documentation",
     "deliverable": "Training session + documentation pack", "days": 12},
    {"step": 6, "title": "30-Day Support",
     "description": "Monitor, tune, and optimize the system for the first 30 days",
     "deliverable": "30-day performance report", "days": 30},
]

QUESTIONNAIRE = [
    {"question": "What's your business name and website?", "type": "text"},
    {"question": "How many people are on your marketing team?", "type": "number"},
    {"question": "Which social media platforms do you currently use?", "type": "multi-select",
     "options": ["LinkedIn", "Instagram", "TikTok", "X (Twitter)", "Facebook", "YouTube"]},
    {"question": "Where do you currently store digital assets?", "type": "text"},
    {"question": "What tools do you use for reporting/analytics?", "type": "text"},
    {"question": "What's your monthly ad spend?", "type": "select",
     "options": ["Under $500", "$500-$2,000", "$2,000-$10,000", "$10,000+"]},
    {"question": "What's your biggest marketing frustration right now?", "type": "textarea"},
    {"question": "Do you have a DAM (Digital Asset Management) system?", "type": "select",
     "options": ["Yes", "No", "Not sure what that is"]},
    {"question": "How long does monthly reporting take?", "type": "select",
     "options": ["Less than 1 day", "1-2 days", "3-5 days", "More than 5 days"]},
    {"question": "Do you run A/B tests on your campaigns?", "type": "select",
     "options": ["Regularly", "Sometimes", "Rarely", "Never"]},
]


def safe_folder_name(name: str) -> str:
    """Convert a client name to a safe folder name."""
    safe = "".join(c if c.isalnum() or c in (" ", "-", "_") else "" for c in name)
    return safe.strip().replace(" ", "_") or "Client"


def create_project_structure(client_dir: Path, service_tier: str) -> list[str]:
    """Create the standard project folder structure for a new client."""
    folders = [
        "01_discovery",
        "02_audit",
        "03_architecture",
        "04_build",
        "05_delivery",
        "06_training",
        "07_reporting",
        "08_assets",
        "09_admin",
    ]
    created = []
    for folder in folders:
        folder_path = client_dir / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        # Add a README in each folder
        readme = folder_path / ".gitkeep"
        readme.touch()
        created.append(str(folder_path))
    return created


def create_checklist(client_dir: Path, client_name: str, service_tier: str) -> Path:
    """Create a detailed onboarding checklist markdown file."""
    tier_info = TIERS.get(service_tier, TIERS["Intelligence Build"])
    today = datetime.now().strftime("%Y-%m-%d")

    lines = [
        f"# Onboarding Checklist — {client_name}",
        f"",
        f"**Service Tier:** {service_tier}",
        f"**Price:** {tier_info['price']}",
        f"**Start Date:** {today}",
        f"**Estimated Duration:** {tier_info['weeks']} weeks",
        f"",
        f"---",
        f"",
        f"## Pre-Onboarding (Before Welcome Call)",
        f"",
        f"- [ ] Send welcome packet to client",
        f"- [ ] Send onboarding questionnaire",
        f"- [ ] Schedule welcome call (30 min)",
        f"- [ ] Create shared Google Drive / project folder",
        f"- [ ] Send NDA / agreement for signature",
        f"- [ ] Collect initial payment ({tier_info['price']})",
        f"",
        f"## Onboarding Steps",
        f"",
    ]

    for step in ONBOARDING_STEPS:
        if tier_info["weeks"] <= 1 and step["step"] > 2:
            continue  # Audit-only clients only get steps 1-2
        lines.extend([
            f"### Step {step['step']}: {step['title']} (Day ~{step['days']})",
            f"",
            f"**Task:** {step['description']}",
            f"**Deliverable:** {step['deliverable']}",
            f"",
            f"- [ ] {step['title']} — in progress",
            f"- [ ] {step['title']} — complete",
            f"- [ ] Deliverable sent to client",
            f"- [ ] Client feedback received",
            f"",
        ])

    lines.extend([
        f"## Post-Onboarding",
        f"",
        f"- [ ] 30-day check-in scheduled",
        f"- [ ] Retainer discussion (if Intelligence Partner tier)",
        f"- [ ] Case study permission requested",
        f"- [ ] Testimonial requested",
        f"- [ ] Referral request sent",
        f"",
        f"## Client Access Needed",
        f"",
        f"- [ ] Social media accounts (admin level)",
        f"- [ ] Analytics platforms (GA4, ads accounts)",
        f"- [ ] Current file storage (Google Drive, Dropbox, etc.)",
        f"- [ ] CMS / website admin (if applicable)",
        f"- [ ] CRM access (if applicable)",
        f"",
        f"---",
        f"",
        f"_Generated by M.O.T Innovation Client Onboarding Automation_",
        f"_{datetime.now().isoformat()}_",
    ])

    checklist_path = client_dir / "onboarding_checklist.md"
    checklist_path.write_text("\n".join(lines), encoding="utf-8")
    return checklist_path


def create_welcome_packet(client_dir: Path, client_name: str, service_tier: str,
                           client_email: str = "") -> Path:
    """Generate a welcome packet markdown template."""
    tier_info = TIERS.get(service_tier, TIERS["Intelligence Build"])
    content = f"""# Welcome to M.O.T Innovation, {client_name}!

_Generated: {datetime.now().strftime('%Y-%m-%d')}_

We're excited to partner with you on your marketing intelligence journey. This document outlines what to expect over the coming weeks.

---

## Your Engagement: {service_tier}

**Price:** {tier_info['price']}
**Estimated Duration:** {tier_info['weeks']} weeks
**Description:** {tier_info['description']}

## What Happens Next

"""
    for step in ONBOARDING_STEPS:
        if tier_info["weeks"] <= 1 and step["step"] > 2:
            continue
        content += f"### Step {step['step']}: {step['title']}\n"
        content += f"{step['description']}\n\n"
        content += f"**Deliverable:** {step['deliverable']}\n\n"

    content += f"""---

## What We Need From You

Please complete the onboarding questionnaire (attached separately). This helps us understand your current setup before the welcome call.

### Access We'll Need

- Your social media accounts (admin/access level)
- Your analytics platforms (GA4, ads accounts, etc.)
- Your current file storage (Google Drive, Dropbox, etc.)
- Your CMS/website admin (if applicable)
- Your CRM (if applicable)

## What You'll Get

- Working marketing intelligence infrastructure (not slide decks)
- Full ownership of everything we build — no black boxes
- Team training on the new system
- Documentation pack
- 30 days of support after handover

## Our Commitment

1. **We build working systems**, not slide decks
2. **You own everything** we build — no black boxes
3. **We train your team**, not just deliver and disappear
4. **We support you** for 30 days after handover

## Contact

- **Email:** hello@motinnovation.co.za
- **Website:** https://motinnovation.co.za
"""
    if client_email:
        content += f"- **Your contact on file:** {client_email}\n"

    content += f"""
---

**M.O.T Innovation**
Marketing Intelligence, Engineered.
hello@motinnovation.co.za
"""

    packet_path = client_dir / "welcome_packet.md"
    packet_path.write_text(content, encoding="utf-8")
    return packet_path


def create_questionnaire(client_dir: Path) -> Path:
    """Write the onboarding questionnaire as a markdown file."""
    lines = ["# M.O.T Innovation — Onboarding Questionnaire", "",
             "Please answer the following questions before our welcome call.", ""]

    for i, q in enumerate(QUESTIONNAIRE, 1):
        lines.append(f"### {i}. {q['question']}")
        lines.append(f"_Type: {q['type']}_")
        if "options" in q:
            for opt in q["options"]:
                lines.append(f"- [ ] {opt}")
        lines.append("")
        lines.append("**Your answer:** ")
        lines.append("")

    lines.append("---")
    lines.append(f"_Generated by M.O.T Innovation Client Onboarding Automation_")

    path = client_dir / "onboarding_questionnaire.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def create_project_config(client_dir: Path, client_name: str, service_tier: str,
                          client_email: str) -> Path:
    """Create a project.json config file for this client."""
    config = {
        "client_name": client_name,
        "client_email": client_email,
        "service_tier": service_tier,
        "price": TIERS.get(service_tier, {}).get("price", ""),
        "start_date": datetime.now().isoformat(),
        "status": "onboarding",
        "steps": ONBOARDING_STEPS,
    }
    path = client_dir / "project.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    return path


def onboard_client(client_name: str, service_tier: str, client_email: str = "") -> dict:
    """Full onboarding pipeline for a new client."""
    folder_name = safe_folder_name(client_name)
    client_dir = ONBOARDING_DIR / folder_name
    client_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("M.O.T INNOVATION — CLIENT ONBOARDING")
    print("=" * 60)
    print(f"\n🏢 Client: {client_name}")
    print(f"📦 Tier:   {service_tier}")
    print(f"📧 Email:  {client_email or 'N/A'}")
    print(f"📁 Folder: {client_dir}\n")

    # 1. Create project folder structure
    print("── Step 1: Creating project folder structure ──")
    folders = create_project_structure(client_dir, service_tier)
    for f in folders:
        print(f"  📁 {f}")

    # 2. Create onboarding checklist
    print("\n── Step 2: Creating onboarding checklist ──")
    checklist = create_checklist(client_dir, client_name, service_tier)
    print(f"  ✅ {checklist}")

    # 3. Generate welcome packet
    print("\n── Step 3: Generating welcome packet ──")
    packet = create_welcome_packet(client_dir, client_name, service_tier, client_email)
    print(f"  ✅ {packet}")

    # 4. Create onboarding questionnaire
    print("\n── Step 4: Creating onboarding questionnaire ──")
    questionnaire = create_questionnaire(client_dir)
    print(f"  ✅ {questionnaire}")

    # 5. Create project.json
    print("\n── Step 5: Creating project config ──")
    config = create_project_config(client_dir, client_name, service_tier, client_email)
    print(f"  ✅ {config}")

    print(f"\n✅ Onboarding complete for {client_name}!")
    print(f"📁 All files in: {client_dir}")

    return {
        "client_name": client_name,
        "service_tier": service_tier,
        "client_email": client_email,
        "folder": str(client_dir),
        "files": {
            "checklist": str(checklist),
            "welcome_packet": str(packet),
            "questionnaire": str(questionnaire),
            "project_config": str(config),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="M.O.T Innovation — Client Onboarding Automation"
    )
    parser.add_argument("--client-name", type=str, default="Demo Client",
                        help="Name of the client to onboard")
    parser.add_argument("--service-tier", type=str, default="Intelligence Build",
                        choices=list(TIERS.keys()),
                        help="Service tier")
    parser.add_argument("--client-email", type=str, default="",
                        help="Client contact email")
    args = parser.parse_args()

    result = onboard_client(args.client_name, args.service_tier, args.client_email)
    return 0


if __name__ == "__main__":
    sys.exit(main())