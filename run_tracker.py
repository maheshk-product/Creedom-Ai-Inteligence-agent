"""
Main runner for the Trend Intelligence System.

Usage
-----
Run once immediately:
    python run_tracker.py --run-now

Start the scheduled daemon (runs at the time set in .env):
    python run_tracker.py --schedule

Print today's report to stdout:
    python run_tracker.py --report
"""

import argparse
import logging
import sys
from pathlib import Path

from trend_tracker.config import config
from trend_tracker.data_storage import save_records
from trend_tracker.instagram_tracker import fetch_trending_reels
from trend_tracker.report_generator import generate_report
from trend_tracker.youtube_tracker import fetch_trending_shorts


def _configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


def collect_and_save() -> None:
    """Fetch trend data from all sources and persist to disk."""
    config.validate()
    config.ensure_dirs()

    logger = logging.getLogger(__name__)
    logger.info("Starting trend collection for topics: %s", config.TRENDING_TOPICS)

    records = []

    # --- YouTube Shorts ---
    yt_records = fetch_trending_shorts()
    logger.info("YouTube Shorts: collected %d records", len(yt_records))
    records.extend(yt_records)

    # --- Instagram Reels ---
    ig_records = fetch_trending_reels()
    logger.info("Instagram Reels: collected %d records", len(ig_records))
    records.extend(ig_records)

    if records:
        path = save_records(records)
        logger.info("All records saved to: %s", path)
    else:
        logger.warning(
            "No records collected. Check your API credentials in .env."
        )


def run_full_pipeline() -> None:
    """Collect data and immediately generate today's report."""
    collect_and_save()
    report_path = generate_report()
    print(f"\n✅ Report generated: {report_path}\n")
    print(report_path.read_text(encoding="utf-8"))


def main() -> None:
    _configure_logging()

    parser = argparse.ArgumentParser(
        description="Trend Intelligence System – YouTube Shorts & Instagram Reels"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--run-now",
        action="store_true",
        help="Run a single collection cycle and generate a report, then exit.",
    )
    group.add_argument(
        "--schedule",
        action="store_true",
        help="Start the scheduler daemon (blocks indefinitely).",
    )
    group.add_argument(
        "--report",
        action="store_true",
        help="Generate and print today's report without collecting new data.",
    )

    args = parser.parse_args()

    if args.run_now:
        run_full_pipeline()
    elif args.report:
        report_path = generate_report()
        print(report_path.read_text(encoding="utf-8"))
    elif args.schedule:
        # Import here to avoid importing schedule when not needed
        from trend_tracker.scheduler import run_scheduler
        run_scheduler(run_full_pipeline)


if __name__ == "__main__":
    main()
