# Trend Intelligence System – Setup Guide

## Overview

This system automatically tracks trending content from **YouTube Shorts** and **Instagram Reels**
for up to 4 hashtags/topics. It produces daily Markdown reports and stores raw data in CSV or JSON format.

> **Non-technical users:** Follow the step-by-step sections below.  
> **Developers:** See the module-level docstrings in each `trend_tracker/*.py` file.

---

## Folder Structure

```
.
├── trend_tracker/          Core Python package
│   ├── config.py           Reads settings from .env
│   ├── youtube_tracker.py  YouTube Data API v3 integration
│   ├── instagram_tracker.py Instagram Graph API + scraping fallback
│   ├── data_storage.py     Saves/loads CSV and JSON files
│   ├── report_generator.py Generates Markdown trend reports
│   ├── scheduler.py        Wraps the `schedule` library for daily/weekly runs
│   └── tests/              Unit and integration tests
├── run_tracker.py          Main entry-point (run-now / schedule / report)
├── .env.example            Template – copy to .env and fill in your credentials
├── requirements.txt        Python dependencies
├── SETUP.md                This file
└── MAKE_ZAPIER_GUIDE.md    No-code workflow templates
```

---

## Prerequisites

| Requirement | Minimum Version |
|-------------|----------------|
| Python      | 3.9+           |
| pip         | 21+            |

---

## 1 – Clone the Repository

```bash
git clone https://github.com/maheshk-product/Creedom-Ai-Inteligence-agent.git
cd Creedom-Ai-Inteligence-agent
```

---

## 2 – Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3 – Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` in a text editor (Notepad on Windows, TextEdit on Mac) and fill in:

### 3a – YouTube Data API Key (required for YouTube tracking)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project → **APIs & Services → Library**
3. Search for **YouTube Data API v3** → Enable it
4. Go to **APIs & Services → Credentials → Create Credentials → API Key**
5. Copy the key and paste it as `YOUTUBE_API_KEY=<your_key>` in `.env`

Free tier: **10,000 units/day** (~25 full collection runs per day for 4 topics).

### 3b – Instagram Graph API (optional, requires Instagram Business account)

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new App (Business type)
3. Add the **Instagram Graph API** product
4. Complete the Instagram Business account linking flow
5. Generate a long-lived access token
6. Paste values in `.env`:
   ```
   INSTAGRAM_ACCESS_TOKEN=<token>
   INSTAGRAM_USER_ID=<your_numeric_instagram_user_id>
   ```

> **Note:** If you skip this step, the system will fall back to public web scraping,
> which works but is less reliable and subject to Instagram's Terms of Service.

### 3c – Choose Your Topics

Edit the `TRENDING_TOPICS` line in `.env`:

```
TRENDING_TOPICS=fitness,travel,cooking,technology
```

You can track up to **4 topics** for free-tier API limits.

---

## 4 – Run the System

### Run once immediately

```bash
python run_tracker.py --run-now
```

This fetches data for all configured topics and prints a Markdown report to the terminal.
Reports are saved to the `reports/` folder, and raw data is saved to the `data/` folder.

### Print today's report (without fetching new data)

```bash
python run_tracker.py --report
```

### Start the automated daily scheduler

```bash
python run_tracker.py --schedule
```

This starts a background loop that will run the collection pipeline every day
at the time set by `RUN_TIME` in `.env` (default: `08:00`).

> **Tip for always-on scheduling:** Use a free cloud VM (Google Cloud Free Tier, Oracle Always Free)
> or run inside a Docker container / GitHub Actions workflow.

---

## 5 – Schedule with Cron (Linux / macOS)

```bash
# Edit crontab
crontab -e

# Add this line to run daily at 8:00 AM
0 8 * * * cd /path/to/Creedom-Ai-Inteligence-agent && python run_tracker.py --run-now >> logs/cron.log 2>&1
```

---

## 6 – Review Reports

Reports are generated in the `reports/` folder as Markdown files:

```
reports/
└── report_2024-01-15.md
```

Open any `.md` file in a Markdown viewer, GitHub, Notion, or VS Code to read it.

---

## 7 – Data Storage

Raw trend data is stored in the `data/` folder:

```
data/
└── trends_2024-01-15.csv   (or .json if STORAGE_FORMAT=json)
```

Each daily file can be opened in Excel, Google Sheets, or imported into Airtable.

---

## 8 – Scaling to SaaS

When you're ready to turn this into a multi-tenant SaaS product:

1. **Host on a VPS** – DigitalOcean / Linode / Railway (all have free or cheap tiers)
2. **Add a web dashboard** – Streamlit (free), Retool, or a custom Next.js frontend
3. **Per-user API keys** – Each customer connects their own YouTube/Instagram credentials
4. **Email delivery** – Integrate SendGrid or Mailgun to email reports automatically
5. **Payments** – Stripe Billing for freemium model (3 topics free, unlimited paid)

---

## 9 – Running Tests

```bash
pytest trend_tracker/tests/ -v
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `YOUTUBE_API_KEY is not set` warning | Add your API key to `.env` |
| YouTube API returns 403 | Check your API key is valid and YouTube Data API v3 is enabled |
| Instagram returns empty results | Ensure `INSTAGRAM_ACCESS_TOKEN` is a **long-lived** token (not short-lived) |
| No data in report | Run `--run-now` first to collect data before generating a report |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
