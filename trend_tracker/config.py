"""
Configuration management for the Trend Intelligence System.

Reads settings from environment variables (via a .env file) and
exposes them as a single Config object used throughout the application.
"""

import os
import logging
from pathlib import Path
from typing import List

from dotenv import load_dotenv

# Load .env file from the project root (two levels up from this file)
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=False)


def _get_topics() -> List[str]:
    """Parse TRENDING_TOPICS env var into a clean list."""
    raw = os.getenv("TRENDING_TOPICS", "fitness,travel,cooking,technology")
    topics = [t.strip() for t in raw.split(",") if t.strip()]
    if not topics:
        topics = ["fitness", "travel", "cooking", "technology"]
    return topics[:4]  # cap at 4 topics to respect free-tier limits


class Config:
    """Central configuration object.  Access values via ``config.<attr>``."""

    # API credentials
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    INSTAGRAM_ACCESS_TOKEN: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    INSTAGRAM_USER_ID: str = os.getenv("INSTAGRAM_USER_ID", "")

    # Topics / hashtags
    TRENDING_TOPICS: List[str] = _get_topics()

    # Storage
    STORAGE_FORMAT: str = os.getenv("STORAGE_FORMAT", "csv").lower()
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", "data"))
    REPORT_DIR: Path = Path(os.getenv("REPORT_DIR", "reports"))

    # Reporting
    EMAIL_RECIPIENT: str = os.getenv("EMAIL_RECIPIENT", "")

    # Scheduling
    RUN_SCHEDULE: str = os.getenv("RUN_SCHEDULE", "daily").lower()
    RUN_TIME: str = os.getenv("RUN_TIME", "08:00")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

    # YouTube API settings
    YOUTUBE_MAX_RESULTS: int = 10       # results per topic per run
    YOUTUBE_API_BASE: str = "https://www.googleapis.com/youtube/v3"

    # Instagram API settings
    INSTAGRAM_API_BASE: str = "https://graph.instagram.com"

    @classmethod
    def validate(cls) -> None:
        """Log warnings about missing optional credentials."""
        logger = logging.getLogger(__name__)
        if not cls.YOUTUBE_API_KEY:
            logger.warning(
                "YOUTUBE_API_KEY is not set. YouTube tracking will be skipped."
            )
        if not cls.INSTAGRAM_ACCESS_TOKEN:
            logger.warning(
                "INSTAGRAM_ACCESS_TOKEN is not set. "
                "Instagram tracking will use public web fallback."
            )

    @classmethod
    def ensure_dirs(cls) -> None:
        """Create data and report directories if they do not exist."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.REPORT_DIR.mkdir(parents=True, exist_ok=True)


config = Config()
