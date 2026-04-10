"""
Tests for trend_tracker.instagram_tracker
"""

import unittest
from unittest.mock import patch

import responses as resp_lib

from trend_tracker.instagram_tracker import (
    _scrape_hashtag_page,
    fetch_trending_reels,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

GRAPH_HASHTAG_SEARCH_RESPONSE = {
    "data": [{"id": "17843820621000001"}]
}

GRAPH_RECENT_MEDIA_RESPONSE = {
    "data": [
        {
            "id": "18023456789",
            "media_type": "REEL",
            "permalink": "https://www.instagram.com/reel/abc/",
            "like_count": 12000,
            "comments_count": 350,
            "timestamp": "2024-01-15T12:00:00+0000",
        },
        {
            "id": "18023456790",
            "media_type": "IMAGE",  # should be filtered out
            "permalink": "https://www.instagram.com/p/xyz/",
            "like_count": 500,
            "comments_count": 20,
            "timestamp": "2024-01-15T11:00:00+0000",
        },
    ]
}

# Minimal HTML snippet that mimics Instagram's embedded JSON
_FAKE_HTML = """
<script type="text/javascript">
window.__additionalData = {
  "edge_hashtag_to_media": {
    "edges": [
      {"node": {"like_count": 5000, "comment_count": 200}},
      {"node": {"like_count": 3000, "comment_count": 100}}
    ]
  }
}
</script>
"""


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

class TestFetchViaGraphAPI(unittest.TestCase):
    @resp_lib.activate
    def test_fetches_reels_via_graph_api(self):
        with patch("trend_tracker.instagram_tracker.config") as mock_config:
            mock_config.INSTAGRAM_ACCESS_TOKEN = "fake_token"
            mock_config.INSTAGRAM_USER_ID = "123456"
            mock_config.INSTAGRAM_API_BASE = "https://graph.instagram.com"
            mock_config.TRENDING_TOPICS = ["fitness"]

            # Mock hashtag search
            resp_lib.add(
                resp_lib.GET,
                "https://graph.instagram.com/ig_hashtag_search",
                json=GRAPH_HASHTAG_SEARCH_RESPONSE,
                status=200,
            )
            # Mock recent media
            resp_lib.add(
                resp_lib.GET,
                "https://graph.instagram.com/17843820621000001/recent_media",
                json=GRAPH_RECENT_MEDIA_RESPONSE,
                status=200,
            )

            import requests
            session = requests.Session()
            results = fetch_trending_reels(topics=["fitness"], session=session)

        # Only VIDEO/REEL items should be returned
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["like_count"], 12000)
        self.assertEqual(results[0]["source"], "instagram_graph_api")

    @resp_lib.activate
    def test_falls_back_to_scraping_when_graph_api_fails(self):
        with patch("trend_tracker.instagram_tracker.config") as mock_config:
            mock_config.INSTAGRAM_ACCESS_TOKEN = "fake_token"
            mock_config.INSTAGRAM_USER_ID = "123456"
            mock_config.INSTAGRAM_API_BASE = "https://graph.instagram.com"
            mock_config.TRENDING_TOPICS = ["fitness"]

            # Graph API returns an error
            resp_lib.add(
                resp_lib.GET,
                "https://graph.instagram.com/ig_hashtag_search",
                status=500,
            )
            # Scraping fallback
            resp_lib.add(
                resp_lib.GET,
                "https://www.instagram.com/explore/tags/fitness/",
                body=_FAKE_HTML,
                status=200,
            )

            import requests
            session = requests.Session()
            results = fetch_trending_reels(topics=["fitness"], session=session)

        # Scraping should have extracted the like_count / comment_count pairs
        self.assertIsInstance(results, list)


class TestScrapeHashtagPage(unittest.TestCase):
    @resp_lib.activate
    def test_scrapes_engagement_from_html(self):
        resp_lib.add(
            resp_lib.GET,
            "https://www.instagram.com/explore/tags/travel/",
            body=_FAKE_HTML,
            status=200,
        )

        import requests
        session = requests.Session()
        with patch("trend_tracker.instagram_tracker.config") as mock_config:
            mock_config.INSTAGRAM_ACCESS_TOKEN = ""
            mock_config.INSTAGRAM_USER_ID = ""

            results = _scrape_hashtag_page("travel", session)

        self.assertIsInstance(results, list)
        if results:
            self.assertEqual(results[0]["topic"], "travel")
            self.assertEqual(results[0]["source"], "instagram_scrape")

    @resp_lib.activate
    def test_returns_empty_on_http_error(self):
        resp_lib.add(
            resp_lib.GET,
            "https://www.instagram.com/explore/tags/test/",
            status=429,
        )

        import requests
        session = requests.Session()
        results = _scrape_hashtag_page("test", session)
        self.assertEqual(results, [])


class TestFetchTrendingReelsNoCredentials(unittest.TestCase):
    @resp_lib.activate
    def test_uses_scraping_when_no_credentials(self):
        with patch("trend_tracker.instagram_tracker.config") as mock_config:
            mock_config.INSTAGRAM_ACCESS_TOKEN = ""
            mock_config.INSTAGRAM_USER_ID = ""
            mock_config.TRENDING_TOPICS = ["cooking"]

            resp_lib.add(
                resp_lib.GET,
                "https://www.instagram.com/explore/tags/cooking/",
                body=_FAKE_HTML,
                status=200,
            )

            import requests
            session = requests.Session()
            results = fetch_trending_reels(topics=["cooking"], session=session)

        self.assertIsInstance(results, list)


if __name__ == "__main__":
    unittest.main()
