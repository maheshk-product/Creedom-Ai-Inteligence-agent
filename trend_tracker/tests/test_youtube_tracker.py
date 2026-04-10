"""
Tests for trend_tracker.youtube_tracker
"""

import json
import unittest
from unittest.mock import MagicMock, patch

import responses as resp_lib

from trend_tracker.youtube_tracker import (
    _build_search_url,
    _build_stats_url,
    _parse_search_results,
    fetch_trending_shorts,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SEARCH_RESPONSE = {
    "kind": "youtube#searchListResponse",
    "items": [
        {
            "kind": "youtube#searchResult",
            "id": {"kind": "youtube#video", "videoId": "abc123"},
            "snippet": {
                "publishedAt": "2024-01-15T10:00:00Z",
                "channelTitle": "FitnessChannel",
                "title": "Best Fitness Shorts 2024",
                "thumbnails": {
                    "high": {"url": "https://img.youtube.com/vi/abc123/hqdefault.jpg"}
                },
            },
        },
        {
            "kind": "youtube#searchResult",
            "id": {"kind": "youtube#video", "videoId": "def456"},
            "snippet": {
                "publishedAt": "2024-01-14T08:00:00Z",
                "channelTitle": "WorkoutHub",
                "title": "Quick Workout Short",
                "thumbnails": {
                    "high": {"url": "https://img.youtube.com/vi/def456/hqdefault.jpg"}
                },
            },
        },
    ],
}

STATS_RESPONSE = {
    "kind": "youtube#videoListResponse",
    "items": [
        {
            "id": "abc123",
            "statistics": {
                "viewCount": "150000",
                "likeCount": "8500",
                "commentCount": "420",
            },
        },
        {
            "id": "def456",
            "statistics": {
                "viewCount": "75000",
                "likeCount": "3200",
                "commentCount": "180",
            },
        },
    ],
}


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

class TestBuildUrls(unittest.TestCase):
    def test_search_url_contains_topic(self):
        url = _build_search_url("fitness")
        self.assertIn("fitness", url)
        self.assertIn("shorts", url)
        self.assertIn("videoDuration=short", url)

    def test_stats_url_contains_video_ids(self):
        url = _build_stats_url(["abc123", "def456"])
        self.assertIn("abc123", url)
        self.assertIn("def456", url)
        self.assertIn("statistics", url)


class TestParseSearchResults(unittest.TestCase):
    def test_parses_video_ids_and_titles(self):
        videos = _parse_search_results(SEARCH_RESPONSE, "fitness")
        self.assertEqual(len(videos), 2)
        self.assertEqual(videos[0]["video_id"], "abc123")
        self.assertEqual(videos[0]["title"], "Best Fitness Shorts 2024")
        self.assertEqual(videos[0]["topic"], "fitness")
        self.assertEqual(videos[0]["source"], "youtube")

    def test_generates_shorts_url(self):
        videos = _parse_search_results(SEARCH_RESPONSE, "fitness")
        self.assertIn("/shorts/abc123", videos[0]["url"])

    def test_empty_response(self):
        videos = _parse_search_results({"items": []}, "fitness")
        self.assertEqual(videos, [])

    def test_skips_missing_video_id(self):
        data = {"items": [{"kind": "youtube#searchResult", "id": {}, "snippet": {}}]}
        videos = _parse_search_results(data, "fitness")
        self.assertEqual(videos, [])


class TestFetchTrendingShorts(unittest.TestCase):
    @patch("trend_tracker.youtube_tracker.config")
    def test_returns_empty_without_api_key(self, mock_config):
        mock_config.YOUTUBE_API_KEY = ""
        mock_config.TRENDING_TOPICS = ["fitness"]
        result = fetch_trending_shorts(topics=["fitness"])
        self.assertEqual(result, [])

    @resp_lib.activate
    def test_fetch_returns_enriched_videos(self):
        """Integration-style test using mocked HTTP responses."""
        with patch("trend_tracker.youtube_tracker.config") as mock_config:
            mock_config.YOUTUBE_API_KEY = "fake_api_key"
            mock_config.YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
            mock_config.YOUTUBE_MAX_RESULTS = 10
            mock_config.TRENDING_TOPICS = ["fitness"]

            # Mock search endpoint
            resp_lib.add(
                resp_lib.GET,
                "https://www.googleapis.com/youtube/v3/search",
                json=SEARCH_RESPONSE,
                status=200,
            )
            # Mock statistics endpoint
            resp_lib.add(
                resp_lib.GET,
                "https://www.googleapis.com/youtube/v3/videos",
                json=STATS_RESPONSE,
                status=200,
            )

            import requests
            session = requests.Session()
            results = fetch_trending_shorts(topics=["fitness"], session=session)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["view_count"], 150000)
        self.assertEqual(results[0]["like_count"], 8500)
        self.assertEqual(results[1]["view_count"], 75000)

    @resp_lib.activate
    def test_handles_api_error_gracefully(self):
        with patch("trend_tracker.youtube_tracker.config") as mock_config:
            mock_config.YOUTUBE_API_KEY = "fake_api_key"
            mock_config.YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
            mock_config.YOUTUBE_MAX_RESULTS = 10
            mock_config.TRENDING_TOPICS = ["fitness"]

            resp_lib.add(
                resp_lib.GET,
                "https://www.googleapis.com/youtube/v3/search",
                status=403,
                json={"error": {"code": 403, "message": "forbidden"}},
            )

            import requests
            session = requests.Session()
            results = fetch_trending_shorts(topics=["fitness"], session=session)

        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
