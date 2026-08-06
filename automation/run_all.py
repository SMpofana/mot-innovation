#!/usr/bin/env python
"""
Master Runner — M.O.T Innovation Automation Pipelines

Executes all automation pipelines in sequence:
1. Lead Capture (demo mode — captures a sample lead)
2. Lead Scoring (ranks all leads)
3. Lead Nurturing (generates due email sequence)
4. Client Onboarding (demo mode — onboards a sample client)
5. Reporting (generates weekly status report)
6. Content Pipeline (scans Reddit, generates posts, schedules calendar)

Usage:
    python run_all.py                  # Run all pipelines
    python run_all.py --skip-content   # Skip Reddit content pipeline (network-heavy)
    python run_all.py --skip-nurturing # Skip nurturing sequence
    python run_all.py --verbose        # Verbose output
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def run_pipeline(name: str, module_name: str, extra_args: list[str] = None) -> bool:
    """Run a single pipeline stage and return success status."""
    print(f"\n{'═' * 60}")
    print(f"  ▶  RUNNING: {name}")
    print(f"{'═' * 60}\n")

    start = time.time()
    try:
        # Import and run the module
        module = __import__(module_name)
        # Build sys.argv for the module
        old_argv = sys.argv
        argv = [module_name]
        if extra_args:
            argv.extend(extra_args)
        sys.argv = argv
        result = module.main()
        sys.argv = old_argv
        return result == 0
    except SystemExit as e:
        return e.code == 0
    except Exception as e:
        print(f"  ❌ ERROR in {name}: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        elapsed = time.time() - start
        print(f"\n  ⏱  {name} completed in {elapsed:.1f}s")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="M.O.T Innovation — Master Automation Runner"
    )
    parser.add_argument("--skip-content", action="store_true",
                        help="Skip content pipeline (Reddit scan — network heavy)")
    parser.add_argument("--skip-nurturing", action="store_true",
                        help="Skip lead nurturing")
    parser.add_argument("--skip-onboarding", action="store_true",
                        help="Skip client onboarding demo")
    parser.add_argument("--verbose", action="store_true",
                        help="Verbose output from all pipelines")
    args = parser.parse_args()

    # Add this script's directory to the path so imports work
    sys.path.insert(0, str(SCRIPT_DIR))

    print("╔" + "═" * 58 + "╗")
    print("║   M.O.T INNOVATION — AUTOMATION PIPELINES MASTER RUNNER   ║")
    print("║   Marketing Intelligence, Engineered.                    ║")
    print("╚" + "═" * 58 + "╝")

    total_start = time.time()
    results: dict[str, bool] = {}

    # 1. Lead Capture (demo mode)
    results["lead_capture"] = run_pipeline(
        "1. Lead Capture", "lead_capture",
        extra_args=(["--verbose"] if args.verbose else None)
    )

    # 2. Lead Scoring
    results["lead_scoring"] = run_pipeline(
        "2. Lead Scoring & Ranking", "lead_scoring",
        extra_args=(["--verbose"] if args.verbose else None)
    )

    # 3. Lead Nurturing
    if not args.skip_nurturing:
        results["lead_nurturing"] = run_pipeline(
            "3. Lead Nurturing Sequence", "lead_nurturing",
            extra_args=(["--verbose"] if args.verbose else None)
        )
    else:
        print("\n  ⏭  Skipping Lead Nurturing (--skip-nurturing)")

    # 4. Client Onboarding
    if not args.skip_onboarding:
        results["client_onboarding"] = run_pipeline(
            "4. Client Onboarding", "client_onboarding",
            extra_args=(["--verbose"] if args.verbose else None)
        )
    else:
        print("\n  ⏭  Skipping Client Onboarding (--skip-onboarding)")

    # 5. Reporting
    results["reporting"] = run_pipeline(
        "5. Reporting Automation", "reporting",
        extra_args=(["--verbose", "--period", "weekly"] if args.verbose else ["--period", "weekly"])
    )

    # 6. Content Pipeline
    if not args.skip_content:
        results["content_pipeline"] = run_pipeline(
            "6. Social Media Content Pipeline", "content_pipeline",
            extra_args=(["--verbose"] if args.verbose else None)
        )
    else:
        print("\n  ⏭  Skipping Content Pipeline (--skip-content)")

    # Summary
    total_elapsed = time.time() - total_start
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║              PIPELINE EXECUTION SUMMARY                   ║")
    print("╚" + "═" * 58 + "╝")
    print(f"\nTotal time: {total_elapsed:.1f}s\n")

    all_passed = True
    for name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {status}  {name}")
        if not success:
            all_passed = False

    passed = sum(1 for s in results.values() if s)
    print(f"\n  {passed}/{len(results)} pipelines completed successfully")
    print(f"  {'🎉 All pipelines passed!' if all_passed else '⚠️  Some pipelines failed — check logs above'}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())