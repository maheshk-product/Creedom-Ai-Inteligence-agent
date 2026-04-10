"""
YouTube Shorts Trending Tracker.

Uses the YouTube Data API v3 (free tier, 10,000 units/day) to search for
trending short-form videos for each configured topic.

Quota cost per run:
  - search.list  →  100 units per call
  - videos.list  →    1 unit  per call (for statistics)
  Up to 4 topics × ~101 units ≈ ~404 units per full run  (well within daily quota)
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

from .config import config

logger = logging.getLogger(__name__)

# ISO 8601 duration for "Shorts" (≤ 60 seconds) – used as videoDuration filter
_SHORTS_DURATION = "short"


def _build_search_url(topic: str) -> str:
    """Return the search.list API URL for a given topic."""
    return (
        f"{config.YOUTUBE_API_BASE}/search"
        f"?part=snippet"
        f"&q={requests.utils.quote(topic + ' shorts')}"
        f"&type=video"
        f"&videoDuration={_SHORTS_DURATION}"
        f"&order=viewCount"
        f"&maxResults={config.YOUTUBE_MAX_RESULTS}"
        f"&key={config.YOUTUBE_API_KEY}"
    )


def _build_stats_url(video_ids: List[str]) -> str:
    """Return the videos.list API URL to fetch statistics for a list of video IDs."""
    ids = ",".join(video_ids)
    return (
        f"{config.YOUTUBE_API_BASE}/videos"
        f"?part=statistics,contentDetails"
        f"&id={ids}"
        f"&key={config.YOUTUBE_API_KEY}"
    )


def _parse_search_results(data: Dict[str, Any], topic: str) -> List[Dict[str, Any]]:
    """Parse raw search.list API response into a list of video dicts."""
    items = data.get("items", [])
    videos = []
    for item in items:
        snippet = item.get("snippet", {})
        video_id = item.get("id", {}).get("videoId", "")
        if not video_id:
            continue
        videos.append(
            {
                "topic": topic,
                "video_id": video_id,
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "published_at": snippet.get("publishedAt", ""),
                "thumbnail": (
                    snippet.get("thumbnails", {})
                    .get("high", {})
                    .get("url", "")
                ),
                "url": f"https://www.youtube.com/shorts/{video_id}",
                "view_count": 0,
                "like_count": 0,
                "comment_count": 0,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "source": "youtube",
            }
        )
    return videos


def _enrich_with_statistics(
    videos: List[Dict[str, Any]], session: requests.Session
) -> List[Dict[str, Any]]:
    """Add view/like/comment counts to each video dict via videos.list."""
    if not videos:
        return videos

    video_ids = [v["video_id"] for v in videos]
    url = _build_stats_url(video_ids)

    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        stats_map: Dict[str, Dict] = {}
        for item in resp.json().get("items", []):
            vid_id = item.get("id", "")
            stats = item.get("statistics", {})
            stats_map[vid_id] = stats

        for video in videos:
            stats = stats_map.get(video["video_id"], {})
            video["view_count"] = int(stats.get("viewCount", 0))
            video["like_count"] = int(stats.get("likeCount", 0))
            video["comment_count"] = int(stats.get("commentCount", 0))
    except requests.RequestException as exc:
        logger.warning("Failed to fetch video statistics: %s", exc)

    return videos


def fetch_trending_shorts(
    topics: Optional[List[str]] = None,
    session: Optional[requests.Session] = None,
) -> List[Dict[str, Any]]:
    """
    Fetch trending YouTube Shorts for the given topics.

    Args:
        topics: List of search topics. Defaults to ``config.TRENDING_TOPICS``.
        session: Optional ``requests.Session`` for dependency injection / testing.

    Returns:
        List of video dicts with engagement metrics.
    """
    if not config.YOUTUBE_API_KEY:
        logger.warning("YouTube API key not configured – skipping YouTube fetch.")
        return []

    if topics is None:
        topics = config.TRENDING_TOPICS

    if session is None:
        session = requests.Session()

    all_videos: List[Dict[str, Any]] = []

    for topic in topics:
        logger.info("Fetching YouTube Shorts for topic: %s", topic)
        url = _build_search_url(topic)
        try:
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
            videos = _parse_search_results(resp.json(), topic)
            videos = _enrich_with_statistics(videos, session)
            logger.info("  → Found %d videos for '%s'", len(videos), topic)
            all_videos.extend(videos)
        except requests.RequestException as exc:
            logger.error("YouTube API error for topic '%s': %s", topic, exc)

    return all_videos
