"""
Instagram Reels Hashtag Tracker.

Strategy (free-tier friendly):
  1. **Primary:** Instagram Graph API ``/hashtag_search`` + ``recent_media``
     – Requires an Instagram Business / Creator account + Facebook App.
     – Free, but rate-limited (200 unique hashtags per 7 days per user).
  2. **Fallback:** Public web scraping of Instagram hashtag pages
     – Works without credentials but is subject to Instagram's ToS.
     – Used only when the Graph API is not configured.

For a SaaS product, prompt end-users to connect their own Instagram
Business account to stay within per-user rate limits.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

from .config import config

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
#  Graph API helpers                                                   #
# ------------------------------------------------------------------ #

def _graph_api_hashtag_id(hashtag: str, session: requests.Session) -> Optional[str]:
    """Resolve a hashtag string to an Instagram hashtag ID via Graph API."""
    url = (
        f"{config.INSTAGRAM_API_BASE}/ig_hashtag_search"
        f"?user_id={config.INSTAGRAM_USER_ID}"
        f"&q={requests.utils.quote(hashtag)}"
        f"&access_token={config.INSTAGRAM_ACCESS_TOKEN}"
    )
    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        hashtag_id = data.get("data", [{}])[0].get("id")
        return hashtag_id
    except (requests.RequestException, IndexError, KeyError) as exc:
        logger.warning("Could not resolve hashtag ID for '%s': %s", hashtag, exc)
        return None


def _graph_api_recent_media(
    hashtag_id: str, hashtag: str, session: requests.Session
) -> List[Dict[str, Any]]:
    """Fetch recent media for a hashtag ID via Graph API."""
    url = (
        f"{config.INSTAGRAM_API_BASE}/{hashtag_id}/recent_media"
        f"?user_id={config.INSTAGRAM_USER_ID}"
        f"&fields=id,media_type,media_url,thumbnail_url,permalink,"
        f"like_count,comments_count,timestamp"
        f"&access_token={config.INSTAGRAM_ACCESS_TOKEN}"
    )
    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        items = resp.json().get("data", [])
        results = []
        for item in items:
            if item.get("media_type") not in ("VIDEO", "REEL"):
                continue
            results.append(
                {
                    "topic": hashtag,
                    "reel_id": item.get("id", ""),
                    "url": item.get("permalink", ""),
                    "like_count": int(item.get("like_count", 0)),
                    "comment_count": int(item.get("comments_count", 0)),
                    "published_at": item.get("timestamp", ""),
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "source": "instagram_graph_api",
                }
            )
        return results
    except requests.RequestException as exc:
        logger.warning("Graph API media fetch failed for hashtag ID '%s': %s", hashtag_id, exc)
        return []


def _fetch_via_graph_api(
    topics: List[str], session: requests.Session
) -> List[Dict[str, Any]]:
    """Use the Instagram Graph API to fetch recent Reels per hashtag."""
    all_reels: List[Dict[str, Any]] = []
    for topic in topics:
        logger.info("Fetching Instagram Reels via Graph API for: #%s", topic)
        hashtag_id = _graph_api_hashtag_id(topic, session)
        if not hashtag_id:
            continue
        reels = _graph_api_recent_media(hashtag_id, topic, session)
        logger.info("  → Found %d reels for '#%s'", len(reels), topic)
        all_reels.extend(reels)
    return all_reels


# ------------------------------------------------------------------ #
#  Public web-scraping fallback                                        #
# ------------------------------------------------------------------ #

# Minimal regex patterns to extract engagement counts from the
# JSON-LD / meta tags embedded in Instagram's public hashtag page.
_LIKES_RE = re.compile(r'"like_count"\s*:\s*(\d+)', re.IGNORECASE)
_COMMENTS_RE = re.compile(r'"comment_count"\s*:\s*(\d+)', re.IGNORECASE)

_SCRAPE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _scrape_hashtag_page(topic: str, session: requests.Session) -> List[Dict[str, Any]]:
    """
    Scrape Instagram's public hashtag page as a last-resort fallback.

    NOTE: This is fragile and may break when Instagram changes its markup.
          It is provided only as a demonstration; production SaaS should
          rely on the Graph API.
    """
    url = f"https://www.instagram.com/explore/tags/{requests.utils.quote(topic)}/"
    try:
        resp = session.get(url, headers=_SCRAPE_HEADERS, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Scraping fallback failed for '#%s': %s", topic, exc)
        return []

    html = resp.text
    likes = _LIKES_RE.findall(html)
    comments = _COMMENTS_RE.findall(html)

    results = []
    for idx, (lk, cm) in enumerate(zip(likes[:10], comments[:10])):
        results.append(
            {
                "topic": topic,
                "reel_id": f"scrape_{topic}_{idx}",
                "url": url,
                "like_count": int(lk),
                "comment_count": int(cm),
                "published_at": "",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "source": "instagram_scrape",
            }
        )
    logger.info("  → Scraped %d reels for '#%s'", len(results), topic)
    return results


def _fetch_via_scraping(
    topics: List[str], session: requests.Session
) -> List[Dict[str, Any]]:
    """Iterate over topics and scrape each Instagram hashtag page."""
    all_reels: List[Dict[str, Any]] = []
    for topic in topics:
        logger.info("Fetching Instagram Reels via scraping for: #%s", topic)
        reels = _scrape_hashtag_page(topic, session)
        all_reels.extend(reels)
    return all_reels


# ------------------------------------------------------------------ #
#  Public API                                                          #
# ------------------------------------------------------------------ #

def fetch_trending_reels(
    topics: Optional[List[str]] = None,
    session: Optional[requests.Session] = None,
) -> List[Dict[str, Any]]:
    """
    Fetch trending Instagram Reels for the given topics.

    Uses the Graph API when credentials are available; falls back to
    public web scraping otherwise.

    Args:
        topics: List of hashtags to track. Defaults to ``config.TRENDING_TOPICS``.
        session: Optional ``requests.Session`` for dependency injection / testing.

    Returns:
        List of reel dicts with engagement metrics.
    """
    if topics is None:
        topics = config.TRENDING_TOPICS

    if session is None:
        session = requests.Session()

    if config.INSTAGRAM_ACCESS_TOKEN and config.INSTAGRAM_USER_ID:
        results = _fetch_via_graph_api(topics, session)
        if results:
            return results
        logger.warning(
            "Graph API returned no results; falling back to scraping."
        )

    return _fetch_via_scraping(topics, session)
