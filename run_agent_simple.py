"""
Creedom AI Intelligence Agent - Simple Runner (No Reddit API Credentials Required!)

This version uses Reddit's public JSON feeds - NO authentication needed!
Perfect for:
- Complete beginners
- Testing the agent before setting up API credentials
- Users who don't want to create Reddit apps

Limitations:
- Can only access public subreddits
- Subject to stricter rate limiting
- Slightly slower than authenticated version

All other features work the same: TSS scoring, email notifications, SQLite database!
"""

import sys
import os
from datetime import datetime

# Import the simple scanner that doesn't need authentication
from reddit_scanner_simple import SimpleRedditScanner
from creedom_agent import CreedomAgent, CreatorProfile

# Try to import configuration (only needs email settings)
try:
    import config_simple as config
except ImportError:
    print("❌ ERROR: config_simple.py not found!")
    print("\n📋 To fix this:")
    print("1. Copy config_simple_template.py to config_simple.py")
    print("2. Edit config_simple.py with your email and preferences")
    print("3. No Reddit API credentials needed!")
    print()
    sys.exit(1)

# Validate configuration
print("🔍 Validating configuration...")
if not config.validate_config():
    print("\n⚠️  Please fix configuration errors and try again.")
    sys.exit(1)

# Import required libraries
try:
    import sqlite3
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
except ImportError as e:
    print(f"❌ ERROR: Missing required library: {e}")
    print("\n📋 To fix this, run:")
    print("   pip install -r requirements.txt")
    print()
    sys.exit(1)


class SimpleRunner:
    """Simple runner that uses public Reddit JSON (no auth)."""

    def __init__(self):
        """Initialize the simple runner."""
        self.agent = CreedomAgent()
        self.scanner = SimpleRedditScanner(
            user_agent=f"CreedomAgent/1.0 by /u/{config.USER_REDDIT_USERNAME}"
        )
        self.db_conn = None
        self.setup_database()

    def setup_database(self):
        """Set up SQLite database (FREE - no server needed)."""
        try:
            print("💾 Setting up database...")
            self.db_conn = sqlite3.connect(config.DATABASE_PATH)
            cursor = self.db_conn.cursor()

            # Create trends table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id TEXT UNIQUE,
                    title TEXT,
                    subreddit TEXT,
                    score INTEGER,
                    num_comments INTEGER,
                    created_utc REAL,
                    url TEXT,
                    tss_score REAL,
                    velocity REAL,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create notifications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    creator_id TEXT,
                    post_id TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    channel TEXT,
                    tss_score REAL
                )
            ''')

            self.db_conn.commit()
            print("✅ Database ready")
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            sys.exit(1)

    def scan_reddit_for_trends(self):
        """Scan configured subreddits for trending content (no auth)."""
        print(f"\n🔎 Scanning {len(config.SUBREDDITS_TO_SCAN)} subreddits (public JSON)...")
        all_trends = []

        for subreddit_name in config.SUBREDDITS_TO_SCAN:
            try:
                print(f"  📊 Scanning r/{subreddit_name}...")

                # Get subreddit info for subscriber count
                sub_info = self.scanner.get_subreddit_info(subreddit_name)
                subreddit_subscribers = sub_info['subscribers'] if sub_info else 100_000

                # Get posts
                trends = self.scanner.get_hot_posts(subreddit_name, limit=config.POSTS_PER_SUBREDDIT)

                for trend in trends:
                    # Calculate metrics
                    trend.velocity = self.agent.calculate_velocity(trend.created_utc, trend.score)
                    trend.comment_ratio = self.agent.calculate_comment_ratio(trend.num_comments, trend.score)
                    trend.emotional_score = self.agent.detect_emotional_language(trend.title + " " + trend.selftext)
                    trend.tss_score = self.agent.score_trend(trend, subreddit_subscribers)

                    # Only keep if above minimum threshold
                    if trend.tss_score >= config.MIN_TSS_SCORE:
                        all_trends.append(trend)
                        self.save_trend_to_db(trend)

                print(f"     Found {len([t for t in all_trends if t.subreddit == subreddit_name])} qualifying trends")

            except Exception as e:
                print(f"  ❌ Error scanning r/{subreddit_name}: {e}")
                continue

        return all_trends

    def save_trend_to_db(self, trend):
        """Save a trend to the database."""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO trends
                (post_id, title, subreddit, score, num_comments, created_utc, url, tss_score, velocity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trend.post_id, trend.title, trend.subreddit, trend.score,
                trend.num_comments, trend.created_utc, trend.url,
                trend.tss_score, trend.velocity
            ))
            self.db_conn.commit()
        except Exception as e:
            if config.DEBUG_MODE:
                print(f"  ⚠️  Could not save trend to DB: {e}")

    def match_trends_to_creator(self, trends):
        """Match trends to the configured creator profile."""
        print(f"\n🎯 Matching trends to your niche: '{config.CREATOR_NICHE}'...")

        creator = CreatorProfile(
            creator_id=config.CREATOR_ID,
            niche=config.CREATOR_NICHE,
            platform=config.CREATOR_PLATFORM,
            style=config.CREATOR_STYLE,
            follower_count=config.CREATOR_FOLLOWER_COUNT,
            audience_age=config.CREATOR_AUDIENCE_AGE,
            past_performance={'avg_engagement': 0.05}
        )

        matched_trends = []
        for trend in trends:
            is_match, confidence = self.agent.match_trend_to_creator(trend, creator)
            if is_match:
                matched_trends.append((trend, confidence))

        # Sort by TSS score
        matched_trends.sort(key=lambda x: x[0].tss_score, reverse=True)

        print(f"✅ Found {len(matched_trends)} matching trends")
        return matched_trends, creator

    def send_email_notification(self, trend, brief):
        """Send email notification using FREE Gmail SMTP."""
        if not config.EMAIL_ENABLED:
            print("  📧 Email notifications disabled in config")
            return False

        try:
            # Determine tier emoji
            if brief.tss_score >= 85:
                tier = "🔥 CRITICAL"
            elif brief.tss_score >= 70:
                tier = "📈 HIGH"
            else:
                tier = "👀 MEDIUM"

            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"{tier} Trend Alert - TSS: {brief.tss_score:.0f}"
            msg['From'] = config.EMAIL_FROM
            msg['To'] = config.EMAIL_TO

            # Email body (plain text)
            text = f"""
Creedom Trend Alert for {config.CREATOR_NAME}

{tier} - TSS Score: {brief.tss_score:.0f}

TREND: {brief.trend_theme}

WHY IT MATTERS:
{brief.why_it_matters}

YOUR HOOK:
"{brief.hook_line}"

CONTENT IDEA:
{brief.content_idea}

URGENCY: {brief.urgency_window}

FORMAT: {brief.recommended_format}

CROSS-NICHE OPPORTUNITY:
{brief.cross_niche_opportunity}

---
Reddit: {trend.url}
Velocity: {trend.velocity:.0f} score/hour
Comments: {trend.num_comments}

This alert brought to you by Creedom AI Intelligence Agent (Simple Mode - No Auth)
            """

            # Email body (HTML)
            html = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h2 style="color: #ff4500;">{tier} Trend Alert</h2>
    <p style="font-size: 18px;"><strong>TSS Score: {brief.tss_score:.0f}</strong></p>

    <h3 style="color: #333;">📊 Trend</h3>
    <p>{brief.trend_theme}</p>

    <h3 style="color: #333;">💡 Why It Matters</h3>
    <p>{brief.why_it_matters}</p>

    <h3 style="color: #333;">🎣 Your Hook</h3>
    <p style="font-style: italic; background: #f0f0f0; padding: 10px; border-left: 3px solid #ff4500;">
        "{brief.hook_line}"
    </p>

    <h3 style="color: #333;">🎬 Content Idea</h3>
    <p>{brief.content_idea}</p>

    <h3 style="color: #333;">⏰ Urgency</h3>
    <p><strong>{brief.urgency_window}</strong></p>

    <h3 style="color: #333;">📱 Recommended Format</h3>
    <p>{brief.recommended_format}</p>

    <h3 style="color: #333;">🔀 Cross-Niche Opportunity</h3>
    <p>{brief.cross_niche_opportunity}</p>

    <hr style="margin: 20px 0;">

    <p style="font-size: 12px; color: #666;">
        <a href="{trend.url}">View on Reddit</a> |
        Velocity: {trend.velocity:.0f} score/hour |
        Comments: {trend.num_comments}
    </p>

    <p style="font-size: 11px; color: #999; margin-top: 20px;">
        Powered by Creedom AI Intelligence Agent (Simple Mode)
    </p>
</body>
</html>
            """

            # Attach both versions
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(part1)
            msg.attach(part2)

            # Send via Gmail SMTP (FREE)
            with smtplib.SMTP(config.EMAIL_SMTP_HOST, config.EMAIL_SMTP_PORT) as server:
                server.starttls()
                server.login(config.EMAIL_FROM, config.EMAIL_PASSWORD)
                server.send_message(msg)

            print(f"  ✅ Email sent to {config.EMAIL_TO}")

            # Log to database
            cursor = self.db_conn.cursor()
            cursor.execute('''
                INSERT INTO notifications (creator_id, post_id, channel, tss_score)
                VALUES (?, ?, ?, ?)
            ''', (config.CREATOR_ID, trend.post_id, 'email', brief.tss_score))
            self.db_conn.commit()

            return True

        except Exception as e:
            print(f"  ❌ Failed to send email: {e}")
            return False

    def process_trends(self, matched_trends, creator):
        """Process matched trends and send notifications."""
        print(f"\n📬 Processing top {min(len(matched_trends), config.MAX_TRENDS_PER_RUN)} trends...")

        sent_count = 0
        for i, (trend, confidence) in enumerate(matched_trends[:config.MAX_TRENDS_PER_RUN]):
            print(f"\n  Trend {i+1}: TSS {trend.tss_score:.0f} | {trend.title[:60]}...")

            # Check notification settings
            should_notify = False
            if trend.tss_score >= 85 and config.NOTIFY_ON_CRITICAL:
                should_notify = True
            elif trend.tss_score >= 70 and config.NOTIFY_ON_HIGH:
                should_notify = True
            elif trend.tss_score >= 50 and config.NOTIFY_ON_MEDIUM:
                should_notify = True

            if should_notify:
                # Generate brief
                brief = self.agent.generate_brief(trend, creator)

                # Send notification
                if self.send_email_notification(trend, brief):
                    sent_count += 1
            else:
                print(f"  ⏭️  Skipped (notification disabled for this TSS tier)")

        print(f"\n✅ Sent {sent_count} notification(s)")
        return sent_count

    def run(self):
        """Main execution flow."""
        print("\n" + "="*60)
        print("🤖 CREEDOM AI INTELLIGENCE AGENT (SIMPLE MODE)")
        print("="*60)
        print("✨ Running without Reddit API authentication")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        try:
            # Step 1: Scan Reddit using public JSON
            trends = self.scan_reddit_for_trends()

            if not trends:
                print("\n📭 No qualifying trends found this time.")
                print("💡 Try again later or adjust MIN_TSS_SCORE in config_simple.py")
                return

            print(f"\n✅ Found {len(trends)} total qualifying trends (TSS >= {config.MIN_TSS_SCORE})")

            # Show top 5
            print("\n🏆 Top 5 Trends by TSS Score:")
            sorted_trends = sorted(trends, key=lambda t: t.tss_score, reverse=True)
            for i, trend in enumerate(sorted_trends[:5], 1):
                print(f"  {i}. TSS {trend.tss_score:.0f} | r/{trend.subreddit} | {trend.title[:50]}...")

            # Step 2: Match to creator
            matched_trends, creator = self.match_trends_to_creator(trends)

            if not matched_trends:
                print("\n📭 No trends matched your niche this time.")
                print(f"💡 Current niche: '{config.CREATOR_NICHE}'")
                print("💡 Try broadening your CREATOR_NICHE in config_simple.py")
                return

            # Step 3: Process and notify
            self.process_trends(matched_trends, creator)

            print("\n" + "="*60)
            print("✅ Run completed successfully!")
            print("="*60)

        except KeyboardInterrupt:
            print("\n\n⚠️  Stopped by user")
        except Exception as e:
            print(f"\n❌ Error during execution: {e}")
            if config.DEBUG_MODE:
                import traceback
                traceback.print_exc()
        finally:
            # Cleanup
            if self.db_conn:
                self.db_conn.close()


def main():
    """Entry point."""
    runner = SimpleRunner()
    runner.run()


if __name__ == "__main__":
    main()
