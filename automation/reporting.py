#!/usr/bin/env python
"""
Reporting Automation — M.O.T Innovation

Generates a weekly status report from:
1. Leads received (from leads/ directory)
2. Pipeline status (lead stages and priorities)
3. Revenue tracking (based on service tiers and lead conversions)

Writes reports to ../reports/ as both markdown and JSON.

Usage:
    python reporting.py                        # Generate this week's report
    python reporting.py --period weekly        # Weekly report (default)
    python reporting.py --period monthly       # Monthly report
    python reporting.py --verbose              # Print full report to console
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
LEADS_DIR = BASE_DIR / "leads"
REPORTS_DIR = BASE_DIR / "reports"
NURTURING_DIR = BASE_DIR / "nurturing"
ONBOARDING_DIR = BASE_DIR / "onboarding"

LEADS_JSON = LEADS_DIR / "leads.json"
LEADS_CSV = LEADS_DIR / "leads.csv"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Revenue mapping per stage / tier
TIER_PRICING = {
    "Infrastructure Audit": {"low": 500, "high": 500, "label": "$500"},
    "Intelligence Build": {"low": 2500, "high": 5000, "label": "$2,500–$5,000"},
    "Intelligence Partner": {"low": 1000, "high": 5000, "label": "$1,000+/month"},
}

# Estimated conversion probability by priority
PRIORITY_CONVERSION = {
    "HOT": 0.30,
    "WARM": 0.15,
    "COLD": 0.05,
}

# Estimated revenue per lead based on stage
STAGE_REVENUE = {
    "Enterprise": 5000,
    "Established": 3500,
    "Have some systems": 2500,
    "Just starting": 500,
}


def load_leads() -> list[dict]:
    if not LEADS_JSON.exists():
        return []
    with open(LEADS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def filter_leads_by_period(leads: list[dict], period: str) -> list[dict]:
    """Filter leads to those captured within the reporting period."""
    now = datetime.now()
    if period == "weekly":
        cutoff = now - timedelta(days=7)
    elif period == "monthly":
        cutoff = now - timedelta(days=30)
    else:
        return leads

    filtered = []
    for lead in leads:
        ts = lead.get("timestamp", "")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(ts)
            if dt >= cutoff:
                filtered.append(lead)
        except (ValueError, TypeError):
            continue
    return filtered


def calculate_pipeline_status(leads: list[dict]) -> dict:
    """Calculate pipeline status from leads."""
    total = len(leads)
    by_stage: dict[str, int] = {}
    by_priority: dict[str, int] = {}
    scores = []

    for lead in leads:
        stage = lead.get("stage", "Just starting")
        by_stage[stage] = by_stage.get(stage, 0) + 1

        priority = lead.get("priority", "COLD")
        by_priority[priority] = by_priority.get(priority, 0) + 1

        scores.append(lead.get("score", 0))

    avg_score = sum(scores) / len(scores) if scores else 0

    return {
        "total_leads": total,
        "by_stage": by_stage,
        "by_priority": by_priority,
        "average_score": round(avg_score, 1),
    }


def calculate_revenue(leads: list[dict]) -> dict:
    """Calculate revenue tracking from leads."""
    total_leads = len(leads)
    projected_revenue = 0
    potential_revenue = 0
    hot_leads = 0
    warm_leads = 0
    cold_leads = 0

    for lead in leads:
        stage = lead.get("stage", "Just starting")
        priority = lead.get("priority", "COLD")
        base_revenue = STAGE_REVENUE.get(stage, 500)
        potential_revenue += base_revenue

        conv_rate = PRIORITY_CONVERSION.get(priority, 0.05)
        projected_revenue += base_revenue * conv_rate

        if priority == "HOT":
            hot_leads += 1
        elif priority == "WARM":
            warm_leads += 1
        else:
            cold_leads += 1

    return {
        "total_leads": total_leads,
        "potential_revenue": potential_revenue,
        "projected_revenue": round(projected_revenue, 2),
        "hot_leads": hot_leads,
        "warm_leads": warm_leads,
        "cold_leads": cold_leads,
    }


def count_onboarded_clients() -> dict:
    """Count client folders in the onboarding directory."""
    if not ONBOARDING_DIR.exists():
        return {"active_clients": 0, "client_folders": []}

    client_folders = []
    for item in ONBOARDING_DIR.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            config_file = item / "project.json"
            client_folders.append({
                "folder": item.name,
                "config_exists": config_file.exists(),
            })

    return {
        "active_clients": len(client_folders),
        "client_folders": client_folders,
    }


def count_nurturing_emails() -> dict:
    """Count nurturing emails generated."""
    state_file = NURTURING_DIR / "nurturing_state.json"
    if not state_file.exists():
        return {"leads_in_nurturing": 0, "total_emails_sent": 0}

    with open(state_file, "r", encoding="utf-8") as f:
        state = json.load(f)

    leads_state = state.get("leads", {})
    total_emails = sum(len(v.get("sent_emails", [])) for v in leads_state.values())
    return {
        "leads_in_nurturing": len(leads_state),
        "total_emails_sent": total_emails,
    }


def generate_markdown_report(
    period: str, leads: list[dict], pipeline: dict, revenue: dict,
    onboarding: dict, nurturing: dict
) -> str:
    """Generate the weekly report as markdown."""
    period_label = "Weekly" if period == "weekly" else "Monthly"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    period_start = (datetime.now() - (timedelta(days=7) if period == "weekly" else timedelta(days=30))).strftime("%Y-%m-%d")

    lines = [
        f"# M.O.T Innovation — {period_label} Status Report",
        f"",
        f"_Generated: {now_str} | Period: {period_start} → {datetime.now().strftime('%Y-%m-%d')}_",
        f"",
        f"---",
        f"",
        f"## 📊 Executive Summary",
        f"",
        f"- **Total leads (period):** {len(leads)}",
        f"- **Pipeline value (projected):** ${revenue['projected_revenue']:,.2f}",
        f"- **Pipeline value (potential):** ${revenue['potential_revenue']:,.2f}",
        f"- **Active clients:** {onboarding['active_clients']}",
        f"- **Leads in nurturing:** {nurturing['leads_in_nurturing']}",
        f"",
        f"---",
        f"",
        f"## 🎯 Leads Received ({period_label})",
        f"",
        f"| # | Name | Business | Stage | Score | Priority | Date |",
        f"|---|------|----------|-------|-------|----------|------|",
    ]

    for i, lead in enumerate(leads, 1):
        name = lead.get("name", "Unknown")[:20]
        business = (lead.get("business", "") or "—")[:20]
        stage = lead.get("stage", "Just starting")
        score = lead.get("score", 0)
        priority = lead.get("priority", "COLD")
        ts = lead.get("timestamp", "")[:10]
        lines.append(f"| {i} | {name} | {business} | {stage} | {score} | {priority} | {ts} |")

    if not leads:
        lines.append(f"| — | No leads this period | — | — | — | — | — |")

    lines.extend([
        f"",
        f"---",
        f"",
        f"## 📈 Pipeline Status",
        f"",
        f"### By Stage",
        f"",
        f"| Stage | Count | % |",
        f"|-------|-------|---|",
    ])

    total = pipeline["total_leads"] or 1
    for stage in ["Enterprise", "Established", "Have some systems", "Just starting"]:
        count = pipeline["by_stage"].get(stage, 0)
        pct = (count / total * 100) if total else 0
        lines.append(f"| {stage} | {count} | {pct:.0f}% |")

    lines.extend([
        f"",
        f"### By Priority",
        f"",
        f"| Priority | Count | Conversion Est. | Projected Revenue |",
        f"|----------|-------|------------------|--------------------|",
    ])

    for priority in ["HOT", "WARM", "COLD"]:
        count = pipeline["by_priority"].get(priority, 0)
        conv = PRIORITY_CONVERSION.get(priority, 0.05)
        est_rev = count * 3000 * conv  # rough average
        lines.append(f"| {priority} | {count} | {conv*100:.0f}% | ${est_rev:,.0f} |")

    lines.extend([
        f"",
        f"**Average lead score:** {pipeline['average_score']}",
        f"",
        f"---",
        f"",
        f"## 💰 Revenue Tracking",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Potential revenue (all leads) | ${revenue['potential_revenue']:,.2f} |",
        f"| Projected revenue (weighted) | ${revenue['projected_revenue']:,.2f} |",
        f"| HOT leads (30% conv) | {revenue['hot_leads']} |",
        f"| WARM leads (15% conv) | {revenue['warm_leads']} |",
        f"| COLD leads (5% conv) | {revenue['cold_leads']} |",
        f"",
        f"### Revenue by Stage",
        f"",
        f"| Stage | Leads | Est. Revenue/Lead | Total Potential |",
        f"|-------|-------|-------------------|-----------------|",
    ])

    for stage in ["Enterprise", "Established", "Have some systems", "Just starting"]:
        count = pipeline["by_stage"].get(stage, 0)
        rev_per = STAGE_REVENUE.get(stage, 500)
        total_potential = count * rev_per
        lines.append(f"| {stage} | {count} | ${rev_per:,} | ${total_potential:,} |")

    lines.extend([
        f"",
        f"---",
        f"",
        f"## 🏢 Client Onboarding Status",
        f"",
        f"- **Active clients:** {onboarding['active_clients']}",
    ])

    for cf in onboarding.get("client_folders", []):
        lines.append(f"  - {cf['folder']} {'(configured)' if cf['config_exists'] else '(no config)'}")

    lines.extend([
        f"",
        f"---",
        f"",
        f"## ✉️ Lead Nurturing Status",
        f"",
        f"- **Leads in nurturing sequence:** {nurturing['leads_in_nurturing']}",
        f"- **Total emails generated:** {nurturing['total_emails_sent']}",
        f"",
        f"---",
        f"",
        f"## ✅ Recommended Actions",
        f"",
    ])

    # Generate recommendations
    actions = []
    if revenue["hot_leads"] > 0:
        actions.append(f"🔥 **Follow up with {revenue['hot_leads']} HOT lead(s) immediately** — highest conversion probability")
    if revenue["warm_leads"] > 0:
        actions.append(f"📋 **Nurture {revenue['warm_leads']} WARM lead(s)** — schedule consultations")
    if revenue["cold_leads"] > 0:
        actions.append(f"❄️  **Add {revenue['cold_leads']} COLD lead(s)** to long-term nurturing sequence")
    if onboarding["active_clients"] > 0:
        actions.append(f"🏢 **Check in on {onboarding['active_clients']} active client(s)** — ensure onboarding on track")
    if not leads:
        actions.append("📊 **No leads this period** — consider increasing content output and outreach")
    actions.append("🔄 **Re-run this report next week** to track progress")

    for action in actions:
        lines.append(f"- {action}")

    lines.extend([
        f"",
        f"---",
        f"",
        f"_Generated by M.O.T Innovation Reporting Automation_",
        f"_{now_str}_",
    ])

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="M.O.T Innovation — Reporting Automation"
    )
    parser.add_argument("--period", choices=["weekly", "monthly"], default="weekly",
                        help="Reporting period (default: weekly)")
    parser.add_argument("--verbose", action="store_true",
                        help="Print full report to console")
    args = parser.parse_args()

    print("=" * 60)
    print(f"M.O.T INNOVATION — {args.period.upper()} STATUS REPORT")
    print("=" * 60)

    # Gather data
    all_leads = load_leads()
    period_leads = filter_leads_by_period(all_leads, args.period)
    pipeline = calculate_pipeline_status(all_leads)
    revenue = calculate_revenue(period_leads)
    onboarding = count_onboarded_clients()
    nurturing = count_nurturing_emails()

    print(f"\n📊 Total leads (all time): {len(all_leads)}")
    print(f"📊 Leads this {args.period}: {len(period_leads)}")
    print(f"💰 Projected revenue: ${revenue['projected_revenue']:,.2f}")
    print(f"🏢 Active clients: {onboarding['active_clients']}")
    print(f"✉️  Nurturing: {nurturing['leads_in_nurturing']} leads, {nurturing['total_emails_sent']} emails")

    # Generate markdown report
    md_report = generate_markdown_report(
        args.period, period_leads, pipeline, revenue, onboarding, nurturing
    )

    # Write files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = REPORTS_DIR / f"report_{args.period}_{timestamp}.md"
    json_path = REPORTS_DIR / f"report_{args.period}_{timestamp}.json"

    md_path.write_text(md_report, encoding="utf-8")

    json_data = {
        "generated_at": datetime.now().isoformat(),
        "period": args.period,
        "period_leads_count": len(period_leads),
        "all_leads_count": len(all_leads),
        "pipeline": pipeline,
        "revenue": revenue,
        "onboarding": onboarding,
        "nurturing": nurturing,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Report generated!")
    print(f"📄 Markdown: {md_path}")
    print(f"📄 JSON:     {json_path}")

    if args.verbose:
        print(f"\n{'=' * 60}")
        print(md_report)

    return 0


if __name__ == "__main__":
    sys.exit(main())