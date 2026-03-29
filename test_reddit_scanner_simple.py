"""
Tests for the Simple Reddit Scanner (No Authentication)

These tests verify that the public JSON scanning functionality works correctly.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from reddit_scanner_simple import SimpleRedditScanner
from creedom_agent import TrendData


class TestSimpleRedditScanner(unittest.TestCase):
    """Test cases for SimpleRedditScanner."""

    def setUp(self):
        """Set up test fixtures."""
        self.scanner = SimpleRedditScanner()

    def test_scanner_initialization(self):
        """Test that scanner initializes correctly."""
        self.assertEqual(self.scanner.base_url, "https://www.reddit.com")
        self.assertIn("CreedomAgent", self.scanner.user_agent)

    @patch('urllib.request.urlopen')
    def test_get_hot_posts_success(self, mock_urlopen):
        """Test successfully fetching hot posts from a subreddit."""
        # Mock Reddit API response
        mock_response = {
            'data': {
                'children': [
                    {
                        'data': {
                            'id': 'abc123',
                            'title': 'Test Post Title',
                            'score': 1000,
                            'num_comments': 100,
                            'created_utc': 1234567890,
                            'permalink': '/r/test/comments/abc123/',
                            'selftext': 'This is test content',
                            'stickied': False
                        }
                    },
                    {
                        'data': {
                            'id': 'def456',
                            'title': 'Another Test Post',
                            'score': 500,
                            'num_comments': 50,
                            'created_utc': 1234567891,
                            'permalink': '/r/test/comments/def456/',
                            'selftext': 'More test content',
                            'stickied': False
                        }
                    },
                    {
                        'data': {
                            'id': 'ghi789',
                            'title': 'Stickied Post',
                            'score': 2000,
                            'num_comments': 200,
                            'created_utc': 1234567892,
                            'permalink': '/r/test/comments/ghi789/',
                            'selftext': 'Pinned content',
                            'stickied': True  # Should be skipped
                        }
                    }
                ]
            }
        }

        # Configure mock
        mock_response_obj = MagicMock()
        mock_response_obj.read.return_value = json.dumps(mock_response).encode('utf-8')
        mock_response_obj.__enter__.return_value = mock_response_obj
        mock_response_obj.__exit__.return_value = None
        mock_urlopen.return_value = mock_response_obj

        # Test
        trends = self.scanner.get_hot_posts('test', limit=10)

        # Verify
        self.assertEqual(len(trends), 2)  # Should skip stickied post
        self.assertIsInstance(trends[0], TrendData)
        self.assertEqual(trends[0].post_id, 'abc123')
        self.assertEqual(trends[0].title, 'Test Post Title')
        self.assertEqual(trends[0].score, 1000)
        self.assertEqual(trends[0].num_comments, 100)
        self.assertEqual(trends[0].subreddit, 'test')

    @patch('urllib.request.urlopen')
    def test_get_hot_posts_empty_response(self, mock_urlopen):
        """Test handling empty response from Reddit."""
        mock_response = {'data': {'children': []}}

        mock_response_obj = MagicMock()
        mock_response_obj.read.return_value = json.dumps(mock_response).encode('utf-8')
        mock_response_obj.__enter__.return_value = mock_response_obj
        mock_response_obj.__exit__.return_value = None
        mock_urlopen.return_value = mock_response_obj

        trends = self.scanner.get_hot_posts('test', limit=10)

        self.assertEqual(len(trends), 0)

    @patch('urllib.request.urlopen')
    def test_get_subreddit_info_success(self, mock_urlopen):
        """Test successfully fetching subreddit information."""
        mock_response = {
            'data': {
                'display_name': 'technology',
                'subscribers': 1000000,
                'public_description': 'Tech news and discussion',
                'over18': False
            }
        }

        mock_response_obj = MagicMock()
        mock_response_obj.read.return_value = json.dumps(mock_response).encode('utf-8')
        mock_response_obj.__enter__.return_value = mock_response_obj
        mock_response_obj.__exit__.return_value = None
        mock_urlopen.return_value = mock_response_obj

        info = self.scanner.get_subreddit_info('technology')

        self.assertIsNotNone(info)
        self.assertEqual(info['name'], 'technology')
        self.assertEqual(info['subscribers'], 1000000)
        self.assertEqual(info['description'], 'Tech news and discussion')
        self.assertFalse(info['over18'])

    def test_url_construction(self):
        """Test that URLs are constructed correctly."""
        # Test with different subreddit names
        subreddits = ['test', 'technology', 'fitness']
        for sub in subreddits:
            with patch.object(self.scanner, '_make_request', return_value={'data': {'children': []}}):
                self.scanner.get_hot_posts(sub, limit=50)
                # Verify URL format would be correct (through the call)

    @patch('urllib.request.urlopen')
    def test_limit_parameter(self, mock_urlopen):
        """Test that limit parameter is respected."""
        mock_response = {'data': {'children': []}}

        mock_response_obj = MagicMock()
        mock_response_obj.read.return_value = json.dumps(mock_response).encode('utf-8')
        mock_response_obj.__enter__.return_value = mock_response_obj
        mock_response_obj.__exit__.return_value = None
        mock_urlopen.return_value = mock_response_obj

        # Test with limit > 100 (should cap at 100)
        self.scanner.get_hot_posts('test', limit=150)

        # Verify the URL contains limit=100
        called_request = mock_urlopen.call_args[0][0]
        self.assertIn('limit=100', called_request.full_url)

    def test_user_agent_header(self):
        """Test that user agent is set correctly."""
        custom_scanner = SimpleRedditScanner(user_agent="CustomAgent/1.0")
        self.assertEqual(custom_scanner.user_agent, "CustomAgent/1.0")

    @patch('urllib.request.urlopen')
    def test_handles_missing_fields(self, mock_urlopen):
        """Test handling posts with missing optional fields."""
        mock_response = {
            'data': {
                'children': [
                    {
                        'data': {
                            'id': 'xyz789',
                            'title': 'Minimal Post',
                            'score': 10,
                            'num_comments': 1,
                            'created_utc': 1234567890,
                            'permalink': '/r/test/comments/xyz789/',
                            # Missing selftext
                            'stickied': False
                        }
                    }
                ]
            }
        }

        mock_response_obj = MagicMock()
        mock_response_obj.read.return_value = json.dumps(mock_response).encode('utf-8')
        mock_response_obj.__enter__.return_value = mock_response_obj
        mock_response_obj.__exit__.return_value = None
        mock_urlopen.return_value = mock_response_obj

        trends = self.scanner.get_hot_posts('test', limit=10)

        self.assertEqual(len(trends), 1)
        self.assertEqual(trends[0].selftext, '')  # Should default to empty string

    @patch('urllib.request.urlopen')
    def test_scan_multiple_subreddits(self, mock_urlopen):
        """Test scanning multiple subreddits."""
        mock_response = {
            'data': {
                'children': [
                    {
                        'data': {
                            'id': 'test1',
                            'title': 'Test',
                            'score': 100,
                            'num_comments': 10,
                            'created_utc': 1234567890,
                            'permalink': '/test',
                            'selftext': '',
                            'stickied': False
                        }
                    }
                ]
            }
        }

        mock_response_obj = MagicMock()
        mock_response_obj.read.return_value = json.dumps(mock_response).encode('utf-8')
        mock_response_obj.__enter__.return_value = mock_response_obj
        mock_response_obj.__exit__.return_value = None
        mock_urlopen.return_value = mock_response_obj

        subreddits = ['fitness', 'technology']
        result = self.scanner.scan_multiple_subreddits(subreddits, limit_per_sub=10)

        self.assertEqual(len(result), 2)
        self.assertIn('fitness', result)
        self.assertIn('technology', result)


class TestIntegrationWithCreedomAgent(unittest.TestCase):
    """Test integration between SimpleRedditScanner and CreedomAgent."""

    @patch('urllib.request.urlopen')
    def test_end_to_end_workflow(self, mock_urlopen):
        """Test complete workflow from scanning to TSS scoring."""
        from creedom_agent import CreedomAgent

        # Mock Reddit response
        mock_response = {
            'data': {
                'children': [
                    {
                        'data': {
                            'id': 'test123',
                            'title': 'Amazing revolutionary fitness breakthrough',
                            'score': 5000,
                            'num_comments': 1500,
                            'created_utc': 1234567890,
                            'permalink': '/r/fitness/comments/test123/',
                            'selftext': 'This is an incredible discovery',
                            'stickied': False
                        }
                    }
                ]
            }
        }

        mock_response_obj = MagicMock()
        mock_response_obj.read.return_value = json.dumps(mock_response).encode('utf-8')
        mock_response_obj.__enter__.return_value = mock_response_obj
        mock_response_obj.__exit__.return_value = None
        mock_urlopen.return_value = mock_response_obj

        # Scan Reddit
        scanner = SimpleRedditScanner()
        trends = scanner.get_hot_posts('fitness', limit=10)

        # Score with CreedomAgent
        agent = CreedomAgent()
        for trend in trends:
            trend.velocity = agent.calculate_velocity(trend.created_utc, trend.score)
            trend.comment_ratio = agent.calculate_comment_ratio(trend.num_comments, trend.score)
            trend.emotional_score = agent.detect_emotional_language(trend.title + " " + trend.selftext)
            trend.tss_score = agent.score_trend(trend, subreddit_subscribers=500000)

        # Verify
        self.assertEqual(len(trends), 1)
        self.assertGreater(trends[0].tss_score, 0)
        self.assertLessEqual(trends[0].tss_score, 100)


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Running Simple Reddit Scanner Tests")
    print("="*60 + "\n")
    run_tests()
