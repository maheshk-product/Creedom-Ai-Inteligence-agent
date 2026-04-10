# No-Code Automation Guide – Make.com & Zapier

This guide explains how to run the Trend Intelligence System **without writing any code**
using Make.com (formerly Integromat) or Zapier.

---

## Option A – Make.com (Recommended for free tier)

Make.com's free tier includes **1,000 operations/month** and supports HTTP module calls.

### Prerequisites

- A Make.com account (free at [make.com](https://www.make.com/))
- Your YouTube API key (see `SETUP.md → Step 3a`)
- (Optional) Instagram Graph API token

---

### Scenario 1: Daily YouTube Shorts Trend Collection

This scenario runs every morning, fetches trending YouTube Shorts,
and appends the results to a Google Sheet.

#### Modules to add (in order)

| Step | Module | Configuration |
|------|--------|--------------|
| 1 | **Schedule** | Set to *Every day* at 08:00 |
| 2 | **HTTP → Make a request** | YouTube search (see below) |
| 3 | **JSON → Parse JSON** | Parse the response body |
| 4 | **Iterator** | Iterate over `items` array |
| 5 | **Google Sheets → Add a Row** | Write each video to a spreadsheet |

#### YouTube API Request (Step 2)

```
URL:     https://www.googleapis.com/youtube/v3/search
Method:  GET
Query String Parameters:
  part          = snippet
  q             = fitness shorts
  type          = video
  videoDuration = short
  order         = viewCount
  maxResults    = 10
  key           = YOUR_YOUTUBE_API_KEY
```

Repeat this scenario (duplicate it) for each of your 4 topics:
`fitness`, `travel`, `cooking`, `technology`.

#### Google Sheet columns

| fetched_at | topic | video_id | title | channel | url | published_at |
|-----------|-------|----------|-------|---------|-----|-------------|

---

### Scenario 2: Daily Instagram Hashtag Tracking

> **Note:** Instagram's official API requires a Business account.
> If you don't have one, use the HTTP module to call a hosted instance of
> this Python app instead (see Scenario 3 below).

| Step | Module | Configuration |
|------|--------|--------------|
| 1 | **Schedule** | Every day at 08:15 |
| 2 | **HTTP → Make a request** | Instagram hashtag search (see below) |
| 3 | **JSON → Parse JSON** | Parse response |
| 4 | **Iterator** | Iterate over `data` array |
| 5 | **Google Sheets → Add a Row** | Append reel data |

#### Instagram Graph API Request (Step 2 – hashtag search)

```
URL:     https://graph.instagram.com/ig_hashtag_search
Method:  GET
Query String Parameters:
  user_id      = YOUR_INSTAGRAM_USER_ID
  q            = fitness
  access_token = YOUR_INSTAGRAM_ACCESS_TOKEN
```

Then use the returned `id` in a second HTTP call to get recent media:

```
URL:     https://graph.instagram.com/{hashtag_id}/recent_media
Method:  GET
Query String Parameters:
  user_id      = YOUR_INSTAGRAM_USER_ID
  fields       = id,media_type,permalink,like_count,comments_count,timestamp
  access_token = YOUR_INSTAGRAM_ACCESS_TOKEN
```

---

### Scenario 3: Trigger Python App via Webhook

If you host the Python app on a server (e.g., Railway, Render, Fly.io – all have free tiers),
you can trigger a collection run from Make.com using a simple HTTP call:

| Step | Module | Configuration |
|------|--------|--------------|
| 1 | **Schedule** | Every day at 08:00 |
| 2 | **HTTP → Make a request** | POST to `https://your-app-url/run` |

Your server should expose a `/run` endpoint that calls `run_full_pipeline()`.

---

### Scenario 4: Weekly Email Report

| Step | Module | Configuration |
|------|--------|--------------|
| 1 | **Schedule** | Every Monday at 09:00 |
| 2 | **Google Sheets → Get All Rows** | Read last 7 days of data |
| 3 | **Text aggregator** | Combine rows into Markdown table |
| 4 | **Email → Send an Email** | Send to yourself / customers |

---

## Option B – Zapier

Zapier's free tier supports **100 tasks/month** across **5 Zaps**.

### Zap 1: Collect YouTube Trends Daily

| Step | App | Event | Configuration |
|------|-----|-------|--------------|
| 1 | Schedule by Zapier | Every Day | 8:00 AM |
| 2 | Webhooks by Zapier | GET | YouTube search URL (see above) |
| 3 | Google Sheets | Create Spreadsheet Row | Map JSON fields |

### Zap 2: Collect Instagram Trends Daily

Same pattern as Zap 1 but using the Instagram Graph API URL.

### Zap 3: Weekly Summary Email

| Step | App | Event |
|------|-----|-------|
| 1 | Schedule by Zapier | Every Week (Monday) |
| 2 | Google Sheets | Get Many Spreadsheet Rows |
| 3 | Gmail / Email by Zapier | Send Email |

---

## Google Sheets Template

Create a Google Sheet with two tabs:

### Tab 1: `youtube_trends`

| Column | Description |
|--------|-------------|
| A | fetched_at |
| B | topic |
| C | video_id |
| D | title |
| E | channel |
| F | url |
| G | published_at |
| H | view_count |
| I | like_count |
| J | comment_count |

### Tab 2: `instagram_trends`

| Column | Description |
|--------|-------------|
| A | fetched_at |
| B | topic |
| C | reel_id |
| D | url |
| E | like_count |
| F | comment_count |
| G | published_at |
| H | source |

---

## Tips for Staying Within Free Tier Limits

| Service | Free Limit | Our Usage |
|---------|-----------|-----------|
| YouTube Data API v3 | 10,000 units/day | ~400 units/day (4 topics) |
| Instagram Graph API | 200 unique hashtags/7 days | 4 hashtags ✅ |
| Make.com | 1,000 ops/month | ~120 ops/month (4 topics/day) |
| Zapier | 100 tasks/month | ~60 tasks/month (2 sources/day) |

> **Pro tip:** Run your collection once per day in the morning.
> Weekly reports use very few operations.

---

## Upgrading to SaaS

Once you're ready to offer this as a paid service:

1. **Host the Python app** on Railway, Render, or Fly.io (all free-to-start)
2. **Build a customer portal** with Bubble, Webflow, or Softr (no-code)
3. **Charge per seat** using Stripe's no-code payment links
4. **White-label the reports** by customising `report_generator.py`
5. **Add more data sources** (TikTok, Twitter/X, Reddit) following the same pattern
