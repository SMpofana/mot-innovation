"""
Shared data for the M.O.T Innovation content engine.

All pain points, services, case studies, and brand constants live here so every
module references a single source of truth (mirrors src/content.ts).
"""
from __future__ import annotations

# ── Brand ────────────────────────────────────────────────────────────────────
BRAND_NAME = "M.O.T Innovation"
WEBSITE_URL = "https://motinnovation.co.za"
BOOKING_URL = "https://calendly.com/mpofanas/15-min-discovery-call"
TAGLINE = "Marketing Intelligence, Engineered."

# ── Pain Points (top 6 from research) ────────────────────────────────────────
PAIN_POINTS = [
    {
        "id": "disconnected_tools",
        "title": "Disconnected marketing tools",
        "summary": "The average marketing team uses 12+ tools and fewer than half talk to each other.",
        "stat": "12+ tools. Fewer than half connected.",
        "subreddit_keywords": ["tools", "stack", "integration", "disconnected", "zapier"],
    },
    {
        "id": "manual_posting",
        "title": "Manual social media posting takes too long",
        "summary": "Posting manually to each platform wastes hours every week and is error-prone.",
        "stat": "10+ hours/week lost to manual posting.",
        "subreddit_keywords": ["posting", "social media", "scheduling", "manual", "buffer"],
    },
    {
        "id": "scattered_assets",
        "title": "Scattered marketing assets / no DAM",
        "summary": "Assets scattered across Google Drive, Dropbox, and laptops. No consistent naming.",
        "stat": "40% of creative time spent searching for files.",
        "subreddit_keywords": ["assets", "files", "dam", "google drive", "dropbox", "disorganized"],
    },
    {
        "id": "manual_reporting",
        "title": "Marketing reporting takes too long",
        "summary": "Reporting takes days of manual spreadsheet work and is often outdated by delivery.",
        "stat": "2+ days/month spent building reports nobody reads.",
        "subreddit_keywords": ["reporting", "dashboard", "spreadsheet", "analytics", "metrics"],
    },
    {
        "id": "wasting_ad_spend",
        "title": "Wasting money on ads / no A/B testing",
        "summary": "Ad spend flying blind with no systematic A/B testing or budget reallocation.",
        "stat": "Up to 40% of ad budget wasted without optimization.",
        "subreddit_keywords": ["ads", "ad spend", "roas", "a/b test", "google ads", "meta ads"],
    },
    {
        "id": "want_builder_not_advisor",
        "title": "Want someone to BUILD not just advise",
        "summary": "Tired of consultants who deliver slide decks. Businesses want working systems.",
        "stat": "We build the system. You own it. We hand over the keys.",
        "subreddit_keywords": ["consultant", "agency", "build", "advise", "implement"],
    },
]

# ── Services ─────────────────────────────────────────────────────────────────
SERVICES = {
    "dam": {
        "id": "dam",
        "name": "Digital Marketing Infrastructure",
        "short": "DAM",
        "icon": "🗄️",
        "description": "DAM setup, content taxonomy, cloud storage architecture, version control.",
        "deliverable": "A centralized asset hub your whole team can use",
        "timeline": "2-3 weeks",
        "price": "$2,500-$5,000",
        "keywords": ["scattered_assets", "disconnected_tools", "want_builder_not_advisor"],
        "hashtags": ["#DAM", "#DigitalAssets", "#MarketingInfrastructure"],
        "angle": "Stop hunting for files. A proper DAM system means finding any asset in seconds, not hours.",
    },
    "delivery": {
        "id": "delivery",
        "name": "Multi-Endpoint Delivery",
        "short": "Delivery",
        "icon": "📡",
        "description": "Push content to every social platform, email, ad network, and web channel from one source.",
        "deliverable": "One content source, every channel served automatically",
        "timeline": "1-2 weeks",
        "price": "$2,500-$5,000",
        "keywords": ["manual_posting", "disconnected_tools"],
        "hashtags": ["#SocialMediaManagement", "#ContentDistribution", "#MultiChannel"],
        "angle": "One content source, every channel served. Stop posting manually to each platform.",
    },
    "tracking": {
        "id": "tracking",
        "name": "Performance Tracking & Reporting",
        "short": "Dashboards",
        "icon": "📊",
        "description": "Unified dashboards pulling data from every channel. Real-time KPIs, automated reports.",
        "deliverable": "One dashboard that tells you exactly what's working",
        "timeline": "1-2 weeks",
        "price": "$2,500-$5,000",
        "keywords": ["manual_reporting", "disconnected_tools"],
        "hashtags": ["#MarketingAnalytics", "#Dashboards", "#KPI"],
        "angle": "If you can't measure it, you can't improve it. Unified dashboards that tell you what's actually working.",
    },
    "optimization": {
        "id": "optimization",
        "name": "Campaign Optimization",
        "short": "Optimization",
        "icon": "⚡",
        "description": "A/B testing frameworks, budget reallocation, audience targeting refinement, automated rules.",
        "deliverable": "Campaigns that improve themselves over time",
        "timeline": "Ongoing",
        "price": "$1,000+/mo",
        "keywords": ["wasting_ad_spend"],
        "hashtags": ["#AdOptimization", "#PPC", "#ROAS"],
        "angle": "Stop wasting ad budget. Proper optimization and A/B testing can 2-3x your ROAS.",
    },
}

# ── Case Studies ─────────────────────────────────────────────────────────────
CASE_STUDIES = [
    {
        "id": "ecommerce",
        "client": "E-commerce Brand",
        "challenge": "Product photos scattered across Google Drive, Dropbox, and individual laptops. No consistent naming. Social media posting was manual and error-prone.",
        "solution": "Centralized DAM with auto-tagging, built delivery pipeline to Instagram, Facebook, and email. Set up performance dashboard tracking conversions per channel.",
        "result": "80% reduction in time-to-publish. Clear view of which channels actually drove sales.",
        "result_stat": "80% reduction in time-to-publish",
        "services": ["dam", "delivery", "tracking"],
    },
    {
        "id": "saas",
        "client": "SaaS Startup",
        "challenge": "Marketing data spread across 6 platforms with no unified view. Reporting took 2 days per month and was often outdated by the time it reached leadership.",
        "solution": "Built unified dashboard pulling from all 6 sources. Automated weekly executive summaries. Set up A/B testing framework for landing pages.",
        "result": "Reporting time cut from 2 days to 0. Conversion rate improved 23% through systematic testing.",
        "result_stat": "23% improvement in conversion rate",
        "services": ["tracking", "optimization"],
    },
    {
        "id": "content_creator",
        "client": "Content Creator Collective",
        "challenge": "5 creators producing content with no shared system. Assets duplicated, channels inconsistent, no performance visibility.",
        "solution": "Shared content library with role-based access. Cross-channel scheduling pipeline. Per-creator performance dashboards.",
        "result": "3x content output with same headcount. Clear attribution of revenue to individual creators.",
        "result_stat": "3x content output with same headcount",
        "services": ["dam", "delivery", "tracking"],
    },
]

# ── Helper lookups ────────────────────────────────────────────────────────────
def get_pain_point(pain_point_id: str) -> dict:
    """Return a pain point dict by id, or the first one if not found."""
    for pp in PAIN_POINTS:
        if pp["id"] == pain_point_id:
            return pp
    return PAIN_POINTS[0]


def get_service(service_id: str) -> dict:
    """Return a service dict by id, or the 'dam' service if not found."""
    return SERVICES.get(service_id, SERVICES["dam"])


def get_case_study(case_study_id: str) -> dict:
    """Return a case study dict by id, or the first one if not found."""
    for cs in CASE_STUDIES:
        if cs["id"] == case_study_id:
            return cs
    return CASE_STUDIES[0]


def services_for_pain_point(pain_point_id: str) -> list[dict]:
    """Return all services that address the given pain point."""
    return [
        SERVICES[sid] for sid, svc in SERVICES.items()
        if pain_point_id in svc["keywords"]
    ]


def case_studies_for_service(service_id: str) -> list[dict]:
    """Return all case studies that involve the given service."""
    return [cs for cs in CASE_STUDIES if service_id in cs["services"]]