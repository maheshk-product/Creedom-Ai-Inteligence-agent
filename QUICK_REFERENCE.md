# Beginner's Quick Reference Guide

This is a **one-page cheat sheet** for complete beginners. Keep this handy!

## 📋 What You Need (All FREE!)

1. **Reddit Account** - reddit.com (sign up free)
2. **Gmail Account** - gmail.com (sign up free)
3. **Python** - python.org/downloads (download free)
4. **This Code** - Already have it!

**Total Cost: $0.00** 🎉

---

## 🚀 Super Quick Setup (5 Steps)

### Step 1: Install Python
- Download from python.org
- **IMPORTANT**: Check "Add Python to PATH" during install
- Test: Open terminal/command prompt, type `python --version`

### Step 2: Run Installation Script

**Windows:** Double-click `install.bat`
**Mac/Linux:** Open terminal, type `./install.sh`

This installs everything automatically!

### Step 3: Get Reddit API Keys

1. Go to reddit.com/prefs/apps
2. Click "create another app..."
3. Name: "Creedom Agent"
4. Type: Select "script"
5. Redirect URI: `http://localhost:8080`
6. Click "create app"
7. **Write down**:
   - The string under the app name = **CLIENT_ID**
   - The string next to "secret" = **CLIENT_SECRET**

### Step 4: Get Gmail App Password

1. Go to myaccount.google.com/security
2. Turn on "2-Step Verification" (if not already on)
3. Go to myaccount.google.com/apppasswords
4. Select "Mail" and "Other"
5. Type "Creedom Agent"
6. Click "Generate"
7. **Copy the 16-character password**

### Step 5: Configure & Run

1. Open `config.py` in Notepad/TextEdit
2. Fill in your information:
   - `REDDIT_CLIENT_ID` = from Step 3
   - `REDDIT_CLIENT_SECRET` = from Step 3
   - `REDDIT_USERNAME` = your Reddit username
   - `REDDIT_PASSWORD` = your Reddit password
   - `EMAIL_FROM` = your Gmail address
   - `EMAIL_TO` = your Gmail address (same)
   - `EMAIL_PASSWORD` = 16-char password from Step 4
   - `CREATOR_NICHE` = your content topics (e.g., "fitness health")
   - `SUBREDDITS_TO_SCAN` = subreddits to watch
3. Save the file
4. Open terminal/command prompt
5. Type: `python run_agent.py`

**You're done!** 🎉 Check your email for trend alerts!

---

## 🎯 What Each File Does

| File | Purpose |
|------|---------|
| `run_agent.py` | Main program - runs the agent |
| `config.py` | Your settings (YOU create this) |
| `config_template.py` | Example config (copy this to make config.py) |
| `creedom_agent.py` | Core AI logic (don't modify) |
| `quickstart.py` | Test if everything works |
| `install.sh` / `install.bat` | Auto-installer scripts |
| `SETUP_GUIDE.md` | Detailed instructions (read this if stuck) |

---

## 💻 Common Commands

```bash
# Run the agent
python run_agent.py

# Test your setup (no credentials needed)
python quickstart.py

# Check if config is correct
python config.py

# View statistics
python run_agent.py --stats

# Install requirements
pip install -r requirements.txt
```

---

## 📧 What to Expect

After running `python run_agent.py`, you'll see:

1. ✅ "Connected to Reddit API"
2. 🔎 "Scanning subreddits..."
3. 📊 "Found X trends"
4. 🎯 "Found X matching trends"
5. ✅ "Email sent!"

Check your email! You should receive alerts like:

```
🔥 [CRITICAL] Trend Alert

TSS Score: 88

TREND: Revolutionary fitness technique...

Your hook: "This changes everything about..."

Content idea: Create a reel showing...

Window: Act today - 12-24 hours max
```

---

## 🔧 Troubleshooting

### "ModuleNotFoundError"
**Fix:** Run `pip install -r requirements.txt`

### "Authentication failed" (Reddit)
**Fix:** Check your Reddit credentials in config.py

### "SMTP authentication error" (Email)
**Fix:**
- Make sure you're using the 16-character App Password
- NOT your regular Gmail password
- Remove any spaces from the password in config.py

### "No trends found"
**Not a problem!** This just means:
- No high-scoring trends right now
- Try again in a few hours
- Or lower `MIN_TSS_SCORE` in config.py

### "pip: command not found"
**Fix:**
- Windows: Use `python -m pip install -r requirements.txt`
- Mac/Linux: Use `pip3 install -r requirements.txt`

---

## 🔄 Running Automatically

### Option 1: Your Computer (While Running)

**Windows - Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily, repeat every 6 hours
4. Action: Start program → `python`
5. Arguments: `run_agent.py`

**Mac/Linux - Cron:**
```bash
crontab -e
# Add this line:
0 */6 * * * cd /path/to/Creedom-Ai-Inteligence-agent && python3 run_agent.py
```

### Option 2: Cloud (FREE - Even When Computer Is Off!)

See **GITHUB_ACTIONS_GUIDE.md** for step-by-step instructions.

Uses GitHub Actions - 100% free, runs 24/7 in the cloud!

---

## 🎓 Understanding TSS Scores

| Score | Tier | What It Means | What To Do |
|-------|------|---------------|------------|
| 85-100 | 🔴 CRITICAL | Going viral NOW | Post within 12-24 hours |
| 70-84 | 🟡 HIGH | Strong momentum | Post within week |
| 50-69 | 🟢 MEDIUM | Worth watching | Post within 2 weeks |
| 0-49 | ⚪ NOISE | Ignore | Don't waste time |

The agent only sends alerts for trends scoring 50+.

---

## 💡 Pro Tips

1. **Start broad** - Use general niches like "fitness health" first
2. **Check daily** - Run the agent once per day initially
3. **Adjust as needed** - Tweak `MIN_TSS_SCORE` based on results
4. **Monitor multiple niches** - Add 3-5 related subreddits
5. **Act fast on CRITICAL** - These are time-sensitive!

---

## 📚 Learning Path

### Day 1: Setup
- [ ] Install Python
- [ ] Run installation script
- [ ] Get Reddit API keys
- [ ] Get Gmail app password
- [ ] Configure config.py
- [ ] Run `python quickstart.py` (test)
- [ ] Run `python run_agent.py` (real)

### Day 2: Customize
- [ ] Adjust your niche keywords
- [ ] Add more subreddits
- [ ] Test different MIN_TSS_SCORE values
- [ ] Review email alerts

### Day 3: Automate
- [ ] Set up automated scheduling (cron or Task Scheduler)
- [ ] OR set up GitHub Actions (cloud)

### Week 1+: Optimize
- [ ] Track which trends worked best
- [ ] Refine your niche keywords
- [ ] Adjust notification preferences
- [ ] Share your success!

---

## 🆘 Getting Help

**Stuck?** Try these in order:

1. **Read SETUP_GUIDE.md** - Detailed beginner instructions
2. **Run `python quickstart.py`** - Test if core agent works
3. **Check troubleshooting section** - Above or in SETUP_GUIDE.md
4. **Open a GitHub Issue** - github.com/maheshk-product/Creedom-Ai-Inteligence-agent/issues

---

## ✅ Quick Checklist

Before asking for help, verify:

- [ ] Python is installed (`python --version` works)
- [ ] Requirements installed (`pip install -r requirements.txt` ran successfully)
- [ ] config.py exists (copied from config_template.py)
- [ ] Reddit API credentials filled in config.py
- [ ] Email credentials filled in config.py
- [ ] No typos in config.py (especially no spaces in passwords)
- [ ] Tried running `python quickstart.py` first

---

## 🎯 Success Checklist

You'll know it's working when:

- [ ] `python quickstart.py` shows "ALL TESTS PASSED"
- [ ] `python run_agent.py` connects to Reddit
- [ ] You see "Found X trends" messages
- [ ] You receive an email alert
- [ ] Email contains trend details and content ideas

---

## 📊 Example Config (Copy & Customize)

```python
# Reddit
REDDIT_CLIENT_ID = "abc123xyz"
REDDIT_CLIENT_SECRET = "AbCdEf789"
REDDIT_USER_AGENT = "Creedom Agent by /u/yourname"
REDDIT_USERNAME = "yourname"
REDDIT_PASSWORD = "yourpassword"

# Email
EMAIL_ENABLED = True
EMAIL_FROM = "you@gmail.com"
EMAIL_TO = "you@gmail.com"
EMAIL_PASSWORD = "abcd efgh ijkl mnop"

# Your Niche
CREATOR_NICHE = "fitness health wellness"
SUBREDDITS_TO_SCAN = ["fitness", "health", "nutrition"]
```

Replace the example values with YOUR actual credentials!

---

## 🚀 You're Ready!

Remember:
- ✅ Everything is FREE
- ✅ No coding experience needed
- ✅ Setup takes ~30 minutes
- ✅ Saves you hours of manual research
- ✅ Never miss trending topics again

**Questions?** See SETUP_GUIDE.md or open a GitHub issue.

**Working?** Give the repo a ⭐ star on GitHub!

---

**Happy trend hunting! 🎯**
