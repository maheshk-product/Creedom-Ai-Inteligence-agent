# Choosing Between Full Mode and Simple Mode

Creedom AI Intelligence Agent offers two ways to scan Reddit for trending content. This guide helps you choose which mode is right for you.

## 📊 Quick Comparison

| Feature | **Full Mode** (`run_agent.py`) | **Simple Mode** (`run_agent_simple.py`) |
|---------|-------------------------------|----------------------------------------|
| **Reddit API Credentials** | ✅ Required | ❌ Not required |
| **Setup Difficulty** | Medium (need Reddit app) | Easy (just email) |
| **Speed** | Faster | Slightly slower |
| **Rate Limits** | 60 requests/min | Stricter (varies) |
| **Subreddit Access** | All public subreddits | Public subreddits only |
| **Reliability** | High | Good |
| **TSS Scoring** | ✅ Yes | ✅ Yes |
| **Email Alerts** | ✅ Yes | ✅ Yes |
| **Database Logging** | ✅ Yes | ✅ Yes |
| **Best For** | Production use | Testing, learning |

## 🆕 Simple Mode (Recommended for Beginners)

### When to Use Simple Mode:
- ✅ You're new to coding and want to try this quickly
- ✅ You don't want to set up Reddit API credentials
- ✅ You're testing the agent before committing to full setup
- ✅ You only need to scan a few subreddits occasionally
- ✅ You want to understand how the agent works first

### Setup (5 minutes):
1. Copy `config_simple_template.py` to `config_simple.py`
2. Add your Gmail credentials (for email notifications)
3. Choose your content niche
4. Run: `python run_agent_simple.py`

**That's it! No Reddit API setup needed.**

### Files You'll Use:
- `run_agent_simple.py` - Main script to run
- `config_simple.py` - Your configuration (copy from template)
- `reddit_scanner_simple.py` - Behind-the-scenes scanner

### Example Configuration:
```python
# Minimal config needed for Simple Mode
EMAIL_FROM = "youremail@gmail.com"
EMAIL_PASSWORD = "your_gmail_app_password"
CREATOR_NICHE = "fitness health wellness"
SUBREDDITS_TO_SCAN = ["fitness", "health", "nutrition"]
```

## 🚀 Full Mode (Recommended for Regular Use)

### When to Use Full Mode:
- ✅ You plan to use this regularly or in production
- ✅ You want maximum speed and reliability
- ✅ You need to scan many subreddits frequently
- ✅ You're comfortable with API setup (takes 10 minutes)
- ✅ You want the best performance

### Setup (15 minutes):
1. Create a Reddit app at https://reddit.com/prefs/apps
2. Get your Reddit API credentials
3. Copy `config_template.py` to `config.py`
4. Add Reddit credentials + Gmail credentials
5. Run: `python run_agent.py`

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed Reddit API setup instructions.

### Files You'll Use:
- `run_agent.py` - Main script to run
- `config.py` - Your configuration (copy from template)
- Built-in PRAW library handles Reddit API

### Example Configuration:
```python
# Full Mode requires Reddit credentials
REDDIT_CLIENT_ID = "your_client_id"
REDDIT_CLIENT_SECRET = "your_secret"
REDDIT_USERNAME = "your_username"
REDDIT_PASSWORD = "your_password"

EMAIL_FROM = "youremail@gmail.com"
EMAIL_PASSWORD = "your_gmail_app_password"

CREATOR_NICHE = "fitness health wellness"
SUBREDDITS_TO_SCAN = ["fitness", "health", "nutrition"]
```

## 💡 Our Recommendation

### Start with Simple Mode if:
- You're completely new to this
- You want to try it today without much setup
- You're not sure if this tool is right for you

### Upgrade to Full Mode when:
- You like the results and want to use it regularly
- You need faster scanning and higher rate limits
- You're ready to invest 10 minutes in setup

## 🔄 Can I Switch Between Modes?

**Yes!** Both modes:
- Use the same `creedom_agent.py` core logic
- Store data in separate SQLite databases (so they don't interfere)
- Can run side by side

You can test with Simple Mode and switch to Full Mode later without losing anything.

## ❓ Common Questions

### Does Simple Mode have all the features?
**Yes!** Simple Mode has 100% of the features:
- TSS scoring algorithm (identical)
- Creator niche matching
- Content brief generation
- Email notifications
- Database logging

The only difference is HOW it gets data from Reddit.

### Why is Simple Mode slower?
Simple Mode makes HTTP requests to Reddit's public JSON endpoints, which have stricter rate limiting for unauthenticated users. Full Mode uses the official Reddit API with authentication, which is faster and more reliable.

### Can I use Simple Mode in production?
You can, but Full Mode is recommended for production use because it's faster, more reliable, and has higher rate limits.

### How do I get Gmail credentials for both modes?
Both modes use the same Gmail setup:
1. Go to Google Account settings
2. Enable 2-factor authentication
3. Create an "App Password" for email
4. Use that 16-character password in your config

See [SETUP_GUIDE.md](SETUP_GUIDE.md) Step 4 for detailed instructions.

## 🎯 Bottom Line

**Try Simple Mode first.** It's easier to set up and you'll understand how the agent works. Then upgrade to Full Mode when you're ready for production use.

Both modes are completely free and use the same core intelligence!
