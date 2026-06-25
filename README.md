# Artrovex Wellness Blog — Auto Generator

Publishes a new wellness article in 5 languages every day automatically.

## Setup (one time, 10 minutes)

### 1. Add API Key to GitHub Secrets
- Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
- Click **New repository secret**
- Name: `ANTHROPIC_API_KEY`
- Value: your Anthropic API key
- Click **Add secret**

### 2. Connect Netlify to this GitHub repo
- Go to netlify.com → **Add new site** → **Import from Git**
- Choose this GitHub repository
- Publish directory: `docs`
- Click **Deploy**

### 3. That's it!
Every day at 08:00 UTC:
- GitHub Actions runs `generate.py`
- 5 new article pages are created (EN, DE, IT, ES, FR)
- Changes are committed to GitHub
- Netlify automatically deploys the update
- Google indexes the new pages

## Manual trigger
Go to GitHub → **Actions** → **Daily Article Generator** → **Run workflow**

## Cost
~$0.03–0.05 per day (5 articles × 5 languages)
