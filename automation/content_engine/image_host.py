#!/usr/bin/env python
"""
image_host.py — Free image hosting for LinkedIn post images.

Uploads carousel slide PNGs to catbox.moe (free, no API key) and returns
the public URL, which Make.com can fetch to attach to a LinkedIn post.

Usage:
    python image_host.py --file carousels/rendered/slide1.png
    python image_host.py --carousel carousels/carousel_*.json   # upload slide 1 (cover)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import requests

SCRIPT_DIR = Path(__file__).resolve().parent
CAROUSEL_DIR = SCRIPT_DIR / "carousels"
RENDER_DIR = CAROUSEL_DIR / "rendered"

CATBOX_URL = "https://catbox.moe/user/api.php"


def upload_image(file_path: Path) -> str:
    """Upload an image to catbox.moe, return the public URL."""
    if not file_path.exists():
        raise FileNotFoundError(f"Image not found: {file_path}")
    with open(file_path, "rb") as f:
        files = {"reqtype": (None, "fileupload"), "fileToUpload": f}
        r = requests.post(CATBOX_URL, files=files, timeout=60)
    r.raise_for_status()
    url = r.text.strip()
    if not url.startswith("http"):
        raise RuntimeError(f"Unexpected catbox response: {url}")
    return url


def upload_carousel_cover(carousel_path: Path) -> str:
    """Upload the first (cover) slide of a carousel. Returns the public URL."""
    stem = carousel_path.stem
    cover = RENDER_DIR / f"{stem}_slide1.png"
    if not cover.exists():
        # Render it on the fly if not already rendered
        sys.path.insert(0, str(SCRIPT_DIR))
        from carousel_render import render_carousel
        render_carousel(carousel_path)
    return upload_image(cover)


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload carousel images to catbox.moe")
    parser.add_argument("--file", type=Path, help="Image file to upload")
    parser.add_argument("--carousel", type=Path, help="Carousel JSON (uploads slide 1 cover)")
    args = parser.parse_args()

    print("=" * 60)
    print("M.O.T INNOVATION — IMAGE HOSTING (catbox.moe)")
    print("=" * 60)

    try:
        if args.file:
            url = upload_image(args.file)
            print(f"✅ Uploaded: {url}")
        elif args.carousel:
            url = upload_carousel_cover(args.carousel)
            print(f"✅ Carousel cover: {url}")
        else:
            parser.print_help()
            return 1
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
