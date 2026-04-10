"""
Scheduler module.

Wraps the ``schedule`` library to provide simple daily/weekly job scheduling.
This module is intentionally lightweight so it can be replaced by a cron job,
Make.com webhook trigger, or any other orchestration tool.
"""

import logging
import time
from typing import Callable

import schedule

from .config import config

logger = logging.getLogger(__name__)


def _schedule_job(job: Callable, run_schedule: str, run_time: str) -> None:
    """Register *job* with the ``schedule`` library."""
    if run_schedule == "weekly":
        schedule.every().monday.at(run_time).do(job)
        logger.info("Scheduler: job registered every Monday at %s", run_time)
    else:
        # default: daily
        schedule.every().day.at(run_time).do(job)
        logger.info("Scheduler: job registered daily at %s", run_time)


def run_scheduler(job: Callable) -> None:
    """
    Start the blocking scheduler loop.

    Registers *job* according to the schedule in ``config`` and runs it
    at the configured time every day (or every week).

    Args:
        job: A zero-argument callable to invoke on each scheduled run.
    """
    config.validate()
    config.ensure_dirs()

    _schedule_job(job, config.RUN_SCHEDULE, config.RUN_TIME)

    logger.info(
        "Scheduler started. Next run: %s",
        schedule.next_run(),
    )

    while True:
        schedule.run_pending()
        time.sleep(30)
