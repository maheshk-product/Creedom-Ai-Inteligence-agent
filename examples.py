"""
Example Usage: Creedom Intelligence Agent

This file demonstrates various use cases for the Creedom Intelligence Agent.
"""

from creedom_agent import (
    CreedomAgent,
    TrendData,
    CreatorProfile,
    ContentBrief
)
from datetime import datetime, timedelta
import json
from dataclasses import asdict


def example_1_basic_trend_scoring():
    """Example 1: Basic trend scoring and evaluation."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Trend Scoring")
    print("=" * 60)

    agent = CreedomAgent()

    # Simulate a trending Reddit post
    now = datetime.now(datetime.UTC if hasattr(datetime, 'UTC') else None)
    if now.tzinfo is None:
        now = datetime.utcnow()

    trend = TrendData(
        post_id="reddit_123",
        title="BREAKING: New AI breakthrough achieves human-level reasoning",
        subreddit="artificialintelligence",
        score=8500,
        num_comments=3200,
        created_utc=now.timestamp() - 1800,  # 30 minutes ago (high velocity!)
        url="https://reddit.com/r/artificialintelligence/123",
        selftext="Researchers at MIT have announced a shocking breakthrough..."
    )

    # Calculate metrics
    trend.velocity = agent.calculate_velocity(trend.created_utc, trend.score)
    trend.comment_ratio = agent.calculate_comment_ratio(trend.num_comments, trend.score)
    trend.emotional_score = agent.detect_emotional_language(trend.title + " " + trend.selftext)
    trend.tss_score = agent.score_trend(trend, subreddit_subscribers=2_000_000)

    print(f"\nTrend: {trend.title}")
    print(f"TSS Score: {trend.tss_score} (CRITICAL TIER)" if trend.tss_score >= 85 else f"TSS Score: {trend.tss_score}")
    print(f"Velocity: {trend.velocity:.0f} score/hour")
    print(f"Comment Ratio: {trend.comment_ratio:.2f}")
    print(f"Emotional Score: {trend.emotional_score:.2f}")

    if trend.tss_score >= agent.CRITICAL_THRESHOLD:
        print("⚠️  CRITICAL - Alert creator immediately!")
    elif trend.tss_score >= agent.HIGH_THRESHOLD:
        print("📈 HIGH - Alert next morning")
    elif trend.tss_score >= agent.MEDIUM_THRESHOLD:
        print("👀 MEDIUM - Add to watchlist")
    else:
        print("🔇 NOISE - Ignore")

    print()


def example_2_creator_matching():
    """Example 2: Matching trends to creator niches."""
    print("=" * 60)
    print("EXAMPLE 2: Creator Matching")
    print("=" * 60)

    agent = CreedomAgent()

    # Create sample trends
    now = datetime.now(datetime.UTC if hasattr(datetime, 'UTC') else None)
    if now.tzinfo is None:
        now = datetime.utcnow()

    trends = [
        TrendData(
            post_id="fit_001",
            title="Doctor reveals the one exercise that burns fat faster than running",
            subreddit="fitness",
            score=4500,
            num_comments=1200,
            created_utc=now.timestamp() - 3600,
            url="https://reddit.com/r/fitness/001"
        ),
        TrendData(
            post_id="tech_001",
            title="ChatGPT competitor launches with mind-blowing new features",
            subreddit="technology",
            score=6200,
            num_comments=1800,
            created_utc=now.timestamp() - 5400,
            url="https://reddit.com/r/technology/001"
        ),
    ]

    # Calculate metrics for all trends
    for trend in trends:
        trend.velocity = agent.calculate_velocity(trend.created_utc, trend.score)
        trend.comment_ratio = agent.calculate_comment_ratio(trend.num_comments, trend.score)
        trend.emotional_score = agent.detect_emotional_language(trend.title)
        trend.tss_score = agent.score_trend(trend)

    # Create fitness creator
    fitness_creator = CreatorProfile(
        creator_id="fit_creator_001",
        niche="fitness weight loss exercise",
        platform="instagram",
        style="transformation stories",
        follower_count=35000,
        audience_age="25-45",
        past_performance={'avg_engagement': 0.055}
    )

    print(f"\nCreator: {fitness_creator.creator_id}")
    print(f"Niche: {fitness_creator.niche}")
    print(f"Platform: {fitness_creator.platform}\n")

    # Check each trend
    for trend in trends:
        is_match, confidence = agent.match_trend_to_creator(trend, fitness_creator)
        status = "✅ MATCH" if is_match else "❌ NO MATCH"
        print(f"{status} (confidence: {confidence:.2f}) - {trend.title[:50]}...")

    print()


def example_3_content_brief_generation():
    """Example 3: Generating personalized content briefs."""
    print("=" * 60)
    print("EXAMPLE 3: Content Brief Generation")
    print("=" * 60)

    agent = CreedomAgent()

    # High-scoring trend
    now = datetime.now(datetime.UTC if hasattr(datetime, 'UTC') else None)
    if now.tzinfo is None:
        now = datetime.utcnow()

    trend = TrendData(
        post_id="fin_001",
        title="Financial advisor exposes the secret banks don't want you to know",
        subreddit="personalfinance",
        score=7200,
        num_comments=2400,
        created_utc=now.timestamp() - 2700,
        url="https://reddit.com/r/personalfinance/001",
        selftext="This shocking revelation about savings accounts..."
    )

    trend.velocity = agent.calculate_velocity(trend.created_utc, trend.score)
    trend.comment_ratio = agent.calculate_comment_ratio(trend.num_comments, trend.score)
    trend.emotional_score = agent.detect_emotional_language(trend.title + " " + trend.selftext)
    trend.tss_score = agent.score_trend(trend, subreddit_subscribers=15_000_000)

    # Finance creator
    finance_creator = CreatorProfile(
        creator_id="fin_creator_001",
        niche="personal finance money management savings",
        platform="youtube",
        style="talking head explainer",
        follower_count=85000,
        audience_age="28-40",
        past_performance={'avg_engagement': 0.062}
    )

    # Generate brief
    brief = agent.generate_brief(trend, finance_creator)

    print(f"\nTSS Score: {brief.tss_score}")
    print(f"\nTREND: {brief.trend_theme}")
    print(f"\nWHY IT MATTERS: {brief.why_it_matters}")
    print(f"\nHOOK LINE: \"{brief.hook_line}\"")
    print(f"\nCONTENT IDEA: {brief.content_idea}")
    print(f"\nURGENCY: {brief.urgency_window}")
    print(f"\nFORMAT: {brief.recommended_format}")
    print(f"\nCROSS-NICHE: {brief.cross_niche_opportunity}")

    print()


def example_4_nudge_system():
    """Example 4: Nudge system with cooldown."""
    print("=" * 60)
    print("EXAMPLE 4: Nudge System with Cooldown")
    print("=" * 60)

    agent = CreedomAgent()

    # Create sample brief
    brief = ContentBrief(
        trend_theme="AI revolution in content creation",
        why_it_matters="Game-changing tech that solves creator burnout",
        hook_line="This AI does in 10 minutes what took me 10 hours",
        content_idea="Show before/after workflow with the new AI tool",
        urgency_window="Act today - 12-24 hours max",
        cross_niche_opportunity="Works for productivity and business creators",
        tss_score=88.0,
        recommended_format="reel"
    )

    creator_id = "creator_nudge_test"

    # Create nudge message
    message = agent.create_nudge_message(brief, "Sarah")
    print(f"\nNudge Message ({len(message.split())} words):")
    print("-" * 50)
    print(message)
    print("-" * 50)

    # Send first nudge
    print("\nAttempt 1: Sending first nudge...")
    result = agent.send_nudge(creator_id, message, channel='whatsapp')
    print(f"Result: {'✅ Sent' if result else '❌ Failed'}")

    # Try to send again immediately
    print("\nAttempt 2: Trying to send again immediately...")
    result = agent.send_nudge(creator_id, message, channel='whatsapp')
    print(f"Result: {'✅ Sent' if result else '❌ Blocked (cooldown active)'}")

    # Simulate cooldown expiry
    print("\nSimulating 4 days passing...")
    agent.nudge_cooldown[creator_id] = agent.nudge_cooldown[creator_id] - timedelta(days=4)

    print("\nAttempt 3: Trying to send after cooldown...")
    result = agent.send_nudge(creator_id, message, channel='email')
    print(f"Result: {'✅ Sent' if result else '❌ Failed'}")

    print()


def example_5_full_workflow():
    """Example 5: Complete workflow - scan, score, match, brief, nudge."""
    print("=" * 60)
    print("EXAMPLE 5: Complete Workflow")
    print("=" * 60)

    agent = CreedomAgent()

    # Simulate multiple trends from scanning
    now = datetime.now(datetime.UTC if hasattr(datetime, 'UTC') else None)
    if now.tzinfo is None:
        now = datetime.utcnow()

    trends = [
        TrendData(
            post_id="edu_001",
            title="Teacher reveals the learning technique that doubled student performance",
            subreddit="education",
            score=5500,
            num_comments=1400,
            created_utc=now.timestamp() - 4200,
            url="https://reddit.com/r/education/001",
            selftext="This amazing technique is backed by research"
        ),
        TrendData(
            post_id="edu_002",
            title="Study shows this one habit makes you 10x more productive",
            subreddit="productivity",
            score=3200,
            num_comments=800,
            created_utc=now.timestamp() - 7200,
            url="https://reddit.com/r/productivity/002",
            selftext="Researchers discovered something incredible"
        ),
        TrendData(
            post_id="noise_001",
            title="Random post with low engagement",
            subreddit="random",
            score=50,
            num_comments=5,
            created_utc=now.timestamp() - 86400,
            url="https://reddit.com/r/random/001"
        ),
    ]

    # Score all trends
    for trend in trends:
        trend.velocity = agent.calculate_velocity(trend.created_utc, trend.score)
        trend.comment_ratio = agent.calculate_comment_ratio(trend.num_comments, trend.score)
        trend.emotional_score = agent.detect_emotional_language(trend.title + " " + trend.selftext)
        trend.tss_score = agent.score_trend(trend)

    # Education creator
    creator = CreatorProfile(
        creator_id="edu_creator_001",
        niche="education learning study techniques productivity",
        platform="linkedin",
        style="carousel with data",
        follower_count=45000,
        audience_age="22-35",
        past_performance={'avg_engagement': 0.048}
    )

    print(f"\nProcessing {len(trends)} trends for creator: {creator.creator_id}")
    print(f"Niche: {creator.niche}\n")

    # Process trends
    briefs = agent.process_trends_for_creator(creator, trends)

    print(f"✅ Generated {len(briefs)} matching brief(s) (filtered {len(trends) - len(briefs)} trends)\n")

    for i, brief in enumerate(briefs, 1):
        print(f"Brief {i}:")
        print(f"  Theme: {brief.trend_theme[:60]}...")
        print(f"  TSS: {brief.tss_score}")
        print(f"  Hook: \"{brief.hook_line[:60]}...\"")
        print(f"  Urgency: {brief.urgency_window}")

        # Send nudge
        message = agent.create_nudge_message(brief, creator.creator_id.split('_')[0].title())
        can_send = agent.can_send_nudge(creator.creator_id)
        if can_send:
            agent.send_nudge(creator.creator_id, message, channel='whatsapp')
            print(f"  📲 Nudge sent via WhatsApp")
        else:
            print(f"  ⏸️  Nudge skipped (cooldown active)")

        # Log signal
        agent.log_signal(trends[i-1], creator.creator_id)
        print()

    print(f"Total signals logged: {len(agent.signal_db)}")
    print()


if __name__ == "__main__":
    example_1_basic_trend_scoring()
    example_2_creator_matching()
    example_3_content_brief_generation()
    example_4_nudge_system()
    example_5_full_workflow()

    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
