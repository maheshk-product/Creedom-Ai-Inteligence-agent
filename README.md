# Creedom AI Intelligence Agent

**Trend Intelligence System for YouTube Shorts & Instagram Reels**

Automatically track 3–4 trending topics/hashtags across YouTube Shorts and Instagram Reels.
Generates daily Markdown trend reports and stores raw engagement data as CSV or JSON —
all within the free tier of both APIs.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure your API keys
cp .env.example .env
# Edit .env with your YouTube API key and (optionally) Instagram credentials

# 3. Run a single collection cycle and print the report
python run_tracker.py --run-now

# 4. Or start the daily scheduler (runs at the time set in .env)
python run_tracker.py --schedule
```

## Documentation

| Document | Description |
|----------|-------------|
| [SETUP.md](SETUP.md) | Full setup guide: API keys, Python installation, cron scheduling |
| [MAKE_ZAPIER_GUIDE.md](MAKE_ZAPIER_GUIDE.md) | No-code workflow templates for Make.com and Zapier |

## Features

- ✅ YouTube Shorts trending search via YouTube Data API v3 (free, ~400 units/day for 4 topics)
- ✅ Instagram Reels hashtag tracking via Graph API with public web fallback
- ✅ CSV and JSON storage with daily date-partitioned files
- ✅ Auto-generated Markdown trend reports with engagement summaries
- ✅ Built-in scheduler (daily or weekly) — or use cron / Make.com / Zapier
- ✅ Non-technical friendly: configure topics in `.env`, no coding required
- ✅ Designed to scale into a SaaS product

## Running Tests

```bash
pytest trend_tracker/tests/ -v
```
