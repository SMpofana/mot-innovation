#!/usr/bin/env python
"""
Lead Scoring & Ranking — M.O.T Innovation

Reads all leads from ../leads/leads.json and ranks them by stage:
    Enterprise > Established > Have some systems > Just starting

Outputs a ranked report to console and writes scored_leads.json + ranked_leads.csv

Usage:
    python lead_scoring.py                    # Score and rank all leads
    python lead_scoring.py --verbose           # Show full details per lead
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
LEADS_DIR = BASE_DIR / "leads"
LEADS_JSON = LEADS_DIR / "leads.json"
SCORED_JSON = LEADS_DIR / "scored_leads.json"
RANKED_CSV = LEADS_DIR / "ranked_leads.csv"

STAGE_PRIORITY = {
    "Enterprise": 4,
    "Established": 3,
    "Have some systems": 2,
    "Just starting": 1,
}


def load_leads() -> list[dict]:
    if not LEADS_JSON.exists():
        return []
    with open(LEADS_JSON, "r", encoding="utf-8") as f:
        leads = json.load(f)
    return leads if isinstance(leads, list) else []


def rank_leads(leads: list[dict]) -> list[dict]:
    """Sort leads: highest stage priority first, then by score descending."""
    def sort_key(lead: dict) -> tuple:
        stage = lead.get("stage", "Just starting")
        stage_rank = STAGE_PRIORITY.get(stage, 1)
        score = lead.get("score", 0)
        return (stage_rank, score)

    return sorted(leads, key=sort_key, reverse=True)


def write_ranked_csv(ranked: list[dict]) -> None:
    fields = ["rank", "id", "name", "email", "business", "stage", "score", "priority", "timestamp", "source"]
    with open(RANKED_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for i, lead in enumerate(ranked, 1):
            lead_with_rank = {**lead, "rank": i}
            writer.writerow(lead_with_rank)


def write_scored_json(ranked: list[dict]) -> None:
    output = {
        "generated_at": datetime.now().isoformat(),
        "total_leads": len(ranked),
        "ranked_leads": [
            {**lead, "rank": i}
            for i, lead in enumerate(ranked, 1)
        ],
    }
    with open(SCORED_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


def print_report(ranked: list[dict], verbose: bool = False) -> None:
    print("=" * 70)
    print("M.O.T INNOVATION — LEAD SCORING & RANKING REPORT")
    print("=" * 70)
    print(f"\nTotal leads: {len(ranked)}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Stage distribution
    stage_counts: dict[str, int] = {}
    for lead in ranked:
        stage = lead.get("stage", "Just starting")
        stage_counts[stage] = stage_counts.get(stage, 0) + 1

    print("── Stage Distribution ──")
    for stage in ["Enterprise", "Established", "Have some systems", "Just starting"]:
        count = stage_counts.get(stage, 0)
        bar = "█" * count
        print(f"  {stage:<22} {count:>3}  {bar}")

    # Priority distribution
    priority_counts: dict[str, int] = {}
    for lead in ranked:
        p = lead.get("priority", "COLD")
        priority_counts[p] = priority_counts.get(p, 0) + 1

    print(f"\n── Priority Distribution ──")
    for p in ["HOT", "WARM", "COLD"]:
        count = priority_counts.get(p, 0)
        print(f"  {p:<6} {count:>3}")

    # Ranked list
    print(f"\n── Ranked Leads ──")
    print(f"{'Rank':<5} {'Name':<25} {'Stage':<22} {'Score':<6} {'Priority':<8} {'Business'}")
    print("-" * 90)
    for i, lead in enumerate(ranked, 1):
        name = lead.get("name", "Unknown")[:24]
        stage = lead.get("stage", "Just starting")[:21]
        score = lead.get("score", 0)
        priority = lead.get("priority", "COLD")
        business = (lead.get("business", "") or "—")[:20]
        print(f"{i:<5} {name:<25} {stage:<22} {score:<6} {priority:<8} {business}")

        if verbose:
            email = lead.get("email", "")
            msg = (lead.get("message", "") or "")[:80]
            source = lead.get("source", "")
            ts = lead.get("timestamp", "")[:19]
            print(f"      Email: {email}")
            print(f"      Source: {source} | Captured: {ts}")
            if msg:
                print(f"      Message: {msg}")
            print()

    print("-" * 90)
    print(f"\n📁 Ranked CSV:  {RANKED_CSV}")
    print(f"📁 Scored JSON: {SCORED_JSON}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="M.O.T Innovation — Lead Scoring & Ranking"
    )
    parser.add_argument("--verbose", action="store_true", help="Show full lead details")
    args = parser.parse_args()

    leads = load_leads()
    if not leads:
        print("⚠️  No leads found. Run lead_capture.py first to capture some leads.")
        return 1

    ranked = rank_leads(leads)
    write_ranked_csv(ranked)
    write_scored_json(ranked)
    print_report(ranked, verbose=args.verbose)
    return 0


if __name__ == "__main__":
    sys.exit(main())