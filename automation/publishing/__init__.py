"""
M.O.T Innovation — Publishing Package

Automated publishing pipeline for YouTube, LinkedIn, and Sanity CMS.

Modules:
    youtube_upload   — YouTube Data API v3 video uploads (OAuth2)
    linkedin_post     — LinkedIn posting via Make.com webhook fallback
    run_publishing    — Master publishing pipeline runner

Usage:
    # Run the full publishing pipeline
    python -m publishing.run_publishing

    # Upload a single video to YouTube
    python youtube_upload.py --video path/to/video.mp4 --title "My Title"

    # Send a LinkedIn post via Make.com webhook
    python linkedin_post.py --webhook-url https://hook.us1.make.com/... --text "Post text"
"""