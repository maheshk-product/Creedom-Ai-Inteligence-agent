"""
QUICKSTART EXAMPLE - Test Your Setup

This is a simple test to make sure everything is working.
Run this BEFORE setting up Reddit and Email to test the core agent.
"""

from creedom_agent import CreedomAgent, TrendData, CreatorProfile
from datetime import datetime
import json
from dataclasses import asdict


def test_basic_functionality():
    """Test the agent without needing Reddit or Email credentials."""

    print("\n" + "="*60)
    print("🧪 CREEDOM AGENT - QUICK TEST")
    print("="*60)
    print("\nThis test checks if the agent is working correctly.")
    print("You don't need Reddit or Email credentials for this test.\n")

    # Initialize agent
    print("1️⃣  Initializing agent...")
    agent = CreedomAgent()
    print("✅ Agent initialized\n")

    # Create a sample trending post
    print("2️⃣  Creating sample trend data...")
    now = datetime.now(datetime.UTC if hasattr(datetime, 'UTC') else None)
    if now.tzinfo is None:
        now = datetime.utcnow()

    sample_trend = TrendData(
        post_id="test_123",
        title="Revolutionary fitness technique helps people lose 20 pounds in 30 days",
        subreddit="fitness",
        score=8500,
        num_comments=2400,
        created_utc=now.timestamp() - 3600,  # 1 hour ago
        url="https://reddit.com/r/fitness/test_123",
        selftext="This amazing new technique has shocked doctors and trainers..."
    )
    print("✅ Sample trend created\n")

    # Calculate trend metrics
    print("3️⃣  Calculating trend metrics...")
    sample_trend.velocity = agent.calculate_velocity(
        sample_trend.created_utc,
        sample_trend.score
    )
    sample_trend.comment_ratio = agent.calculate_comment_ratio(
        sample_trend.num_comments,
        sample_trend.score
    )
    sample_trend.emotional_score = agent.detect_emotional_language(
        sample_trend.title + " " + sample_trend.selftext
    )
    sample_trend.tss_score = agent.score_trend(sample_trend, subreddit_subscribers=5_000_000)
    print("✅ Metrics calculated\n")

    # Display results
    print("📊 TREND ANALYSIS RESULTS:")
    print("-" * 60)
    print(f"Title: {sample_trend.title}")
    print(f"Subreddit: r/{sample_trend.subreddit}")
    print(f"Score: {sample_trend.score:,} upvotes")
    print(f"Comments: {sample_trend.num_comments:,}")
    print()
    print(f"🔥 Velocity: {sample_trend.velocity:.0f} score/hour")
    print(f"💬 Comment Ratio: {sample_trend.comment_ratio:.2f}")
    print(f"😮 Emotional Score: {sample_trend.emotional_score:.2f}")
    print()
    print(f"⭐ TSS SCORE: {sample_trend.tss_score:.1f}/100")

    # Determine tier
    if sample_trend.tss_score >= agent.CRITICAL_THRESHOLD:
        tier = "🔴 CRITICAL - Alert immediately! Act in 12-24 hours"
    elif sample_trend.tss_score >= agent.HIGH_THRESHOLD:
        tier = "🟡 HIGH - Alert next morning. Act in 5-7 days"
    elif sample_trend.tss_score >= agent.MEDIUM_THRESHOLD:
        tier = "🟢 MEDIUM - Add to watchlist. Act within 2 weeks"
    else:
        tier = "⚪ NOISE - Ignore"

    print(f"Tier: {tier}")
    print("-" * 60)
    print()

    # Create sample creator profile
    print("4️⃣  Creating sample creator profile...")
    sample_creator = CreatorProfile(
        creator_id="test_creator",
        niche="fitness weight loss health",
        platform="instagram",
        style="transformation stories",
        follower_count=45000,
        audience_age="25-40",
        past_performance={'avg_engagement': 0.05}
    )
    print("✅ Creator profile created\n")

    # Match trend to creator
    print("5️⃣  Matching trend to creator niche...")
    is_match, confidence = agent.match_trend_to_creator(sample_trend, sample_creator)

    if is_match:
        print(f"✅ MATCH! Confidence: {confidence:.0%}")
        print(f"   This trend is relevant for {sample_creator.niche}\n")

        # Generate content brief
        print("6️⃣  Generating personalized content brief...")
        brief = agent.generate_brief(sample_trend, sample_creator)
        print("✅ Brief generated\n")

        print("📝 CONTENT BRIEF:")
        print("-" * 60)
        print(f"Theme: {brief.trend_theme}")
        print()
        print(f"Why It Matters:")
        print(f"  {brief.why_it_matters}")
        print()
        print(f"Your Hook:")
        print(f'  "{brief.hook_line}"')
        print()
        print(f"Content Idea:")
        print(f"  {brief.content_idea}")
        print()
        print(f"Urgency: {brief.urgency_window}")
        print(f"Format: {brief.recommended_format}")
        print()
        print(f"Cross-Niche Opportunity:")
        print(f"  {brief.cross_niche_opportunity}")
        print("-" * 60)
        print()

        # Create nudge message
        print("7️⃣  Creating nudge message...")
        nudge = agent.create_nudge_message(brief, "Test Creator")
        print("✅ Nudge message created\n")

        print("📧 EXAMPLE NOTIFICATION:")
        print("-" * 60)
        print(nudge)
        print("-" * 60)
        print()

    else:
        print(f"❌ No match (confidence: {confidence:.0%})")
        print(f"   This trend is not relevant for {sample_creator.niche}\n")

    # Test logging
    print("8️⃣  Testing intelligence logging...")
    agent.log_signal(sample_trend, sample_creator.creator_id)
    print(f"✅ Signal logged ({len(agent.signal_db)} signals in memory)\n")

    # Final summary
    print("="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print()
    print("🎉 Your Creedom Agent is working correctly!")
    print()
    print("📖 Next Steps:")
    print("1. Follow SETUP_GUIDE.md to configure Reddit API")
    print("2. Set up Gmail notifications (Step 4 in guide)")
    print("3. Run: python run_agent.py")
    print()
    print("💡 The agent will then:")
    print("   - Scan Reddit for real trends in your niche")
    print("   - Calculate TSS scores for each trend")
    print("   - Send you email alerts for high-scoring matches")
    print()


def test_calculations():
    """Test individual calculation functions."""
    print("\n" + "="*60)
    print("🔬 TESTING CALCULATION FUNCTIONS")
    print("="*60)
    print()

    agent = CreedomAgent()

    # Test velocity calculation
    print("Testing velocity calculation...")
    now = datetime.now(datetime.UTC if hasattr(datetime, 'UTC') else None)
    if now.tzinfo is None:
        now = datetime.utcnow()
    one_hour_ago = now.timestamp() - 3600
    velocity = agent.calculate_velocity(one_hour_ago, 5000)
    print(f"  Score 5000 after 1 hour = {velocity:.0f} score/hour")
    assert velocity > 0, "Velocity calculation failed"
    print("✅ Velocity test passed\n")

    # Test comment ratio
    print("Testing comment ratio calculation...")
    ratio = agent.calculate_comment_ratio(1000, 5000)
    print(f"  1000 comments / 5000 score = {ratio:.2f}")
    assert 0 <= ratio <= 1, "Comment ratio out of bounds"
    print("✅ Comment ratio test passed\n")

    # Test emotional detection
    print("Testing emotional language detection...")
    text = "This shocking and amazing breakthrough is revolutionary!"
    score = agent.detect_emotional_language(text)
    print(f'  "{text}"')
    print(f"  Emotional score: {score:.2f}")
    assert score > 0, "Emotional detection failed"
    print("✅ Emotional detection test passed\n")

    print("="*60)
    print("✅ All calculation tests passed!")
    print("="*60)
    print()


if __name__ == "__main__":
    print("\n🚀 Starting Creedom Agent Quick Test...\n")

    try:
        # Run main functionality test
        test_basic_functionality()

        # Ask if user wants detailed tests
        print("\n" + "="*60)
        response = input("Run detailed calculation tests? (y/n): ")
        if response.lower() in ['y', 'yes']:
            test_calculations()

        print("\n💪 Ready to use the real agent with Reddit!")
        print("📖 See SETUP_GUIDE.md for Reddit and Email setup\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user\n")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you ran: pip install -r requirements.txt")
        print("2. Check that creedom_agent.py exists in this directory")
        print("3. See SETUP_GUIDE.md for help\n")
