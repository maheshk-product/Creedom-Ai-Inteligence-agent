# Creedom AI Intelligence Agent

An AI agent built for content creators to detect trending topics before they go viral, match them to creator niches, and deliver actionable content briefs.

## Overview

Creedom Intelligence is designed to serve solo creators, educators, and social commerce sellers on Instagram, YouTube, and LinkedIn — primarily in fitness, finance, education, and entertainment niches (1k–100k followers).

## Features

### 🎯 Core Capabilities

- **Trend Detection**: Scans Reddit for emerging trends using velocity-based analysis
- **TSS Scoring**: Proprietary Trend Scoring System (0-100) based on:
  - Velocity (posts/hr) × 35%
  - Comment-to-upvote ratio × 25%
  - Subreddit size weight × 15%
  - Emotional language detection × 15%
  - Cross-subreddit spread × 10%
- **Creator Matching**: Matches trends to creator niches with confidence scoring
- **Content Brief Generation**: Produces actionable, personalized content briefs
- **Smart Nudging**: Sends alerts via WhatsApp or email with 3-day cooldown
- **Intelligence Logging**: Tracks all signals for learning and optimization

### 📊 TSS Tiers

- **85–100 (CRITICAL)**: Alert same day - act within 12-24 hours
- **70–84 (HIGH)**: Alert next morning - act in 5-7 days
- **50–69 (MEDIUM)**: Add to watchlist - act within 2 weeks
- **Below 50 (NOISE)**: Ignore

## 🚀 Quick Start for Beginners

**New to coding?** No problem! We've got you covered.

### 🆕 Super Simple Mode (NO Reddit API Setup Required!)

**Want to try this RIGHT NOW without ANY setup?** Use Simple Mode!

```bash
# 1. Clone the repository
git clone https://github.com/maheshk-product/Creedom-Ai-Inteligence-agent.git
cd Creedom-Ai-Inteligence-agent

# 2. Install dependencies (all FREE)
pip install -r requirements.txt

# 3. Set up simple configuration (NO Reddit API needed!)
cp config_simple_template.py config_simple.py
# Edit config_simple.py - only needs your email settings!

# 4. Run the simple agent
python run_agent_simple.py
```

**Simple Mode Features:**
- ✅ No Reddit API credentials needed
- ✅ Uses public Reddit JSON feeds
- ✅ All features work the same (TSS scoring, email alerts, etc.)
- ⚠️ Slightly slower and subject to stricter rate limits
- ⚠️ Can only access public subreddits

**Perfect for:** Testing the agent, learning how it works, or if you don't want to set up Reddit API credentials.

---

### Option 1: Automated Setup (Recommended)

**Windows:**
```bash
install.bat
```

**Mac/Linux:**
```bash
./install.sh
```

The script will:
- ✅ Check Python installation
- ✅ Install all required libraries (free)
- ✅ Create configuration template
- ✅ Guide you through setup

### Option 2: Manual Setup

```bash
# 1. Clone the repository
git clone https://github.com/maheshk-product/Creedom-Ai-Inteligence-agent.git
cd Creedom-Ai-Inteligence-agent

# 2. Install dependencies (all FREE)
pip install -r requirements.txt

# 3. Set up configuration
cp config_template.py config.py
# Edit config.py with your credentials (see SETUP_GUIDE.md)

# 4. Run the agent
python run_agent.py
```

### 📖 Complete Beginner's Guide

**Never coded before?** Start here:
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Step-by-step instructions for complete beginners (written for 8th graders!)
- **[GITHUB_ACTIONS_GUIDE.md](GITHUB_ACTIONS_GUIDE.md)** - Run the agent in the cloud 24/7 for FREE

### 💰 Cost: $0.00

Everything you need is FREE:
- ✅ Reddit API - Free (60 requests/min)
- ✅ Email notifications - Free Gmail SMTP (500/day)
- ✅ Database - Free SQLite (built-in)
- ✅ Cloud hosting - Free GitHub Actions (2,000 min/month)
- ✅ Python & libraries - Free & open source

## Quick Start (For Developers)

```python
from creedom_agent import CreedomAgent, TrendData, CreatorProfile
from datetime import datetime

# Initialize agent
agent = CreedomAgent()

# Create sample trend data
trend = TrendData(
    post_id="abc123",
    title="Revolutionary AI tool changes content creation forever",
    subreddit="technology",
    score=5000,
    num_comments=1500,
    created_utc=datetime.utcnow().timestamp() - 7200,  # 2 hours ago
    url="https://reddit.com/r/technology/abc123",
    selftext="An amazing new AI tool has emerged..."
)

# Calculate trend metrics
trend.velocity = agent.calculate_velocity(trend.created_utc, trend.score)
trend.comment_ratio = agent.calculate_comment_ratio(trend.num_comments, trend.score)
trend.emotional_score = agent.detect_emotional_language(trend.title + " " + trend.selftext)
trend.tss_score = agent.score_trend(trend)

print(f"TSS Score: {trend.tss_score}")

# Create creator profile
creator = CreatorProfile(
    creator_id="creator_001",
    niche="technology",
    platform="instagram",
    style="educational reels",
    follower_count=50000,
    audience_age="25-35",
    past_performance={'avg_engagement': 0.045}
)

# Match and generate brief
is_match, confidence = agent.match_trend_to_creator(trend, creator)
if is_match:
    brief = agent.generate_brief(trend, creator)
    print(f"Brief: {brief.content_idea}")

    # Send nudge
    message = agent.create_nudge_message(brief, "Creator Name")
    agent.send_nudge(creator.creator_id, message, channel='whatsapp')
```

## Usage Example

Run the included example:

```bash
python creedom_agent.py
```

This will demonstrate:
1. Trend scoring with sample data
2. Creator profile matching
3. Content brief generation
4. Nudge message creation

## API Reference

### Main Methods

#### `scan_reddit(subreddit, limit)`
Scans Reddit for potential trending topics.

#### `score_trend(trend_data, subreddit_subscribers)`
Calculates TSS score (0-100) for a trend.

#### `match_trend_to_creator(trend_data, creator)`
Determines if trend matches creator's niche. Returns `(is_match, confidence)`.

#### `generate_brief(trend_data, creator)`
Generates personalized content brief with hook, idea, and urgency.

#### `send_nudge(creator_id, message, channel)`
Sends nudge via WhatsApp or email (respects 3-day cooldown).

#### `process_trends_for_creator(creator, trends)`
Processes multiple trends and returns matching briefs (TSS ≥ 50).

### Data Structures

#### `TrendData`
- `post_id`: Unique identifier
- `title`: Post title
- `subreddit`: Subreddit name
- `score`: Upvote score
- `num_comments`: Comment count
- `created_utc`: Creation timestamp
- `velocity`: Score per hour
- `tss_score`: Calculated TSS score

#### `CreatorProfile`
- `creator_id`: Unique identifier
- `niche`: Content niche (e.g., "fitness", "finance")
- `platform`: Social platform (e.g., "instagram", "youtube")
- `style`: Content style
- `follower_count`: Number of followers

#### `ContentBrief`
- `trend_theme`: Brief description (max 15 words)
- `why_it_matters`: Psychology explanation
- `hook_line`: Opening line for content
- `content_idea`: Niche-specific suggestion
- `urgency_window`: Time to act
- `tss_score`: Trend score
- `recommended_format`: Content format (reel, carousel, etc.)

## Testing

Run the test suite:

```bash
python test_creedom_agent.py
```

Or with pytest:

```bash
pip install pytest
pytest test_creedom_agent.py -v
```

Tests cover:
- TSS scoring algorithm
- Velocity calculation
- Comment ratio analysis
- Emotional language detection
- Creator matching
- Brief generation
- Nudge cooldown logic
- Trend deduplication

## Design Principles

### What Creedom Never Does
- Never recommend trends with TSS below 50
- Never send nudges without personalized content ideas
- Never repeat the same trend theme to the same creator
- Never be vague — every output is actionable within 30 minutes

### Output Philosophy
A creator should open your nudge, read it in 30 seconds, and immediately know exactly what to post and why. If they need to think too hard — you failed.

## Roadmap

- [x] Reddit API integration with PRAW
- [x] Public JSON Reddit scanner (no auth alternative)
- [x] Database backend for creator profiles and signals
- [x] Email service integration (Gmail SMTP)
- [ ] WhatsApp Business API integration
- [ ] Cross-subreddit trend detection
- [ ] Machine learning for improved niche matching
- [ ] Dashboard for trend monitoring
- [ ] Historical performance tracking
- [ ] A/B testing for hook lines

## Architecture

The agent follows a modular design:

1. **Scanner Module**: Fetches data from Reddit (two modes available)
2. **Scoring Engine**: Calculates TSS scores
3. **Matching Engine**: Maps trends to creators
4. **Brief Generator**: Creates actionable content
5. **Nudge System**: Handles notifications with cooldown
6. **Intelligence DB**: Logs signals for learning

### Two Scanning Modes

#### Full Mode (`run_agent.py`)
- Uses Reddit API (PRAW) with authentication
- Requires Reddit API credentials (free but needs setup)
- Faster and more reliable
- 60 requests per minute
- **Best for:** Regular use, production deployments

**Files:**
- `run_agent.py` - Main runner with full Reddit API
- `config_template.py` → `config.py` - Full configuration

#### Simple Mode (`run_agent_simple.py`)
- Uses Reddit's public JSON feeds (no auth)
- No Reddit API credentials needed
- Slightly slower, stricter rate limits
- Can only access public subreddits
- **Best for:** Testing, learning, quick setup

**Files:**
- `run_agent_simple.py` - Simple runner without authentication
- `reddit_scanner_simple.py` - Public JSON scanner
- `config_simple_template.py` → `config_simple.py` - Simplified configuration

Both modes provide:
- ✅ TSS scoring
- ✅ Creator matching
- ✅ Content brief generation
- ✅ Email notifications
- ✅ SQLite database logging

## Contributing

Contributions are welcome! Please ensure:
- Code follows existing style
- All tests pass
- New features include tests
- Documentation is updated

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Credits

Built for content creators who need to stay ahead of trends without burning out.
