# M.O.T Innovation — Automation Pipelines

**Marketing Intelligence, Engineered.**

This directory contains automation scripts for ALL business processes at M.O.T Innovation. Each script runs independently or via the master runner.

## Quick Start

```bash
# Run ALL pipelines in sequence
python run_all.py

# Run individual pipelines
python lead_capture.py
python lead_scoring.py
python lead_nurturing.py
python client_onboarding.py
python reporting.py
python content_pipeline.py

# Skip specific pipelines
python run_all.py --skip-content --skip-nurturing

# Verbose output
python run_all.py --verbose
```

---

## Directory Structure

```
mot_innovation/
├── automation/
│   ├── run_all.py              # Master runner — executes all pipelines
│   ├── lead_capture.py         # Lead capture from contact form submissions
│   ├── lead_scoring.py         # Ranks leads by stage (Enterprise > Just starting)
│   ├── lead_nurturing.py       # Automated email sequence (Day 0 → Day 14)
│   ├── client_onboarding.py    # Auto-generates project folders, checklists, welcome packets
│   ├── reporting.py            # Weekly status reports (leads, pipeline, revenue)
│   ├── content_pipeline.py     # Reddit pain points → social media posts → content calendar
│   ├── email_templates/        # Email sequence templates (5 emails)
│   │   ├── day0_welcome.txt
│   │   ├── day1_case_study_ecommerce.txt
│   │   ├── day3_case_study_saas.txt
│   │   ├── day7_pricing_breakdown.txt
│   │   └── day14_final_followup.txt
│   └── README.md               # This file
├── leads/                      # Lead data (CSV + JSON)
├── reports/                    # Generated weekly reports
├── notifications/              # Lead capture notifications
├── nurturing/                  # Nurturing emails per lead
├── onboarding/                 # Client project folders
└── content_calendar/           # Social media content calendar + posts
```

---

## 1. Lead Capture Automation (`lead_capture.py`)

**What it does:** Captures leads from the website contact form (POST `/api/lead`), logs them, sends notifications, and scores them.

**Features:**
- Logs leads to CSV (`leads/leads.csv`) and JSON (`leads/leads.json`)
- Sends notifications (console + `notifications/notifications.json`)
- Scores each lead based on stage, business name, message detail, email domain, and source
- Ranks leads by stage: **Enterprise > Established > Have some systems > Just starting**
- Priority labels: **HOT** (score ≥ 60), **WARM** (score ≥ 40), **COLD** (score < 40)

**Usage:**
```bash
# Demo mode (sample lead)
python lead_capture.py

# Single lead via JSON
python lead_capture.py --lead '{"name":"Jane","email":"jane@corp.co.za","business":"Corp Ltd","stage":"Enterprise","message":"Need DAM setup for 50-person team"}'

# Batch import from JSON file
python lead_capture.py --file leads_batch.json
```

**Programmatic use:**
```python
from lead_capture import capture_lead
lead = capture_lead({
    "name": "Jane Doe",
    "email": "jane@corp.co.za",
    "business": "Corp Ltd",
    "stage": "Enterprise",
    "message": "Need DAM setup for our team",
})
```

---

## 2. Lead Scoring & Ranking (`lead_scoring.py`)

**What it does:** Reads all captured leads and ranks them by stage priority and score.

**Output:**
- `leads/ranked_leads.csv` — Ranked leads with rank numbers
- `leads/scored_leads.json` — Full scored lead data

**Usage:**
```bash
python lead_scoring.py             # Score and rank all leads
python lead_scoring.py --verbose   # Show full details per lead
```

---

## 3. Lead Nurturing Sequence (`lead_nurturing.py`)

**What it does:** Manages a 5-email nurturing sequence over 14 days. Renders email templates with lead data and writes them to `nurturing/{lead_id}/`.

**Email Sequence:**
| Day | Subject | Template File |
|-----|---------|---------------|
| 0 | Welcome + consultation booking | `day0_welcome.txt` |
| 1 | Case study: E-commerce 80% time reduction | `day1_case_study_ecommerce.txt` |
| 3 | Case study: SaaS 23% conversion improvement | `day3_case_study_saas.txt` |
| 7 | Pricing breakdown + CTA | `day7_pricing_breakdown.txt` |
| 14 | Final follow-up | `day14_final_followup.txt` |

**Usage:**
```bash
python lead_nurturing.py                  # Process all leads
python lead_nurturing.py --lead-id lead_xxx  # Single lead
python lead_nurturing.py --verbose        # Show full email content
```

**To wire to Resend/SendGrid later:**
The rendered emails are in `nurturing/{lead_id}/`. Each file contains the full email text. A future step can read these files and send them via the Resend/SendGrid API.

---

## 4. Client Onboarding Automation (`client_onboarding.py`)

**What it does:** When a client signs up, generates a complete project folder structure, onboarding checklist, welcome packet, and questionnaire.

**Generated Structure:**
```
onboarding/{Client_Name}/
├── project.json              # Project config (client, tier, status, steps)
├── onboarding_checklist.md   # Full checklist with all steps
├── welcome_packet.md         # Welcome packet for the client
├── onboarding_questionnaire.md  # 10-question onboarding survey
├── 01_discovery/
├── 02_audit/
├── 03_architecture/
├── 04_build/
├── 05_delivery/
├── 06_training/
├── 07_reporting/
├── 08_assets/
└── 09_admin/
```

**Usage:**
```bash
# Demo client
python client_onboarding.py

# Real client
python client_onboarding.py --client-name "Acme Corp" --service-tier "Intelligence Build" --client-email "ceo@acme.com"
```

**Service Tiers:**
- `Infrastructure Audit` — $500, 1 week
- `Intelligence Build` — $2,500–$5,000, 4 weeks
- `Intelligence Partner` — $1,000+/month, ongoing

---

## 5. Reporting Automation (`reporting.py`)

**What it does:** Generates weekly (or monthly) status reports from leads, pipeline status, and revenue tracking.

**Report Contents:**
- Executive summary (leads, projected revenue, active clients)
- Leads received this period (with table)
- Pipeline status (by stage and priority)
- Revenue tracking (potential + projected with conversion rates)
- Client onboarding status
- Nurturing sequence status
- Recommended actions

**Output:**
- `reports/report_weekly_{timestamp}.md` — Markdown report
- `reports/report_weekly_{timestamp}.json` — JSON data

**Usage:**
```bash
python reporting.py                  # Weekly report
python reporting.py --period monthly # Monthly report
python reporting.py --verbose        # Print full report to console
```

---

## 6. Social Media Content Pipeline (`content_pipeline.py`)

**What it does:** Connects to the existing agent-team Reddit RSS pipeline, pulls pain points from Reddit, generates social media posts about M.O.T Innovation services, and schedules them into a content calendar.

**Pipeline Stages:**
1. **Scan Reddit** — Pulls pain points from r/marketing, r/digitalmarketing, r/smallbusiness, etc. via RSS
2. **Match to services** — Matches complaints to M.O.T services (DAM, Delivery, Tracking, Optimization)
3. **Generate posts** — Creates social media posts per service + brand awareness posts
4. **Schedule calendar** — Distributes posts across LinkedIn, Twitter, Instagram, Facebook over 30 days

**Integration with agent-team:**
- Reads existing pain points from `C:\Users\mpofa\agent-team\store\painpoints.json` if available
- Uses the same Reddit RSS scanning pattern as `agents/painpoint_scanner.py`

**Output:**
- `content_calendar/painpoints.json` — Scanned Reddit pain points
- `content_calendar/social_posts.json` — Generated social media posts
- `content_calendar/content_calendar.md` — Scheduled content calendar
- `content_calendar/content_calendar.json` — Calendar data

**Usage:**
```bash
python content_pipeline.py                # Full pipeline
python content_pipeline.py --scan-only   # Only scan Reddit
python content_pipeline.py --generate-only  # Only generate posts
python content_pipeline.py --schedule-only  # Only schedule calendar
python content_pipeline.py --verbose      # Show full post content
```

---

## Master Runner (`run_all.py`)

Runs all pipelines in sequence:
1. Lead Capture → 2. Lead Scoring → 3. Lead Nurturing → 4. Client Onboarding → 5. Reporting → 6. Content Pipeline

```bash
python run_all.py                  # Run everything
python run_all.py --skip-content    # Skip Reddit content pipeline
python run_all.py --skip-nurturing  # Skip nurturing
python run_all.py --verbose          # Verbose output
```

---

## Integration Notes

### Website Lead API (`/api/lead`)
The Next.js contact form posts to `/api/lead` (see `src/app/api/lead/route.ts`). To connect the form to this automation:

**Option A (recommended):** Have the API route call `lead_capture.py` via subprocess:
```typescript
import { exec } from 'child_process';
// In route.ts POST handler:
exec(`python automation/lead_capture.py --lead '${JSON.stringify(lead)}'`);
```

**Option B:** Rewrite `lead_capture.py` as an API endpoint (importable module).

### Email Service (Resend/SendGrid)
Nurturing emails are written as text files in `nurturing/{lead_id}/`. To wire to a real email service:
1. Add `RESEND_API_KEY` to `.env`
2. Create a `send_email.py` that reads from `nurturing/` and sends via the Resend API
3. Run it on a cron schedule (daily)

### Existing Agent-Team Pipeline
This automation suite works alongside the existing agent-team pipeline at `C:\Users\mpofa\agent-team\`. The content pipeline reads pain points from `store/painpoints.json` if available, and the reporting script can reference pipeline data from `store/mot_innovation/`.

---

## Pricing Reference

| Service | Price | Duration |
|---------|-------|----------|
| Infrastructure Audit | $500 | 1 week |
| Intelligence Build | $2,500–$5,000 | 4 weeks |
| Intelligence Partner | $1,000+/month | Ongoing |
| Free Consultation | $0 | 30 min |

**Contact:** hello@motinnovation.co.za | https://motinnovation.co.za

---

_Generated by M.O.T Innovation Automation_
_Marketing Intelligence, Engineered._