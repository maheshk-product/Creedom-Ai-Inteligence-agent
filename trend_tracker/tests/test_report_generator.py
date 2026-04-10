"""
Tests for trend_tracker.report_generator
"""

import tempfile
import unittest
from pathlib import Path

from trend_tracker.data_storage import save_to_csv, save_to_json
from trend_tracker.report_generator import (
    _aggregate_by_topic,
    _format_number,
    _top_items,
    generate_report,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_RECORDS = [
    {
        "fetched_at": "2024-01-15T08:00:00+00:00",
        "source": "youtube",
        "topic": "fitness",
        "video_id": "abc123",
        "title": "Best Fitness Shorts 2024",
        "url": "https://www.youtube.com/shorts/abc123",
        "view_count": 150000,
        "like_count": 8500,
        "comment_count": 420,
    },
    {
        "fetched_at": "2024-01-15T08:00:00+00:00",
        "source": "youtube",
        "topic": "fitness",
        "video_id": "def456",
        "title": "Quick Workout Short",
        "url": "https://www.youtube.com/shorts/def456",
        "view_count": 75000,
        "like_count": 3200,
        "comment_count": 180,
    },
    {
        "fetched_at": "2024-01-15T08:00:00+00:00",
        "source": "instagram_graph_api",
        "topic": "travel",
        "reel_id": "18023456789",
        "title": "",
        "url": "https://www.instagram.com/reel/abc/",
        "view_count": 0,
        "like_count": 12000,
        "comment_count": 350,
    },
]


# ---------------------------------------------------------------------------
# Unit tests for helpers
# ---------------------------------------------------------------------------

class TestFormatNumber(unittest.TestCase):
    def test_formats_millions(self):
        self.assertEqual(_format_number(2_500_000), "2.5M")

    def test_formats_thousands(self):
        self.assertEqual(_format_number(8500), "8.5K")

    def test_formats_small_numbers(self):
        self.assertEqual(_format_number(420), "420")

    def test_zero(self):
        self.assertEqual(_format_number(0), "0")


class TestAggregateByTopic(unittest.TestCase):
    def test_groups_by_topic(self):
        summary = _aggregate_by_topic(SAMPLE_RECORDS)
        self.assertIn("fitness", summary)
        self.assertIn("travel", summary)

    def test_aggregates_counts(self):
        summary = _aggregate_by_topic(SAMPLE_RECORDS)
        self.assertEqual(summary["fitness"]["count"], 2)
        self.assertEqual(summary["fitness"]["total_views"], 225000)
        self.assertEqual(summary["fitness"]["total_likes"], 11700)

    def test_empty_input(self):
        summary = _aggregate_by_topic([])
        self.assertEqual(summary, {})


class TestTopItems(unittest.TestCase):
    def test_returns_top_n_by_engagement(self):
        items = [
            {"view_count": 100, "like_count": 50},
            {"view_count": 500, "like_count": 200},
            {"view_count": 10, "like_count": 5},
        ]
        top = _top_items(items, n=2)
        self.assertEqual(len(top), 2)
        self.assertEqual(top[0]["view_count"], 500)

    def test_handles_fewer_items_than_n(self):
        items = [{"view_count": 100, "like_count": 10}]
        top = _top_items(items, n=5)
        self.assertEqual(len(top), 1)


# ---------------------------------------------------------------------------
# Integration tests for report generation
# ---------------------------------------------------------------------------

class TestGenerateReport(unittest.TestCase):
    def setUp(self):
        self.data_dir = Path(tempfile.mkdtemp())
        self.report_dir = Path(tempfile.mkdtemp())

    def test_generates_markdown_report_from_csv(self):
        save_to_csv(SAMPLE_RECORDS, data_dir=self.data_dir, date_str="2024-01-15")
        report_path = generate_report(
            date_str="2024-01-15",
            data_dir=self.data_dir,
            report_dir=self.report_dir,
        )
        self.assertTrue(report_path.exists())
        content = report_path.read_text(encoding="utf-8")
        self.assertIn("Trend Intelligence Report", content)
        self.assertIn("#fitness", content)
        self.assertIn("#travel", content)

    def test_generates_markdown_report_from_json(self):
        save_to_json(SAMPLE_RECORDS, data_dir=self.data_dir, date_str="2024-01-15")
        report_path = generate_report(
            date_str="2024-01-15",
            data_dir=self.data_dir,
            report_dir=self.report_dir,
        )
        content = report_path.read_text(encoding="utf-8")
        self.assertIn("#fitness", content)

    def test_report_for_empty_data(self):
        report_path = generate_report(
            date_str="1999-01-01",
            data_dir=self.data_dir,
            report_dir=self.report_dir,
        )
        content = report_path.read_text(encoding="utf-8")
        self.assertIn("No trend data available", content)

    def test_report_contains_engagement_metrics(self):
        save_to_csv(SAMPLE_RECORDS, data_dir=self.data_dir, date_str="2024-01-15")
        report_path = generate_report(
            date_str="2024-01-15",
            data_dir=self.data_dir,
            report_dir=self.report_dir,
        )
        content = report_path.read_text(encoding="utf-8")
        # fitness total views = 225K
        self.assertIn("225.0K", content)

    def test_report_file_naming(self):
        report_path = generate_report(
            date_str="2024-01-15",
            data_dir=self.data_dir,
            report_dir=self.report_dir,
        )
        self.assertEqual(report_path.name, "report_2024-01-15.md")


if __name__ == "__main__":
    unittest.main()
