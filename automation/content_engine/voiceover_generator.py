#!/usr/bin/env python
"""
voiceover_generator.py — M.O.T Innovation Voiceover Generator

Generates voiceover audio from script markdown files using:
    1. ElevenLabs free tier API (if ELEVENLABS_API_KEY env var is set)
    2. Fallback: edge-tts (free Microsoft Edge TTS, no API key needed)

Audio files are saved as MP3 in automation/content_engine/audio/.

Usage:
    # Generate voiceover from a script file
    python voiceover_generator.py --script scripts/yt_short_disconnected_tools_20250101_120000.md

    # Generate from raw text
    python voiceover_generator.py --text "Your marketing tools don't talk to each other..." --name custom_vo

    # Specify voice and speed
    python voiceover_generator.py --script scripts/my_script.md --voice en-US-AndrewNeural --rate "+10%"

    # List available edge-tts voices
    python voiceover_generator.py --list-voices
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

AUDIO_DIR = SCRIPT_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Default edge-tts voice (professional, neutral)
DEFAULT_VOICE = "en-US-AndrewNeural"
DEFAULT_RATE = "+0%"
DEFAULT_PITCH = "+0Hz"

# Alternative professional voices
VOICE_OPTIONS = {
    "male": "en-US-AndrewNeural",
    "female": "en-US-AvaNeural",
    "british_male": "en-GB-RyanNeural",
    "british_female": "en-GB-SoniaNeural",
    "south_african": "en-ZA-LiamNeural",
}


# ── Extract voiceover text from script markdown ──────────────────────────────
def extract_voiceover_text(md_content: str) -> str:
    """
    Extract the full voiceover text from a script markdown file.

    Looks for the '## Full Voiceover Text (for TTS)' section first.
    Falls back to extracting all voiceover blocks.
    """
    # Try the dedicated section first
    pattern = r"## Full Voiceover Text \(for TTS\)\s*\n+(.*?)(?:\n---|\Z)"
    match = re.search(pattern, md_content, re.DOTALL)
    if match:
        text = match.group(1).strip()
        # Remove visual cues and markdown formatting
        text = re.sub(r"\[VISUAL:.*?\]", "", text)
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        text = re.sub(r"```", "", text)
        # Clean up extra whitespace from removed tags
        text = re.sub(r"  +", " ", text)
        text = text.strip()
        if text:
            return text

    # Fall back to extracting all Voiceover blocks
    vo_blocks = re.findall(r"\*\*Voiceover:\*\*\s*\n```\s*\n(.*?)\n```", md_content, re.DOTALL)
    if vo_blocks:
        text = " ".join(block.strip() for block in vo_blocks)
        text = re.sub(r"\[VISUAL:.*?\]", "", text)
        return text.strip()

    # Last resort: extract everything that isn't a visual cue or metadata
    lines = md_content.split("\n")
    text_lines = []
    skip = False
    for line in lines:
        if line.startswith("## Metadata") or line.startswith("---"):
            skip = True
            continue
        if line.startswith("## "):
            skip = False
            continue
        if skip:
            continue
        if line.startswith("```") or line.startswith("**") or line.startswith("[VISUAL"):
            continue
        if line.strip():
            text_lines.append(line.strip())

    return " ".join(text_lines).strip()


# ── ElevenLabs API ────────────────────────────────────────────────────────────
def generate_with_elevenlabs(text: str, output_path: Path, api_key: str) -> bool:
    """
    Generate voiceover using ElevenLabs API.

    Uses the REST API directly (no SDK needed).
    Free tier: 10,000 chars/month.
    """
    try:
        import urllib.request
        import urllib.error

        # Trim text to free tier limit (10k chars per month, ~2k per request safe)
        if len(text) > 2500:
            text = text[:2500]
            print(f"   ⚠️  Text trimmed to 2500 chars (ElevenLabs free tier conservation)")

        voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel — default professional female
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        payload = json.dumps({
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            },
        }).encode("utf-8")

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key,
        }

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

        print("   🎙️  Calling ElevenLabs API...")
        with urllib.request.urlopen(req, timeout=60) as response:
            if response.status == 200:
                with open(output_path, "wb") as f:
                    f.write(response.read())
                print(f"   ✅ ElevenLabs voiceover saved: {output_path}")
                return True
            else:
                print(f"   ❌ ElevenLabs API error: HTTP {response.status}")
                return False

    except urllib.error.HTTPError as e:
        print(f"   ❌ ElevenLabs API error: {e}")
        try:
            error_body = e.read().decode("utf-8")
            print(f"      {error_body[:200]}")
        except Exception:
            pass
        return False
    except Exception as e:
        print(f"   ❌ ElevenLabs error: {e}")
        return False


# ── edge-tts (free fallback) ──────────────────────────────────────────────────
async def _generate_with_edge_tts(text: str, output_path: Path, voice: str, rate: str, pitch: str) -> bool:
    """Generate voiceover using edge-tts (free, no API key)."""
    try:
        import edge_tts
    except ImportError:
        print("   ⚠️  edge-tts not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "edge-tts"])
        import edge_tts

    # Remove visual cues and markdown artifacts from text
    text = re.sub(r"\[VISUAL:.*?\]", "", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"```", "", text)
    text = text.strip()

    if not text:
        print("   ❌ No text to convert")
        return False

    print(f"   🎙️  Generating with edge-tts (voice: {voice}, rate: {rate})...")
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)

    try:
        await communicate.save(str(output_path))
        print(f"   ✅ edge-tts voiceover saved: {output_path}")
        return True
    except Exception as e:
        print(f"   ❌ edge-tts error: {e}")
        return False


def generate_with_edge_tts(text: str, output_path: Path, voice: str = DEFAULT_VOICE,
                            rate: str = DEFAULT_RATE, pitch: str = DEFAULT_PITCH) -> bool:
    """Synchronous wrapper for edge-tts generation."""
    return asyncio.run(_generate_with_edge_tts(text, output_path, voice, rate, pitch))


# ── Main generation logic ────────────────────────────────────────────────────
def generate_voiceover(text: str, output_name: str, voice: str = DEFAULT_VOICE,
                       rate: str = DEFAULT_RATE, pitch: str = DEFAULT_PITCH,
                       audio_dir: Path | None = None) -> str | None:
    """
    Generate a voiceover MP3 from text.

    Uses ElevenLabs if ELEVENLABS_API_KEY is set, otherwise falls back to edge-tts.

    Args:
        text: The voiceover text to convert.
        output_name: Name for the output file (without extension).
        voice: edge-tts voice name (ignored if ElevenLabs is used).
        rate: edge-tts speech rate adjustment.
        pitch: edge-tts pitch adjustment.
        audio_dir: Directory for audio files (default: audio/).

    Returns:
        Path to the generated MP3 file, or None if generation failed.
    """
    if audio_dir is None:
        audio_dir = AUDIO_DIR
    audio_dir.mkdir(parents=True, exist_ok=True)

    output_path = audio_dir / f"{output_name}.mp3"

    # Check for ElevenLabs key
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if elevenlabs_key:
        print(f"   🔑 ELEVENLABS_API_KEY found — using ElevenLabs")
        success = generate_with_elevenlabs(text, output_path, elevenlabs_key)
        if success:
            return str(output_path)
        print("   ⚠️  ElevenLabs failed, falling back to edge-tts...")
    else:
        print(f"   🔑 No ELEVENLABS_API_KEY — using edge-tts (free)")

    # Fallback to edge-tts
    success = generate_with_edge_tts(text, output_path, voice, rate, pitch)
    if success:
        return str(output_path)
    return None


def generate_from_script(script_path: Path, voice: str = DEFAULT_VOICE,
                         rate: str = DEFAULT_RATE, pitch: str = DEFAULT_PITCH,
                         audio_dir: Path | None = None) -> str | None:
    """
    Generate a voiceover from a script markdown file.

    Extracts the voiceover text and generates an MP3.
    The output filename is based on the script filename.
    """
    if not script_path.exists():
        print(f"   ❌ Script not found: {script_path}")
        return None

    md_content = script_path.read_text(encoding="utf-8")
    vo_text = extract_voiceover_text(md_content)

    if not vo_text:
        print(f"   ❌ No voiceover text found in {script_path}")
        return None

    print(f"   📄 Script: {script_path.name}")
    print(f"   📝 Voiceover text: {len(vo_text)} chars")
    print(f"   📝 Preview: \"{vo_text[:100]}...\"")

    output_name = script_path.stem  # filename without extension
    return generate_voiceover(vo_text, output_name, voice, rate, pitch, audio_dir)


# ── List voices ──────────────────────────────────────────────────────────────
async def list_voices() -> None:
    """List available edge-tts voices."""
    try:
        import edge_tts
    except ImportError:
        print("Installing edge-tts...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "edge-tts"])
        import edge_tts

    print("\nAvailable en-US and en-GB voices:")
    voices = await edge_tts.list_voices()
    for v in voices:
        if v["Locale"].startswith("en-"):
            print(f"  {v['ShortName']:30s}  {v['Gender']:8s}  {v['Locale']}")


# ── CLI ──────────────────────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(
        description="M.O.T Innovation — Voiceover Generator (ElevenLabs or edge-tts)"
    )
    parser.add_argument("--script", type=str, default=None,
                        help="Path to a script markdown file to generate voiceover from")
    parser.add_argument("--text", type=str, default=None,
                        help="Raw text to convert to voiceover")
    parser.add_argument("--name", type=str, default="voiceover",
                        help="Name for the output file (without extension)")
    parser.add_argument("--voice", type=str, default=DEFAULT_VOICE,
                        help=f"edge-tts voice (default: {DEFAULT_VOICE}). Use --list-voices to see options.")
    parser.add_argument("--rate", type=str, default=DEFAULT_RATE,
                        help=f"Speech rate (default: {DEFAULT_RATE}, e.g. '+10%' or '-5%')")
    parser.add_argument("--pitch", type=str, default=DEFAULT_PITCH,
                        help=f"Pitch adjustment (default: {DEFAULT_PITCH})")
    parser.add_argument("--audio-dir", type=str, default=None,
                        help="Output directory for audio files (default: audio/)")
    parser.add_argument("--list-voices", action="store_true",
                        help="List available edge-tts voices and exit")
    args = parser.parse_args()

    if args.list_voices:
        asyncio.run(list_voices())
        return 0

    print(f"\n{'=' * 60}")
    print(f"VOICEOVER GENERATOR — M.O.T Innovation")
    print(f"{'=' * 60}")

    audio_dir = Path(args.audio_dir) if args.audio_dir else AUDIO_DIR

    if args.script:
        result = generate_from_script(Path(args.script), args.voice, args.rate, args.pitch, audio_dir)
    elif args.text:
        print(f"   📝 Text: {len(args.text)} chars")
        result = generate_voiceover(args.text, args.name, args.voice, args.rate, args.pitch, audio_dir)
    else:
        print("Error: provide --script or --text, or use --list-voices.")
        return 1

    if result:
        print(f"\n✅ Voiceover generated: {result}")
        return 0
    else:
        print(f"\n❌ Voiceover generation failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())