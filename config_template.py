"""
Configuration Template for Creedom AI Intelligence Agent

INSTRUCTIONS:
1. Copy this file and rename it to 'config.py'
2. Fill in YOUR information below
3. Never share config.py with anyone (it contains your passwords!)

All services used here are 100% FREE!
"""

# ==============================================================================
# REDDIT API CONFIGURATION (FREE - 60 requests per minute)
# ==============================================================================
# Get your credentials at: https://reddit.com/prefs/apps
# See SETUP_GUIDE.md Step 3 for detailed instructions

REDDIT_CLIENT_ID = "your_client_id_here"  # From Reddit app page
REDDIT_CLIENT_SECRET = "your_client_secret_here"  # From Reddit app page
REDDIT_USER_AGENT = "Creedom Agent by /u/YOUR_USERNAME"  # Replace YOUR_USERNAME
REDDIT_USERNAME = "your_reddit_username"  # Your Reddit account username
REDDIT_PASSWORD = "your_reddit_password"  # Your Reddit account password

# ==============================================================================
# EMAIL CONFIGURATION (FREE - Gmail SMTP, 500 emails/day)
# ==============================================================================
# See SETUP_GUIDE.md Step 4 for how to get Gmail App Password

EMAIL_ENABLED = True  # Set to False to disable email notifications
EMAIL_FROM = "yourname@gmail.com"  # Your Gmail address
EMAIL_TO = "yourname@gmail.com"  # Where to send alerts (can be same email)
EMAIL_PASSWORD = "your_app_password_here"  # 16-character Gmail App Password
EMAIL_SMTP_HOST = "smtp.gmail.com"  # Gmail SMTP server (free)
EMAIL_SMTP_PORT = 587  # Gmail SMTP port

# ==============================================================================
# DATABASE CONFIGURATION (FREE - SQLite file-based database)
# ==============================================================================
# SQLite is built into Python - no setup needed!

DATABASE_TYPE = "sqlite"  # Use SQLite (free, no server needed)
DATABASE_PATH = "creedom_data.db"  # File where data is stored

# ==============================================================================
# CREATOR PROFILE (Tell the agent about YOUR content)
# ==============================================================================

CREATOR_ID = "creator_001"  # A unique ID for you (can be anything)
CREATOR_NAME = "Your Name"  # Your name or channel name
CREATOR_NICHE = "fitness health wellness"  # Your content topics (space-separated)
CREATOR_PLATFORM = "instagram"  # Options: instagram, youtube, linkedin
CREATOR_STYLE = "educational reels"  # Your content style
CREATOR_FOLLOWER_COUNT = 10000  # Approximate follower count
CREATOR_AUDIENCE_AGE = "25-35"  # Your target audience age range

# ==============================================================================
# REDDIT SCANNING SETTINGS
# ==============================================================================

# Which subreddits to monitor (comma-separated)
# Choose subreddits related to your niche
SUBREDDITS_TO_SCAN = [
    "fitness",
    "health",
    "wellness",
    "nutrition",
    "exercise"
]

# How many posts to check per subreddit
POSTS_PER_SUBREDDIT = 50

# Minimum TSS score to consider (0-100)
# 50 = Medium tier, 70 = High tier, 85 = Critical tier
MIN_TSS_SCORE = 50

# ==============================================================================
# NOTIFICATION SETTINGS
# ==============================================================================

# Send notifications for these TSS tiers
NOTIFY_ON_CRITICAL = True  # TSS >= 85
NOTIFY_ON_HIGH = True  # TSS >= 70
NOTIFY_ON_MEDIUM = False  # TSS >= 50 (usually too many)

# Cooldown between nudges (days)
NUDGE_COOLDOWN_DAYS = 3

# ==============================================================================
# ADVANCED SETTINGS (Optional)
# ==============================================================================

# How often to scan Reddit (for automation)
SCAN_INTERVAL_HOURS = 6  # Run every 6 hours

# Debug mode (shows more detailed logs)
DEBUG_MODE = False

# Maximum trends to process per run
MAX_TRENDS_PER_RUN = 10

# ==============================================================================
# EXAMPLE CONFIGURATIONS FOR DIFFERENT NICHES
# ==============================================================================

# Fitness Creator:
# CREATOR_NICHE = "fitness workout exercise health nutrition"
# SUBREDDITS_TO_SCAN = ["fitness", "bodybuilding", "running", "nutrition"]

# Finance Creator:
# CREATOR_NICHE = "finance money investing personal finance"
# SUBREDDITS_TO_SCAN = ["personalfinance", "investing", "financialindependence"]

# Tech Creator:
# CREATOR_NICHE = "technology AI programming software"
# SUBREDDITS_TO_SCAN = ["technology", "programming", "artificial", "gadgets"]

# Education Creator:
# CREATOR_NICHE = "education learning study techniques"
# SUBREDDITS_TO_SCAN = ["education", "teachers", "learnprogramming", "study"]

# ==============================================================================
# VALIDATION
# ==============================================================================

def validate_config():
    """Check if configuration is complete."""
    errors = []

    # Check Reddit config
    if "your_client_id" in REDDIT_CLIENT_ID:
        errors.append("❌ REDDIT_CLIENT_ID not configured")
    if "your_client_secret" in REDDIT_CLIENT_SECRET:
        errors.append("❌ REDDIT_CLIENT_SECRET not configured")
    if "YOUR_USERNAME" in REDDIT_USER_AGENT:
        errors.append("❌ REDDIT_USER_AGENT not configured")

    # Check Email config (if enabled)
    if EMAIL_ENABLED:
        if "yourname@gmail.com" in EMAIL_FROM:
            errors.append("❌ EMAIL_FROM not configured")
        if "your_app_password" in EMAIL_PASSWORD:
            errors.append("❌ EMAIL_PASSWORD not configured")

    # Check Creator profile
    if CREATOR_NAME == "Your Name":
        errors.append("⚠️  CREATOR_NAME not customized (optional)")
    if CREATOR_NICHE == "fitness health wellness":
        errors.append("⚠️  CREATOR_NICHE not customized (using default)")

    if errors:
        print("\n🔧 Configuration Issues Found:\n")
        for error in errors:
            print(f"  {error}")
        print("\n📖 See SETUP_GUIDE.md for help configuring these settings.\n")
        return False
    else:
        print("✅ Configuration validated successfully!")
        return True


if __name__ == "__main__":
    # Test configuration when this file is run directly
    print("Testing Creedom Agent Configuration...")
    validate_config()
