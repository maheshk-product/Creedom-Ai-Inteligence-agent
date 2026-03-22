# GitHub Actions Automation Guide

Run your Creedom Agent in the cloud for FREE using GitHub Actions!

## Why GitHub Actions?

- ✅ **100% Free** - 2,000 minutes/month for free accounts
- ✅ **Runs 24/7** - Even when your computer is off
- ✅ **No server needed** - Everything runs in GitHub's cloud
- ✅ **Automatic scheduling** - Set it and forget it

## Setup Steps

### Step 1: Push Your Code to GitHub

1. Create a GitHub account at [github.com](https://github.com) (free)
2. Create a new repository (name it anything, e.g., "my-creedom-agent")
3. Make it **private** (to protect your credentials)
4. Push your code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/my-creedom-agent.git
   git push -u origin main
   ```

### Step 2: Add GitHub Secrets

GitHub Secrets keep your passwords safe. Never put passwords in your code!

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these secrets one by one:

| Secret Name | Value | Where to Get It |
|------------|-------|----------------|
| `REDDIT_CLIENT_ID` | Your Reddit client ID | reddit.com/prefs/apps |
| `REDDIT_CLIENT_SECRET` | Your Reddit client secret | reddit.com/prefs/apps |
| `REDDIT_USERNAME` | Your Reddit username | Your Reddit account |
| `REDDIT_PASSWORD` | Your Reddit password | Your Reddit account |
| `EMAIL_FROM` | Your Gmail address | yourname@gmail.com |
| `EMAIL_TO` | Where to send alerts | Same or different email |
| `EMAIL_PASSWORD` | Gmail App Password | See SETUP_GUIDE.md Step 4 |

**Example:**
- Click "New repository secret"
- Name: `REDDIT_CLIENT_ID`
- Secret: `abc123xyz` (your actual client ID)
- Click "Add secret"

Repeat for all 7 secrets.

### Step 3: Create the Workflow File

1. In your repository, create this folder structure:
   ```
   .github/
   └── workflows/
       └── run-creedom-agent.yml
   ```

2. Copy the file `github_workflow_template.yml` to `.github/workflows/run-creedom-agent.yml`

3. Edit the file to customize your schedule and settings

### Step 4: Customize Your Settings

Open `.github/workflows/run-creedom-agent.yml` and customize:

```yaml
# How often to run (currently every 6 hours)
- cron: '0 */6 * * *'

# Your creator settings
env:
  CREATOR_NAME: "Your Name"
  CREATOR_NICHE: "fitness health wellness"
  CREATOR_PLATFORM: "instagram"
  SUBREDDITS: "fitness,health,nutrition"
```

#### Cron Schedule Examples:

- Every 6 hours: `0 */6 * * *`
- Every 3 hours: `0 */3 * * *`
- Every day at 9 AM: `0 9 * * *`
- Twice daily (9 AM and 5 PM): `0 9,17 * * *`
- Every hour: `0 * * * *`

**Tool to help:** Use [crontab.guru](https://crontab.guru) to create schedules

### Step 5: Push and Activate

1. Commit and push your workflow file:
   ```bash
   git add .github/workflows/run-creedom-agent.yml
   git commit -m "Add GitHub Actions workflow"
   git push
   ```

2. Go to your repository on GitHub
3. Click the **Actions** tab
4. You should see your workflow listed
5. Click **Enable workflow** if prompted

### Step 6: Test It

Don't wait for the schedule - test it now!

1. Go to **Actions** tab
2. Click your workflow name
3. Click **Run workflow** button
4. Select branch "main"
5. Click **Run workflow**

Watch it run in real-time! You should see:
- ✅ Setup Python
- ✅ Install dependencies
- ✅ Scan Reddit for trends
- ✅ Send email notifications

Check your email for trend alerts!

## Understanding the Workflow

The GitHub Action does this automatically:

1. **Sets up Python** - Installs Python 3.9
2. **Installs libraries** - Runs `pip install -r requirements.txt`
3. **Creates config** - Builds config.py from your secrets
4. **Runs the agent** - Executes `python run_agent.py`
5. **Sends results** - Emails you the trend alerts
6. **Saves data** - Stores trends in the workflow (optional)

## Viewing Results

### Check Workflow Logs:

1. Go to **Actions** tab
2. Click on a workflow run
3. Click **Run Creedom Agent** job
4. Expand each step to see details

You'll see:
- How many trends were found
- TSS scores
- Which trends matched your niche
- Email sending status

### Check Your Email:

Within minutes of the workflow running, you should receive emails with trend alerts!

## Advanced: Upload Artifacts

Want to save the database between runs?

Add this to your workflow (already in template):

```yaml
- name: Upload database
  uses: actions/upload-artifact@v3
  with:
    name: creedom-database
    path: creedom_data.db
```

This saves your SQLite database so trends aren't duplicated.

## Cost Breakdown

GitHub Actions free tier:
- **2,000 minutes/month** for private repos
- **Unlimited** for public repos

Our workflow uses about **1-2 minutes per run**.

Running every 6 hours (4 times per day):
- Minutes per day: 4 × 2 = **8 minutes**
- Minutes per month: 8 × 30 = **240 minutes**
- **Well within the free 2,000 minutes!** ✅

You could run it every hour and still be free:
- 24 runs/day × 2 min = **48 min/day**
- 48 × 30 = **1,440 min/month**
- **Still free!** ✅

## Troubleshooting

### Workflow fails with "Invalid credentials"

**Problem:** GitHub Secrets not set correctly

**Solution:**
1. Go to Settings → Secrets → Actions
2. Verify all 7 secrets are created
3. Check for typos in secret names (they're case-sensitive!)
4. Re-enter secrets if needed

### Workflow runs but no email received

**Problem:** Email configuration issue

**Solution:**
1. Check your spam folder
2. Verify `EMAIL_FROM` and `EMAIL_PASSWORD` secrets
3. Make sure you're using Gmail App Password (not regular password)
4. Check workflow logs for email error messages

### "No qualifying trends found"

**Problem:** Not a problem! Just means no high-scoring trends right now

**Solution:**
- This is normal - trends come and go
- Try again in a few hours
- Lower `MIN_TSS_SCORE` in the workflow (currently 50)
- Add more subreddits to `SUBREDDITS` list

### Want to pause the automation?

1. Go to **Actions** tab
2. Click your workflow name
3. Click the **...** menu
4. Click **Disable workflow**

To resume, click **Enable workflow**

## Monitoring Your Usage

Track your GitHub Actions minutes:

1. Go to your profile → **Settings**
2. Click **Billing and plans**
3. Click **Plans and usage**
4. See **Actions minutes used**

You'll see you're using very little of your free quota!

## Next Steps

Once it's working:
- ✅ Tweak the schedule to your needs
- ✅ Adjust TSS threshold
- ✅ Add more subreddits
- ✅ Customize email templates in `run_agent.py`

## Security Best Practices

- ✅ **Never** commit `config.py` to GitHub
- ✅ Always use GitHub Secrets for passwords
- ✅ Make your repository private
- ✅ Regularly rotate your Reddit and email passwords
- ✅ Use Gmail App Passwords (not your main password)

## Alternative: Deploy to Other Free Platforms

If GitHub Actions doesn't work for you, try these (all free):

1. **Replit** - Has automatic scheduling
2. **PythonAnywhere** - Free tier with scheduled tasks
3. **Render** - Free cron jobs
4. **Railway** - Free tier with scheduling

See SETUP_GUIDE.md for more options.

---

**Questions?** Open an issue on GitHub or check the troubleshooting section.

**Enjoying Creedom?** Give the repository a ⭐ star on GitHub!
