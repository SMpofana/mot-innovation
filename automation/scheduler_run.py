#!/usr/bin/env python
"""
scheduler_run.py — M.O.T Innovation scheduled pipeline runner.

Runs the three automation pipelines in sequence, logging output to a
timestamped file under automation/logs/. Designed to be invoked by
Windows Task Scheduler (or cron) on a daily cadence.

Pipelines (in order):
  1. Content engine   — generate new scripts, voiceovers, videos, carousels
  2. Publishing       — sync to Sanity CMS + upload to YouTube/LinkedIn
  3. Business ops     — lead capture/scoring/nurturing/onboarding/reporting

Each step is optional via flags so you can schedule them independently:
    python scheduler_run.py                 # all three
    python scheduler_run.py --content-only
    python scheduler_run.py --publish-only
    python scheduler_run.py --ops-only
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PYTHON = sys.executable
LOG_DIR = SCRIPT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def _run(name: str, script: Path, args: list[str] | None = None) -> bool:
    """Run one pipeline, streaming output to the log. Returns success."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'=' * 60}\n  ▶ {name}  ({stamp})\n{'=' * 60}\n", flush=True)
    cmd = [PYTHON, str(script)] + (args or [])
    # Force UTF-8 so box-drawing/emoji output survives the Windows ANSI
    # codepage (cp1252) that Task Scheduler uses by default.
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        result = subprocess.run(
            cmd, cwd=str(SCRIPT_DIR), capture_output=True, text=True,
            encoding="utf-8", errors="replace", env=env,
        )
        out = result.stdout + result.stderr
        print(out, flush=True)
        ok = result.returncode == 0
        print(f"\n  {'✅' if ok else '❌'} {name} exit={result.returncode}\n", flush=True)
        return ok
    except Exception as e:  # noqa: BLE001
        print(f"\n  ❌ {name} failed to launch: {e}\n", flush=True)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="M.O.T Innovation scheduled runner")
    parser.add_argument("--content-only", action="store_true", help="Only run content engine")
    parser.add_argument("--publish-only", action="store_true", help="Only run publishing")
    parser.add_argument("--ops-only", action="store_true", help="Only run business ops (run_all)")
    args = parser.parse_args()

    only = args.content_only or args.publish_only or args.ops_only

    # Reconfigure our own stdout/stderr to UTF-8 so the Tee can write the
    # box-drawing/emoji output even when Task Scheduler runs us under cp1252.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    log_file = LOG_DIR / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    tee = open(log_file, "w", encoding="utf-8")
    orig_stdout, orig_stderr = sys.stdout, sys.stderr
    sys.stdout = _Tee(orig_stdout, tee)
    sys.stderr = _Tee(orig_stderr, tee)

    results: dict[str, bool] = {}

    if not only or args.content_only:
        results["content_engine"] = _run(
            "Content Engine",
            SCRIPT_DIR / "content_engine" / "run_content_engine.py",
        )

    if not only or args.publish_only:
        results["publishing"] = _run(
            "Publishing (Sanity + YouTube + LinkedIn)",
            SCRIPT_DIR / "publishing" / "run_publishing.py",
        )

    if not only or args.ops_only:
        results["business_ops"] = _run(
            "Business Ops (lead capture/scoring/nurturing/onboarding/reporting)",
            SCRIPT_DIR / "run_all.py",
        )

    sys.stdout, sys.stderr = orig_stdout, orig_stderr
    tee.close()

    print(f"\nLog written to: {log_file}")
    for name, ok in results.items():
        print(f"  {'✅' if ok else '❌'}  {name}")
    return 0 if all(results.values()) else 1


class _Tee:
    """Duplicate writes to both the original stream and the log file."""

    def __init__(self, stream, file):
        self.stream = stream
        self.file = file

    def write(self, data):
        self.stream.write(data)
        self.file.write(data)
        return len(data)

    def flush(self):
        self.stream.flush()
        self.file.flush()


if __name__ == "__main__":
    sys.exit(main())
