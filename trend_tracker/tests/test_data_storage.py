"""
Tests for trend_tracker.data_storage
"""

import csv
import json
import os
import tempfile
import unittest
from pathlib import Path

from trend_tracker.data_storage import (
    load_records,
    save_to_csv,
    save_to_json,
    save_records,
    _normalise_record,
    _CSV_FIELDNAMES,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_YT_RECORD = {
    "fetched_at": "2024-01-15T08:00:00+00:00",
    "source": "youtube",
    "topic": "fitness",
    "video_id": "abc123",
    "title": "Best Fitness Shorts 2024",
    "channel": "FitnessChannel",
    "url": "https://www.youtube.com/shorts/abc123",
    "published_at": "2024-01-14T10:00:00Z",
    "view_count": 150000,
    "like_count": 8500,
    "comment_count": 420,
    "thumbnail": "https://img.youtube.com/vi/abc123/hqdefault.jpg",
}

SAMPLE_IG_RECORD = {
    "fetched_at": "2024-01-15T08:00:00+00:00",
    "source": "instagram_graph_api",
    "topic": "travel",
    "reel_id": "18023456789",
    "url": "https://www.instagram.com/reel/abc/",
    "published_at": "2024-01-15T12:00:00+0000",
    "view_count": 0,
    "like_count": 12000,
    "comment_count": 350,
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestNormaliseRecord(unittest.TestCase):
    def test_fills_missing_fields_with_empty_string(self):
        partial = {"topic": "fitness", "source": "youtube"}
        result = _normalise_record(partial)
        for field in _CSV_FIELDNAMES:
            self.assertIn(field, result)
        self.assertEqual(result["video_id"], "")

    def test_preserves_existing_values(self):
        result = _normalise_record(SAMPLE_YT_RECORD)
        self.assertEqual(result["topic"], "fitness")
        self.assertEqual(result["view_count"], 150000)


class TestSaveToCSV(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_creates_csv_with_header(self):
        path = save_to_csv(
            [SAMPLE_YT_RECORD], data_dir=Path(self.tmpdir), date_str="2024-01-15"
        )
        self.assertTrue(path.exists())
        with path.open() as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["topic"], "fitness")
        self.assertEqual(rows[0]["source"], "youtube")

    def test_appends_to_existing_file(self):
        # First save
        save_to_csv(
            [SAMPLE_YT_RECORD], data_dir=Path(self.tmpdir), date_str="2024-01-15"
        )
        # Second save – should append
        path = save_to_csv(
            [SAMPLE_IG_RECORD], data_dir=Path(self.tmpdir), date_str="2024-01-15"
        )
        with path.open() as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(len(rows), 2)

    def test_creates_data_dir_if_missing(self):
        nested_dir = Path(self.tmpdir) / "nested" / "subdir"
        path = save_to_csv([SAMPLE_YT_RECORD], data_dir=nested_dir, date_str="2024-01-15")
        self.assertTrue(path.exists())


class TestSaveToJSON(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_creates_json_file(self):
        path = save_to_json(
            [SAMPLE_YT_RECORD], data_dir=Path(self.tmpdir), date_str="2024-01-15"
        )
        self.assertTrue(path.exists())
        with path.open() as fh:
            data = json.load(fh)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["topic"], "fitness")

    def test_appends_to_existing_json(self):
        save_to_json(
            [SAMPLE_YT_RECORD], data_dir=Path(self.tmpdir), date_str="2024-01-15"
        )
        path = save_to_json(
            [SAMPLE_IG_RECORD], data_dir=Path(self.tmpdir), date_str="2024-01-15"
        )
        with path.open() as fh:
            data = json.load(fh)
        self.assertEqual(len(data), 2)


class TestSaveRecords(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_defaults_to_csv(self):
        from unittest.mock import patch
        with patch("trend_tracker.data_storage.config") as mock_config:
            mock_config.STORAGE_FORMAT = "csv"
            mock_config.DATA_DIR = Path(self.tmpdir)
            path = save_records(
                [SAMPLE_YT_RECORD], data_dir=Path(self.tmpdir), date_str="2024-01-15"
            )
        self.assertTrue(str(path).endswith(".csv"))

    def test_json_format_when_configured(self):
        from unittest.mock import patch
        with patch("trend_tracker.data_storage.config") as mock_config:
            mock_config.STORAGE_FORMAT = "json"
            mock_config.DATA_DIR = Path(self.tmpdir)
            path = save_records(
                [SAMPLE_YT_RECORD], data_dir=Path(self.tmpdir), date_str="2024-01-15"
            )
        self.assertTrue(str(path).endswith(".json"))


class TestLoadRecords(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_load_csv_records(self):
        save_to_csv(
            [SAMPLE_YT_RECORD], data_dir=Path(self.tmpdir), date_str="2024-01-15"
        )
        loaded = load_records(data_dir=Path(self.tmpdir), date_str="2024-01-15")
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["topic"], "fitness")

    def test_load_json_records(self):
        save_to_json(
            [SAMPLE_YT_RECORD], data_dir=Path(self.tmpdir), date_str="2024-01-15"
        )
        loaded = load_records(data_dir=Path(self.tmpdir), date_str="2024-01-15")
        self.assertEqual(len(loaded), 1)

    def test_returns_empty_list_when_no_file(self):
        loaded = load_records(data_dir=Path(self.tmpdir), date_str="1999-01-01")
        self.assertEqual(loaded, [])


if __name__ == "__main__":
    unittest.main()
