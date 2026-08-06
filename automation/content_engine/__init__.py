"""
M.O.T Innovation — Content Engine Package

Automated faceless content pipeline for YouTube Shorts, LinkedIn posts,
carousels, voiceovers, storyboards, and content calendars.

Modules:
    script_generator      — PAS-formula scripts (YouTube Short + LinkedIn)
    voiceover_generator   — TTS audio (ElevenLabs or edge-tts fallback)
    video_storyboard      — Scene timings, visual cues, CapCut instructions
    linkedin_carousel     — 6-slide carousel JSON + Canva spec + PDF-ready MD
    content_calendar      — 30-day calendar CSV with weekly rotation
    run_content_engine    — Master runner orchestrating the full pipeline

Usage:
    # Run the full pipeline
    python -m content_engine.run_content_engine

    # Or run individual modules
    python script_generator.py --pain-point "Disconnected tools" --service dam
    python voiceover_generator.py --script scripts/my_script.md
    python video_storyboard.py --script scripts/my_script.md
    python linkedin_carousel.py --pain-point "Disconnected tools" --service dam
    python content_calendar.py --output calendar.csv
"""