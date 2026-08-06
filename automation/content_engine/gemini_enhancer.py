#!/usr/bin/env python
"""
gemini_enhancer.py — AI-powered script enhancement using Google Gemini API

Upgrades template-based content engine scripts with AI-generated hooks,
problem agitation, and solution copy. Uses the free tier Gemini API.

Models (in priority order):
    gemini-flash-lite-latest  (free, fast, good quality)
    gemini-2.0-flash-lite    (alternative)
    gemini-flash-latest      (free, higher quality)

Free tier limits:
    15 requests/minute, 1,500 requests/day

Usage:
    from gemini_enhancer import enhance_script
    enhanced = enhance_script(pain_point, service, script_sections)
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# Load environment
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env.local"
if not ENV_PATH.exists():
    ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Model priority — first one that works
MODELS = [
    "gemini-flash-lite-latest",
    "gemini-2.0-flash-lite",
    "gemini-flash-latest",
    "gemini-2.0-flash",
]

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"


def _call_gemini(prompt: str, max_tokens: int = 300, temperature: float = 0.7) -> str | None:
    """Call Gemini API and return generated text, or None on failure."""
    if not GEMINI_API_KEY:
        return None

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }

    for model in MODELS:
        url = API_URL.format(model=model, key=GEMINI_API_KEY)
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if "candidates" in data:
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return text.strip()
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in body:
                # Rate limited, try next model
                continue
            # Other error, try next model
            continue
        except Exception:
            continue

    return None


def enhance_hook(pain_point_title: str, pain_point_stat: str) -> str | None:
    """Generate an AI-powered hook (first 5 seconds of a YouTube Short)."""
    prompt = f"""You are writing a YouTube Short hook for a marketing infrastructure company called M.O.T Innovation.

PAIN POINT: {pain_point_title}
STAT: {pain_point_stat}

Write ONE sentence (5 seconds spoken) that aggressively states the problem.
Direct, no fluff, speaks to frustrated business owners.
Do not use quotes, do not explain — just the hook sentence."""

    return _call_gemini(prompt, max_tokens=60, temperature=0.8)


def enhance_problem(pain_point_title: str, pain_point_stat: str, pain_point_summary: str) -> str | None:
    """Generate AI-powered problem agitation (5-15 seconds)."""
    prompt = f"""You are writing a YouTube Short problem agitation section.

PAIN POINT: {pain_point_title}
STAT: {pain_point_stat}
SUMMARY: {pain_point_summary}

Write 2-3 sentences (10 seconds spoken) that agitate the pain.
Include the stat naturally. Make the viewer feel the cost of inaction.
Direct, professional, no fluff."""

    return _call_gemini(prompt, max_tokens=120, temperature=0.7)


def enhance_solution(service_name: str, service_description: str, service_angle: str,
                     case_study_text: str) -> str | None:
    """Generate AI-powered solution section (15-45 seconds)."""
    prompt = f"""You are writing a YouTube Short solution section for M.O.T Innovation.

SERVICE: {service_name}
DESCRIPTION: {service_description}
ANGLE: {service_angle}
CASE STUDY: {case_study_text}

Write 4-5 sentences (30 seconds spoken) explaining how M.O.T Innovation solves the problem.
Mention the service name, what it does, and the case study result.
Professional, direct, benefit-focused. No fluff."""

    return _call_gemini(prompt, max_tokens=200, temperature=0.7)


def enhance_linkedin_post(pain_point_title: str, pain_point_stat: str,
                          service_name: str, service_angle: str,
                          case_study_text: str) -> str | None:
    """Generate an AI-powered LinkedIn post."""
    prompt = f"""Write a LinkedIn post for M.O.T Innovation, a marketing infrastructure company.

PAIN POINT: {pain_point_title}
STAT: {pain_point_stat}
SERVICE: {service_name}
ANGLE: {service_angle}
CASE STUDY: {case_study_text}

Rules:
- Start with a bold hook (no "Hey LinkedIn!")
- 100-150 words maximum
- Use line breaks for readability
- End with a CTA: "Book a free consultation at motinnovation.co.za"
- Professional but direct tone
- No hashtags in the body (they'll be added separately)
- No emojis"""

    return _call_gemini(prompt, max_tokens=250, temperature=0.7)


def check_api() -> bool:
    """Check if the Gemini API key is available and working."""
    if not GEMINI_API_KEY:
        return False
    result = _call_gemini("Say 'OK' if you can hear me.", max_tokens=10)
    return result is not None


if __name__ == "__main__":
    # Quick test
    print("=== Gemini API Enhancer Test ===")
    print(f"API Key: {'Found' if GEMINI_API_KEY else 'Missing'}")

    if check_api():
        print("API Status: Working")

        # Test hook generation
        hook = enhance_hook(
            "Disconnected marketing tools",
            "12+ tools. Fewer than half connected."
        )
        print(f"\nGenerated Hook: {hook}")

        # Test LinkedIn post
        post = enhance_linkedin_post(
            "Disconnected marketing tools",
            "12+ tools. Fewer than half connected.",
            "Digital Marketing Infrastructure",
            "We don't consult — we build the infrastructure.",
            "Like E-commerce Brand: 80% reduction in time-to-publish."
        )
        print(f"\nGenerated LinkedIn Post:\n{post}")
    else:
        print("API Status: Not available (will fall back to templates)")