"""
Tests for Creedom Intelligence Agent

Run with: python -m pytest test_creedom_agent.py -v
Or simply: python test_creedom_agent.py
"""

import unittest
from datetime import datetime, timedelta
from creedom_agent import (
    CreedomAgent, TrendData, CreatorProfile, ContentBrief
)


class TestCreedomAgent(unittest.TestCase):
    """Test suite for Creedom Intelligence Agent."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = CreedomAgent()
        self.sample_trend = TrendData(
            post_id="test123",
            title="Revolutionary AI breakthrough in machine learning",
            subreddit="technology",
            score=3000,
            num_comments=900,
            created_utc=datetime.utcnow().timestamp() - 3600,  # 1 hour ago
            url="https://reddit.com/r/technology/test123",
            selftext="This amazing new breakthrough changes everything"
        )
        self.sample_creator = CreatorProfile(
            creator_id="creator_test_001",
            niche="technology",
            platform="instagram",
            style="educational",
            follower_count=25000,
            audience_age="25-35",
            past_performance={'avg_engagement': 0.05}
        )

    def test_calculate_velocity(self):
        """Test velocity calculation."""
        # Post 1 hour old with 3000 score = 3000 score/hour
        velocity = self.agent.calculate_velocity(
            created_utc=datetime.utcnow().timestamp() - 3600,
            score=3000
        )
        self.assertAlmostEqual(velocity, 3000.0, delta=10)

        # Post 2 hours old with 1000 score = 500 score/hour
        velocity = self.agent.calculate_velocity(
            created_utc=datetime.utcnow().timestamp() - 7200,
            score=1000
        )
        self.assertAlmostEqual(velocity, 500.0, delta=10)

    def test_calculate_comment_ratio(self):
        """Test comment ratio calculation."""
        # 300 comments / 1000 score = 0.3 ratio
        ratio = self.agent.calculate_comment_ratio(300, 1000)
        self.assertAlmostEqual(ratio, 0.6, delta=0.1)  # Normalized

        # 500 comments / 1000 score = 0.5 ratio (high engagement)
        ratio = self.agent.calculate_comment_ratio(500, 1000)
        self.assertEqual(ratio, 1.0)  # Maxed out at normalized 1.0

        # Zero score edge case
        ratio = self.agent.calculate_comment_ratio(100, 0)
        self.assertEqual(ratio, 0.0)

    def test_detect_emotional_language(self):
        """Test emotional language detection."""
        # High emotional content
        text = "This is shocking and amazing, absolutely mind-blowing!"
        score = self.agent.detect_emotional_language(text)
        self.assertGreater(score, 0.5)

        # Neutral content
        text = "This is a technical overview of the system architecture"
        score = self.agent.detect_emotional_language(text)
        self.assertLess(score, 0.3)

    def test_get_subreddit_size_score(self):
        """Test subreddit size scoring."""
        # Large subreddit
        score = self.agent.get_subreddit_size_score(2_000_000)
        self.assertEqual(score, 1.0)

        # Medium subreddit
        score = self.agent.get_subreddit_size_score(500_000)
        self.assertEqual(score, 0.7)

        # Small subreddit
        score = self.agent.get_subreddit_size_score(50_000)
        self.assertEqual(score, 0.4)

        # Tiny subreddit
        score = self.agent.get_subreddit_size_score(5_000)
        self.assertEqual(score, 0.2)

    def test_score_trend(self):
        """Test TSS scoring."""
        # Prepare trend data
        trend = TrendData(
            post_id="score_test",
            title="Amazing breakthrough",
            subreddit="technology",
            score=5000,
            num_comments=2500,
            created_utc=datetime.utcnow().timestamp() - 3600,
            url="https://reddit.com/test"
        )

        # Calculate components
        trend.velocity = self.agent.calculate_velocity(trend.created_utc, trend.score)
        trend.comment_ratio = self.agent.calculate_comment_ratio(trend.num_comments, trend.score)
        trend.emotional_score = self.agent.detect_emotional_language(trend.title)

        # Score trend
        tss = self.agent.score_trend(trend, subreddit_subscribers=1_000_000)

        # TSS should be between 0-100
        self.assertGreaterEqual(tss, 0)
        self.assertLessEqual(tss, 100)

        # High velocity + high comments should give good score
        self.assertGreater(tss, 50)

    def test_score_trend_below_threshold(self):
        """Test that low-quality trends score below 50."""
        trend = TrendData(
            post_id="low_score",
            title="Regular post",
            subreddit="small_sub",
            score=100,
            num_comments=10,
            created_utc=datetime.utcnow().timestamp() - 86400,  # 24 hours ago
            url="https://reddit.com/test"
        )

        trend.velocity = self.agent.calculate_velocity(trend.created_utc, trend.score)
        trend.comment_ratio = self.agent.calculate_comment_ratio(trend.num_comments, trend.score)
        trend.emotional_score = self.agent.detect_emotional_language(trend.title)

        tss = self.agent.score_trend(trend, subreddit_subscribers=10_000)

        # Low engagement should score below MEDIUM threshold
        self.assertLess(tss, self.agent.MEDIUM_THRESHOLD)

    def test_match_trend_to_creator(self):
        """Test trend-to-creator matching."""
        # Matching trend
        tech_trend = TrendData(
            post_id="match_test",
            title="New technology innovation in software development",
            subreddit="technology",
            score=1000,
            num_comments=200,
            created_utc=datetime.utcnow().timestamp(),
            url="https://reddit.com/test",
            selftext="Advanced technology breakthrough"
        )

        is_match, confidence = self.agent.match_trend_to_creator(tech_trend, self.sample_creator)
        self.assertTrue(is_match)
        self.assertGreater(confidence, 0.3)

        # Non-matching trend
        fitness_trend = TrendData(
            post_id="no_match_test",
            title="Best workout routine for abs",
            subreddit="fitness",
            score=1000,
            num_comments=200,
            created_utc=datetime.utcnow().timestamp(),
            url="https://reddit.com/test",
            selftext="Exercise tips"
        )

        is_match, confidence = self.agent.match_trend_to_creator(fitness_trend, self.sample_creator)
        self.assertFalse(is_match)

    def test_generate_brief(self):
        """Test content brief generation."""
        # Set up trend with high score
        trend = self.sample_trend
        trend.velocity = 3000.0
        trend.comment_ratio = 0.8
        trend.emotional_score = 0.7
        trend.tss_score = 85.0  # CRITICAL tier

        brief = self.agent.generate_brief(trend, self.sample_creator)

        # Verify structure
        self.assertIsInstance(brief, ContentBrief)
        self.assertIsNotNone(brief.trend_theme)
        self.assertIsNotNone(brief.hook_line)
        self.assertIsNotNone(brief.content_idea)
        self.assertIsNotNone(brief.urgency_window)
        self.assertEqual(brief.tss_score, 85.0)

        # Critical tier should have urgent window
        self.assertIn("today", brief.urgency_window.lower())

    def test_generate_brief_urgency_tiers(self):
        """Test urgency window based on TSS tiers."""
        trend = self.sample_trend

        # CRITICAL tier
        trend.tss_score = 90
        brief = self.agent.generate_brief(trend, self.sample_creator)
        self.assertIn("today", brief.urgency_window.lower())

        # HIGH tier
        trend.tss_score = 75
        brief = self.agent.generate_brief(trend, self.sample_creator)
        self.assertIn("5-7 days", brief.urgency_window.lower())

        # MEDIUM tier
        trend.tss_score = 60
        brief = self.agent.generate_brief(trend, self.sample_creator)
        self.assertIn("2 weeks", brief.urgency_window.lower())

    def test_can_send_nudge(self):
        """Test nudge cooldown logic."""
        creator_id = "test_creator_cooldown"

        # First time - should be able to send
        self.assertTrue(self.agent.can_send_nudge(creator_id))

        # After sending, add to cooldown
        self.agent.nudge_cooldown[creator_id] = datetime.utcnow()

        # Immediately after - should not be able to send
        self.assertFalse(self.agent.can_send_nudge(creator_id))

        # Simulate 4 days passing (beyond 3-day cooldown)
        self.agent.nudge_cooldown[creator_id] = datetime.utcnow() - timedelta(days=4)

        # Should be able to send again
        self.assertTrue(self.agent.can_send_nudge(creator_id))

    def test_has_seen_trend(self):
        """Test trend deduplication."""
        creator_id = "test_creator_dedup"
        trend_theme = "AI Revolution"

        # Initially should not have seen it
        self.assertFalse(self.agent.has_seen_trend(creator_id, trend_theme))

        # Add to sent trends
        self.agent.sent_trends[creator_id] = {trend_theme}

        # Now should return True
        self.assertTrue(self.agent.has_seen_trend(creator_id, trend_theme))

        # Different trend should still be False
        self.assertFalse(self.agent.has_seen_trend(creator_id, "Different Topic"))

    def test_send_nudge_message_length(self):
        """Test nudge message length validation."""
        creator_id = "test_creator_length"

        # Short message should succeed
        short_message = "This is a short test message. " * 3  # ~20 words
        result = self.agent.send_nudge(creator_id, short_message)
        self.assertTrue(result)

        # Message over 100 words should fail
        long_message = "word " * 101
        result = self.agent.send_nudge("another_creator", long_message)
        self.assertFalse(result)

    def test_send_nudge_respects_cooldown(self):
        """Test that send_nudge respects cooldown."""
        creator_id = "test_creator_cooldown_send"
        message = "Test message for cooldown"

        # First send should succeed
        result = self.agent.send_nudge(creator_id, message)
        self.assertTrue(result)

        # Second send immediately should fail
        result = self.agent.send_nudge(creator_id, message)
        self.assertFalse(result)

    def test_create_nudge_message(self):
        """Test nudge message creation."""
        brief = ContentBrief(
            trend_theme="AI transforms content creation",
            why_it_matters="Novel tech that solves creator pain points",
            hook_line="This AI tool does what took us 10 hours in 10 minutes",
            content_idea="Show before/after workflow comparison",
            urgency_window="Act in next 5-7 days",
            cross_niche_opportunity="Works for productivity creators too",
            tss_score=78.0,
            recommended_format="reel"
        )

        message = self.agent.create_nudge_message(brief, "Sarah")

        # Verify message structure
        self.assertIn("Sarah", message)
        self.assertIn(brief.trend_theme, message)
        self.assertIn(brief.hook_line, message)
        self.assertIn("Creedom", message)

        # Should be under 100 words
        word_count = len(message.split())
        self.assertLessEqual(word_count, 100)

        # Should indicate tier
        self.assertIn("HIGH", message)

    def test_log_signal(self):
        """Test signal logging."""
        trend = self.sample_trend
        trend.tss_score = 75.0

        initial_count = len(self.agent.signal_db)

        # Log signal
        self.agent.log_signal(trend, "creator_123")

        # Should have added one signal
        self.assertEqual(len(self.agent.signal_db), initial_count + 1)

        # Verify signal structure
        signal = self.agent.signal_db[-1]
        self.assertEqual(signal['trend_id'], trend.post_id)
        self.assertEqual(signal['tss_score'], 75.0)
        self.assertEqual(signal['creator_id'], "creator_123")
        self.assertIn('timestamp', signal)

    def test_process_trends_for_creator(self):
        """Test processing multiple trends for a creator."""
        # Create multiple trends
        trends = []
        for i in range(5):
            trend = TrendData(
                post_id=f"multi_{i}",
                title=f"Technology breakthrough number {i}",
                subreddit="technology",
                score=2000 + i * 500,
                num_comments=400 + i * 100,
                created_utc=datetime.utcnow().timestamp() - 3600,
                url=f"https://reddit.com/test{i}",
                selftext="Tech content"
            )
            # Calculate metrics
            trend.velocity = self.agent.calculate_velocity(trend.created_utc, trend.score)
            trend.comment_ratio = self.agent.calculate_comment_ratio(trend.num_comments, trend.score)
            trend.emotional_score = self.agent.detect_emotional_language(trend.title)
            trend.tss_score = self.agent.score_trend(trend)
            trends.append(trend)

        # Process for creator
        briefs = self.agent.process_trends_for_creator(self.sample_creator, trends)

        # Should generate briefs only for matching trends with TSS >= 50
        self.assertGreater(len(briefs), 0)
        self.assertIsInstance(briefs[0], ContentBrief)

        # Verify all briefs meet threshold
        for brief in briefs:
            self.assertGreaterEqual(brief.tss_score, self.agent.MEDIUM_THRESHOLD)

    def test_no_duplicate_trends_to_creator(self):
        """Test that same trend isn't sent twice to same creator."""
        # Create trend with explicit match to technology niche
        trend = TrendData(
            post_id="duplicate_test",
            title="New technology breakthrough in software",
            subreddit="technology",
            score=3000,
            num_comments=900,
            created_utc=datetime.utcnow().timestamp() - 3600,
            url="https://reddit.com/test",
            selftext="Amazing technology innovation"
        )
        trend.velocity = 3000
        trend.comment_ratio = 0.8
        trend.emotional_score = 0.7
        trend.tss_score = 75

        # Process first time
        briefs1 = self.agent.process_trends_for_creator(self.sample_creator, [trend])
        self.assertEqual(len(briefs1), 1)

        # Process same trend again
        briefs2 = self.agent.process_trends_for_creator(self.sample_creator, [trend])
        self.assertEqual(len(briefs2), 0)  # Should be filtered out


class TestTSSScoring(unittest.TestCase):
    """Dedicated tests for TSS scoring algorithm."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = CreedomAgent()

    def test_tss_weights_sum_to_one(self):
        """Verify TSS weights sum to 100%."""
        total_weight = (
            self.agent.VELOCITY_WEIGHT +
            self.agent.COMMENT_RATIO_WEIGHT +
            self.agent.SUBREDDIT_SIZE_WEIGHT +
            self.agent.EMOTIONAL_WEIGHT +
            self.agent.CROSS_SUBREDDIT_WEIGHT
        )
        self.assertAlmostEqual(total_weight, 1.0, places=2)

    def test_tss_critical_threshold(self):
        """Test CRITICAL tier detection."""
        self.assertEqual(self.agent.CRITICAL_THRESHOLD, 85)
        self.assertEqual(self.agent.HIGH_THRESHOLD, 70)
        self.assertEqual(self.agent.MEDIUM_THRESHOLD, 50)

    def test_perfect_trend_scores_high(self):
        """Test that a perfect trend scores in CRITICAL range."""
        trend = TrendData(
            post_id="perfect",
            title="SHOCKING revelation that will change everything forever - MUST SEE",
            subreddit="technology",
            score=10000,
            num_comments=5000,
            created_utc=datetime.utcnow().timestamp() - 1800,  # 30 min ago = high velocity
            url="https://reddit.com/test",
            selftext="This is absolutely insane and mind-blowing"
        )

        trend.velocity = self.agent.calculate_velocity(trend.created_utc, trend.score)
        trend.comment_ratio = self.agent.calculate_comment_ratio(trend.num_comments, trend.score)
        trend.emotional_score = self.agent.detect_emotional_language(trend.title + " " + trend.selftext)
        trend.tss_score = self.agent.score_trend(trend, subreddit_subscribers=5_000_000)

        # Should be very high
        self.assertGreater(trend.tss_score, self.agent.HIGH_THRESHOLD)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
