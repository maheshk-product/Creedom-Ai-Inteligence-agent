"""
Data Storage Module.

Persists collected trend records to CSV or JSON files on disk.
Each run appends to a date-partitioned file so history is preserved.
"""

import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import config

logger = logging.getLogger(__name__)

# Canonical field order for CSV output
_CSV_FIELDNAMES = [
    "fetched_at",
    "source",
    "topic",
    "video_id",
    "reel_id",
    "title",
    "channel",
    "url",
    "published_at",
    "view_count",
    "like_count",
    "comment_count",
    "thumbnail",
]


def _today_str() -> str:
    """Return today's date as a YYYY-MM-DD string (UTC)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _normalise_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure every CSV field exists in the record (fill missing with empty)."""
    return {field: record.get(field, "") for field in _CSV_FIELDNAMES}


def save_to_csv(
    records: List[Dict[str, Any]],
    data_dir: Optional[Path] = None,
    date_str: Optional[str] = None,
) -> Path:
    """
    Append *records* to a date-partitioned CSV file.

    Args:
        records:  List of trend dicts (from YouTube or Instagram trackers).
        data_dir: Directory to write into. Defaults to ``config.DATA_DIR``.
        date_str: Date suffix for the filename (YYYY-MM-DD). Defaults to today.

    Returns:
        Path to the CSV file that was written.
    """
    if data_dir is None:
        data_dir = config.DATA_DIR
    if date_str is None:
        date_str = _today_str()

    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    filepath = data_dir / f"trends_{date_str}.csv"

    file_exists = filepath.exists()

    with filepath.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_CSV_FIELDNAMES, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        for record in records:
            writer.writerow(_normalise_record(record))

    logger.info("Saved %d records to %s", len(records), filepath)
    return filepath


def save_to_json(
    records: List[Dict[str, Any]],
    data_dir: Optional[Path] = None,
    date_str: Optional[str] = None,
) -> Path:
    """
    Save *records* to a date-partitioned JSON file (list of objects).

    If the file already exists for today, new records are appended to it.

    Args:
        records:  List of trend dicts.
        data_dir: Directory to write into. Defaults to ``config.DATA_DIR``.
        date_str: Date suffix (YYYY-MM-DD). Defaults to today.

    Returns:
        Path to the JSON file that was written.
    """
    if data_dir is None:
        data_dir = config.DATA_DIR
    if date_str is None:
        date_str = _today_str()

    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    filepath = data_dir / f"trends_{date_str}.json"

    existing: List[Dict[str, Any]] = []
    if filepath.exists():
        try:
            with filepath.open("r", encoding="utf-8") as fh:
                existing = json.load(fh)
        except (json.JSONDecodeError, OSError):
            existing = []

    existing.extend(records)

    with filepath.open("w", encoding="utf-8") as fh:
        json.dump(existing, fh, indent=2, ensure_ascii=False)

    logger.info("Saved %d records to %s", len(records), filepath)
    return filepath


def save_records(
    records: List[Dict[str, Any]],
    data_dir: Optional[Path] = None,
    date_str: Optional[str] = None,
) -> Path:
    """
    Save records using the format configured in ``config.STORAGE_FORMAT``.

    Args:
        records:  List of trend dicts to persist.
        data_dir: Target directory. Defaults to ``config.DATA_DIR``.
        date_str: Date suffix for filename. Defaults to today.

    Returns:
        Path to the file that was written.
    """
    if config.STORAGE_FORMAT == "json":
        return save_to_json(records, data_dir=data_dir, date_str=date_str)
    return save_to_csv(records, data_dir=data_dir, date_str=date_str)


def load_records(
    data_dir: Optional[Path] = None,
    date_str: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Load trend records from disk for the given date.

    Supports both CSV and JSON files; tries CSV first.

    Args:
        data_dir: Directory to read from. Defaults to ``config.DATA_DIR``.
        date_str: Date suffix (YYYY-MM-DD). Defaults to today.

    Returns:
        List of trend record dicts. Empty list if no file exists.
    """
    if data_dir is None:
        data_dir = config.DATA_DIR
    if date_str is None:
        date_str = _today_str()

    data_dir = Path(data_dir)

    for ext, loader in [("csv", _load_csv), ("json", _load_json)]:
        filepath = data_dir / f"trends_{date_str}.{ext}"
        if filepath.exists():
            return loader(filepath)

    logger.warning("No trend data found for %s in %s", date_str, data_dir)
    return []


def _load_csv(filepath: Path) -> List[Dict[str, Any]]:
    with filepath.open("r", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _load_json(filepath: Path) -> List[Dict[str, Any]]:
    with filepath.open("r", encoding="utf-8") as fh:
        return json.load(fh)
