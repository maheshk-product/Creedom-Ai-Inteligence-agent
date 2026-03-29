"""
Simple Reddit Scanner - No Authentication Required

This scanner uses Reddit's public JSON API that doesn't require authentication.
Perfect for beginners or users who don't want to set up Reddit API credentials.

Limitations compared to authenticated access:
- Can only access public subreddits
- Limited to ~100 posts per request
- Subject to Reddit's rate limiting for unauthenticated requests
"""

import json
import time
import urllib.request
import urllib.error
from typing import List, Optional
from creedom_agent import TrendData


class SimpleRedditScanner:
    """
    Simple Reddit scanner using public JSON endpoints.
    No authentication required!
    """

    def __init__(self, user_agent: str = "CreedomAgent/1.0"):
        """
        Initialize the simple scanner.

        Args:
            user_agent: User agent string for requests
        """
        self.user_agent = user_agent
        self.base_url = "https://www.reddit.com"

    def _make_request(self, url: str, retries: int = 3) -> Optional[dict]:
        """
        Make a request to Reddit's public JSON API.

        Args:
            url: The URL to request
            retries: Number of retries on failure

        Returns:
            Parsed JSON response or None on failure
        """
        headers = {
            'User-Agent': self.user_agent
        }

        for attempt in range(retries):
            try:
                request = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(request, timeout=10) as response:
                    data = response.read()
                    return json.loads(data.decode('utf-8'))
            except urllib.error.HTTPError as e:
                if e.code == 429:  # Rate limited
                    wait_time = (attempt + 1) * 5  # Exponential backoff
                    print(f"  ⚠️  Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                elif e.code == 404:
                    print(f"  ❌ Subreddit not found or is private")
                    return None
                else:
                    print(f"  ❌ HTTP Error {e.code}: {e.reason}")
                    return None
            except urllib.error.URLError as e:
                print(f"  ❌ Network error: {e.reason}")
                return None
            except Exception as e:
                print(f"  ❌ Error: {e}")
                return None

        return None

    def get_hot_posts(self, subreddit: str, limit: int = 50) -> List[TrendData]:
        """
        Get hot posts from a subreddit using public JSON API.

        Args:
            subreddit: Name of the subreddit (without r/)
            limit: Maximum number of posts to retrieve (max ~100)

        Returns:
            List of TrendData objects
        """
        # Reddit's JSON endpoint
        url = f"{self.base_url}/r/{subreddit}/hot.json?limit={min(limit, 100)}"

        print(f"  📡 Fetching from r/{subreddit} (no auth)...")

        response_data = self._make_request(url)
        if not response_data:
            return []

        trends = []
        try:
            posts = response_data.get('data', {}).get('children', [])

            for post_data in posts:
                post = post_data.get('data', {})

                # Skip pinned/stickied posts
                if post.get('stickied', False):
                    continue

                # Create TrendData object
                trend = TrendData(
                    post_id=post.get('id', ''),
                    title=post.get('title', ''),
                    subreddit=subreddit,
                    score=post.get('score', 0),
                    num_comments=post.get('num_comments', 0),
                    created_utc=post.get('created_utc', 0),
                    url=f"{self.base_url}{post.get('permalink', '')}",
                    selftext=post.get('selftext', '')[:500]  # First 500 chars
                )

                trends.append(trend)

            # Small delay to be respectful to Reddit's servers
            time.sleep(2)

        except Exception as e:
            print(f"  ❌ Error parsing response: {e}")
            return []

        return trends

    def get_subreddit_info(self, subreddit: str) -> Optional[dict]:
        """
        Get basic information about a subreddit.

        Args:
            subreddit: Name of the subreddit

        Returns:
            Dictionary with subreddit info or None
        """
        url = f"{self.base_url}/r/{subreddit}/about.json"

        response_data = self._make_request(url)
        if not response_data:
            return None

        try:
            data = response_data.get('data', {})
            return {
                'name': data.get('display_name', subreddit),
                'subscribers': data.get('subscribers', 0),
                'description': data.get('public_description', ''),
                'over18': data.get('over18', False)
            }
        except Exception as e:
            print(f"  ❌ Error parsing subreddit info: {e}")
            return None

    def scan_multiple_subreddits(self, subreddits: List[str], limit_per_sub: int = 50) -> dict:
        """
        Scan multiple subreddits and return trends from all.

        Args:
            subreddits: List of subreddit names
            limit_per_sub: How many posts to get from each

        Returns:
            Dictionary with subreddit as key and list of trends as value
        """
        all_trends = {}

        for subreddit in subreddits:
            trends = self.get_hot_posts(subreddit, limit_per_sub)
            if trends:
                all_trends[subreddit] = trends
            # Be respectful - wait between requests
            time.sleep(2)

        return all_trends


def test_scanner():
    """Test the simple scanner."""
    print("\n" + "="*60)
    print("Testing Simple Reddit Scanner (No Auth)")
    print("="*60 + "\n")

    scanner = SimpleRedditScanner()

    # Test getting posts from a single subreddit
    print("Testing: Scanning r/technology...")
    trends = scanner.get_hot_posts('technology', limit=10)

    if trends:
        print(f"✅ Found {len(trends)} posts from r/technology\n")
        print("Top 3 posts:")
        for i, trend in enumerate(trends[:3], 1):
            print(f"  {i}. Score: {trend.score} | {trend.title[:60]}...")
    else:
        print("❌ No posts retrieved")

    print("\n" + "="*60)
    print("Test complete!")
    print("="*60)


if __name__ == "__main__":
    test_scanner()
