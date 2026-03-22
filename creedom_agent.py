"""
Creedom Intelligence Agent - Main Module

An AI agent built for content creators to detect trending topics before they go viral,
match them to creator niches, and deliver actionable content briefs.
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class TrendData:
    """Data structure for a detected trend."""
    post_id: str
    title: str
    subreddit: str
    score: int
    num_comments: int
    created_utc: float
    url: str
    selftext: str = ""
    velocity: float = 0.0
    comment_ratio: float = 0.0
    emotional_score: float = 0.0
    tss_score: float = 0.0


@dataclass
class CreatorProfile:
    """Data structure for a creator profile."""
    creator_id: str
    niche: str
    platform: str
    style: str
    follower_count: int
    audience_age: str
    past_performance: Dict[str, float]


@dataclass
class ContentBrief:
    """Data structure for a content brief."""
    trend_theme: str
    why_it_matters: str
    hook_line: str
    content_idea: str
    urgency_window: str
    cross_niche_opportunity: str
    tss_score: float
    recommended_format: str


class CreedomAgent:
    """
    Creedom Intelligence Agent - Core Implementation

    Detects trends, scores them, matches to creators, and generates actionable briefs.
    """

    # TSS scoring weights
    VELOCITY_WEIGHT = 0.35
    COMMENT_RATIO_WEIGHT = 0.25
    SUBREDDIT_SIZE_WEIGHT = 0.15
    EMOTIONAL_WEIGHT = 0.15
    CROSS_SUBREDDIT_WEIGHT = 0.10

    # Tier thresholds
    CRITICAL_THRESHOLD = 85
    HIGH_THRESHOLD = 70
    MEDIUM_THRESHOLD = 50

    # Subreddit size categories (subscribers)
    SUBREDDIT_SIZES = {
        'large': 1_000_000,
        'medium': 100_000,
        'small': 10_000
    }

    # Emotional keywords for detection
    EMOTIONAL_KEYWORDS = [
        'shocking', 'amazing', 'unbelievable', 'insane', 'crazy',
        'mind-blowing', 'incredible', 'horrifying', 'devastating',
        'game-changer', 'revolutionary', 'urgent', 'breaking', 'viral',
        'exposed', 'revealed', 'secret', 'finally', 'must-see'
    ]

    def __init__(self):
        """Initialize the Creedom Agent."""
        self.nudge_cooldown = {}  # Track last nudge time per creator
        self.sent_trends = {}  # Track trends sent to each creator
        self.signal_db = []  # In-memory signal database

    def scan_reddit(self, subreddit: str, limit: int = 100) -> List[TrendData]:
        """
        Scan Reddit for potential trending topics.

        This is a placeholder that returns mock data structure.
        In production, this would use PRAW to fetch real Reddit data.

        Args:
            subreddit: The subreddit name to scan
            limit: Maximum number of posts to retrieve

        Returns:
            List of TrendData objects
        """
        # Placeholder - in production, would use PRAW:
        # reddit = praw.Reddit(...)
        # posts = reddit.subreddit(subreddit).hot(limit=limit)
        # return [self._parse_reddit_post(post) for post in posts]
        return []

    def calculate_velocity(self, created_utc: float, score: int) -> float:
        """
        Calculate the velocity of a post (score per hour).

        Args:
            created_utc: Unix timestamp when post was created
            score: Current upvote score

        Returns:
            Velocity as score per hour
        """
        now = datetime.now(datetime.UTC if hasattr(datetime, 'UTC') else None)
        if now.tzinfo is None:
            now = datetime.utcnow()
        now_timestamp = now.timestamp()
        hours_old = max((now_timestamp - created_utc) / 3600, 0.1)  # Prevent division by zero
        return score / hours_old

    def calculate_comment_ratio(self, num_comments: int, score: int) -> float:
        """
        Calculate the comment-to-upvote ratio.

        High ratios indicate controversial or engaging content.

        Args:
            num_comments: Number of comments
            score: Upvote score

        Returns:
            Comment ratio (normalized to 0-1)
        """
        if score == 0:
            return 0.0
        ratio = num_comments / score
        # Normalize: ratios above 0.5 are considered very high
        return min(ratio / 0.5, 1.0)

    def detect_emotional_language(self, text: str) -> float:
        """
        Detect emotional language in post title and text.

        Args:
            text: Text to analyze (title + selftext)

        Returns:
            Emotional score (0-1)
        """
        text_lower = text.lower()
        matches = sum(1 for keyword in self.EMOTIONAL_KEYWORDS if keyword in text_lower)
        # Normalize: 3+ emotional keywords = max score
        return min(matches / 3.0, 1.0)

    def get_subreddit_size_score(self, subreddit_subscribers: int) -> float:
        """
        Score based on subreddit size.

        Args:
            subreddit_subscribers: Number of subscribers

        Returns:
            Size score (0-1)
        """
        if subreddit_subscribers >= self.SUBREDDIT_SIZES['large']:
            return 1.0
        elif subreddit_subscribers >= self.SUBREDDIT_SIZES['medium']:
            return 0.7
        elif subreddit_subscribers >= self.SUBREDDIT_SIZES['small']:
            return 0.4
        else:
            return 0.2

    def score_trend(self, trend_data: TrendData, subreddit_subscribers: int = 500_000) -> float:
        """
        Calculate the TSS (Trend Scoring System) score for a trend.

        Formula:
        TSS = (velocity × 35%) + (comment_ratio × 25%) + (subreddit_size × 15%) +
              (emotional_score × 15%) + (cross_subreddit × 10%)

        Args:
            trend_data: TrendData object with post information
            subreddit_subscribers: Number of subreddit subscribers

        Returns:
            TSS score (0-100)
        """
        # Calculate velocity score (normalize to 0-1, assuming 100+ score/hr is max)
        velocity_score = min(trend_data.velocity / 100.0, 1.0)

        # Get other component scores
        comment_score = trend_data.comment_ratio
        subreddit_score = self.get_subreddit_size_score(subreddit_subscribers)
        emotional_score = trend_data.emotional_score

        # Cross-subreddit score (placeholder - would check if same topic in multiple subs)
        cross_subreddit_score = 0.5  # Default to medium

        # Calculate weighted TSS
        tss = (
            velocity_score * self.VELOCITY_WEIGHT +
            comment_score * self.COMMENT_RATIO_WEIGHT +
            subreddit_score * self.SUBREDDIT_SIZE_WEIGHT +
            emotional_score * self.EMOTIONAL_WEIGHT +
            cross_subreddit_score * self.CROSS_SUBREDDIT_WEIGHT
        ) * 100

        return round(tss, 2)

    def get_creator_profile(self, creator_id: str) -> Optional[CreatorProfile]:
        """
        Retrieve a creator's profile.

        In production, this would fetch from a database.

        Args:
            creator_id: Unique creator identifier

        Returns:
            CreatorProfile object or None
        """
        # Placeholder - would fetch from database
        return None

    def match_trend_to_creator(self, trend_data: TrendData, creator: CreatorProfile) -> Tuple[bool, float]:
        """
        Determine if a trend matches a creator's niche and style.

        Args:
            trend_data: The trend to evaluate
            creator: The creator profile

        Returns:
            Tuple of (is_match, confidence_score)
        """
        # Simple keyword matching - in production, would use more sophisticated NLP
        text = (trend_data.title + " " + trend_data.selftext).lower()
        niche_keywords = creator.niche.lower().split()

        matches = sum(1 for keyword in niche_keywords if keyword in text)
        confidence = min(matches / len(niche_keywords), 1.0) if niche_keywords else 0.0

        is_match = confidence >= 0.3  # At least 30% keyword overlap
        return is_match, confidence

    def generate_brief(self, trend_data: TrendData, creator: CreatorProfile) -> ContentBrief:
        """
        Generate a personalized content brief for a creator.

        Args:
            trend_data: The trending topic
            creator: The creator profile

        Returns:
            ContentBrief object with actionable content
        """
        # Extract theme (simplified - in production, would use NLP)
        theme = trend_data.title[:60] + "..." if len(trend_data.title) > 60 else trend_data.title

        # Determine urgency based on TSS tier
        if trend_data.tss_score >= self.CRITICAL_THRESHOLD:
            urgency = "Act today - 12-24 hours max"
        elif trend_data.tss_score >= self.HIGH_THRESHOLD:
            urgency = "Act in next 5-7 days"
        else:
            urgency = "Act within next 2 weeks"

        # Generate hook (simplified)
        hook = self._generate_hook(trend_data, creator)

        # Generate niche-specific idea
        content_idea = self._generate_content_idea(trend_data, creator)

        # Determine format based on creator platform and style
        format_map = {
            'instagram': 'reel | carousel',
            'youtube': 'talking head | voiceover',
            'linkedin': 'carousel | talking head'
        }
        recommended_format = format_map.get(creator.platform.lower(), 'reel | talking head')

        return ContentBrief(
            trend_theme=theme,
            why_it_matters=self._explain_psychology(trend_data),
            hook_line=hook,
            content_idea=content_idea,
            urgency_window=urgency,
            cross_niche_opportunity=self._find_cross_niche_angle(trend_data, creator),
            tss_score=trend_data.tss_score,
            recommended_format=recommended_format
        )

    def _generate_hook(self, trend_data: TrendData, creator: CreatorProfile) -> str:
        """Generate a hook line for the content."""
        # Simplified hook generation
        if creator.niche.lower() == 'fitness':
            return f"This changes everything about {trend_data.title.split()[0].lower()}..."
        elif creator.niche.lower() == 'finance':
            return f"Nobody's talking about this money move..."
        elif creator.niche.lower() == 'education':
            return f"Here's what they don't teach you about..."
        else:
            return f"You need to see this: {trend_data.title[:40]}..."

    def _generate_content_idea(self, trend_data: TrendData, creator: CreatorProfile) -> str:
        """Generate a niche-specific content idea."""
        niche = creator.niche.lower()
        return f"Create a {creator.style} piece connecting this trend to {niche}. Focus on how your audience can apply this immediately."

    def _explain_psychology(self, trend_data: TrendData) -> str:
        """Explain why a trend is spreading."""
        if trend_data.emotional_score > 0.7:
            return "High emotional resonance - triggers strong reactions and sharing behavior."
        elif trend_data.comment_ratio > 0.7:
            return "Controversial or debate-sparking - drives engagement through disagreement."
        else:
            return "Novel information that fills a knowledge gap in the target audience."

    def _find_cross_niche_angle(self, trend_data: TrendData, creator: CreatorProfile) -> str:
        """Find cross-niche opportunities."""
        # Simplified - in production, would use more sophisticated analysis
        niches = ['fitness', 'finance', 'education', 'entertainment']
        other_niches = [n for n in niches if n != creator.niche.lower()]
        if other_niches:
            return f"Could also work for {other_niches[0]} creators focusing on personal development angle."
        return "No obvious cross-niche opportunity detected."

    def can_send_nudge(self, creator_id: str) -> bool:
        """
        Check if we can send a nudge to a creator (respects 3-day cooldown).

        Args:
            creator_id: The creator's ID

        Returns:
            True if nudge can be sent, False otherwise
        """
        if creator_id not in self.nudge_cooldown:
            return True

        last_nudge = self.nudge_cooldown[creator_id]
        cooldown_expires = last_nudge + timedelta(days=3)
        now = datetime.now(datetime.UTC if hasattr(datetime, 'UTC') else None)
        if now.tzinfo is None:
            now = datetime.utcnow()
        return now >= cooldown_expires

    def has_seen_trend(self, creator_id: str, trend_theme: str) -> bool:
        """
        Check if a creator has already seen this trend theme.

        Args:
            creator_id: The creator's ID
            trend_theme: The trend theme

        Returns:
            True if already seen, False otherwise
        """
        if creator_id not in self.sent_trends:
            return False
        return trend_theme in self.sent_trends[creator_id]

    def send_nudge(self, creator_id: str, message: str, channel: str = 'whatsapp') -> bool:
        """
        Send a nudge to a creator via WhatsApp or email.

        Args:
            creator_id: The creator's ID
            message: The message content (max 100 words)
            channel: 'whatsapp' or 'email'

        Returns:
            True if sent successfully, False otherwise
        """
        # Validate message length
        word_count = len(message.split())
        if word_count > 100:
            print(f"Warning: Message exceeds 100 words ({word_count} words)")
            return False

        # Check cooldown
        if not self.can_send_nudge(creator_id):
            print(f"Cooldown active for creator {creator_id}")
            return False

        # Placeholder for actual sending logic
        # In production, would integrate with WhatsApp API or email service
        print(f"[{channel.upper()}] Sending nudge to {creator_id}:")
        print(message)

        # Update cooldown
        now = datetime.now(datetime.UTC if hasattr(datetime, 'UTC') else None)
        if now.tzinfo is None:
            now = datetime.utcnow()
        self.nudge_cooldown[creator_id] = now

        return True

    def log_signal(self, trend_data: TrendData, creator_id: Optional[str] = None) -> None:
        """
        Log a trend signal to the intelligence database.

        Args:
            trend_data: The trend data to log
            creator_id: Optional creator ID if matched
        """
        now = datetime.now(datetime.UTC if hasattr(datetime, 'UTC') else None)
        if now.tzinfo is None:
            now = datetime.utcnow()
        signal = {
            'timestamp': now.isoformat(),
            'trend_id': trend_data.post_id,
            'subreddit': trend_data.subreddit,
            'tss_score': trend_data.tss_score,
            'velocity': trend_data.velocity,
            'creator_id': creator_id,
            'title': trend_data.title
        }
        self.signal_db.append(signal)

    def create_nudge_message(self, brief: ContentBrief, creator_name: str) -> str:
        """
        Create a concise nudge message for a creator.

        Args:
            brief: The content brief
            creator_name: Creator's name

        Returns:
            Formatted nudge message (max 100 words)
        """
        tier = "CRITICAL" if brief.tss_score >= self.CRITICAL_THRESHOLD else "HIGH"

        message = f"""🔥 [{tier}] Trend Alert for {creator_name}

{brief.trend_theme}

Your hook: "{brief.hook_line}"

{brief.content_idea}

Window: {brief.urgency_window}

Open Creedom to get your full script."""

        return message

    def process_trends_for_creator(self, creator: CreatorProfile, trends: List[TrendData]) -> List[ContentBrief]:
        """
        Process multiple trends for a single creator and return matching briefs.

        Args:
            creator: The creator profile
            trends: List of trend data to evaluate

        Returns:
            List of ContentBrief objects for matching trends with TSS >= 50
        """
        briefs = []

        for trend in trends:
            # Skip low-score trends
            if trend.tss_score < self.MEDIUM_THRESHOLD:
                continue

            # Check if trend matches creator's niche
            is_match, confidence = self.match_trend_to_creator(trend, creator)
            if not is_match:
                continue

            # Check if already sent this theme
            if self.has_seen_trend(creator.creator_id, trend.title):
                continue

            # Generate brief
            brief = self.generate_brief(trend, creator)
            briefs.append(brief)

            # Track that we've processed this trend for this creator
            if creator.creator_id not in self.sent_trends:
                self.sent_trends[creator.creator_id] = set()
            self.sent_trends[creator.creator_id].add(trend.title)

        return briefs


def main():
    """Example usage of the Creedom Agent."""
    agent = CreedomAgent()

    # Example: Create sample trend data
    now = datetime.now(datetime.UTC if hasattr(datetime, 'UTC') else None)
    if now.tzinfo is None:
        now = datetime.utcnow()
    sample_trend = TrendData(
        post_id="abc123",
        title="Revolutionary AI tool changes content creation forever",
        subreddit="technology",
        score=5000,
        num_comments=1500,
        created_utc=now.timestamp() - 7200,  # 2 hours ago
        url="https://reddit.com/r/technology/abc123",
        selftext="An amazing new AI tool has emerged..."
    )

    # Calculate trend metrics
    sample_trend.velocity = agent.calculate_velocity(sample_trend.created_utc, sample_trend.score)
    sample_trend.comment_ratio = agent.calculate_comment_ratio(sample_trend.num_comments, sample_trend.score)
    sample_trend.emotional_score = agent.detect_emotional_language(sample_trend.title + " " + sample_trend.selftext)
    sample_trend.tss_score = agent.score_trend(sample_trend)

    print(f"Trend: {sample_trend.title}")
    print(f"TSS Score: {sample_trend.tss_score}")
    print(f"Velocity: {sample_trend.velocity:.2f} score/hour")
    print(f"Comment Ratio: {sample_trend.comment_ratio:.2f}")
    print(f"Emotional Score: {sample_trend.emotional_score:.2f}")

    # Example: Create sample creator profile
    sample_creator = CreatorProfile(
        creator_id="creator_001",
        niche="AI technology content creation",
        platform="instagram",
        style="educational reels",
        follower_count=50000,
        audience_age="25-35",
        past_performance={'avg_engagement': 0.045}
    )

    # Check match
    is_match, confidence = agent.match_trend_to_creator(sample_trend, sample_creator)
    print(f"\nMatch for creator: {is_match} (confidence: {confidence:.2f})")

    if is_match:
        # Generate brief
        brief = agent.generate_brief(sample_trend, sample_creator)
        print("\nGenerated Brief:")
        print(json.dumps(asdict(brief), indent=2))

        # Create and send nudge
        message = agent.create_nudge_message(brief, "Alex")
        print("\nNudge Message:")
        print(message)

        # Log signal
        agent.log_signal(sample_trend, sample_creator.creator_id)


if __name__ == "__main__":
    main()
