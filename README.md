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
- New pages are added to the sitemap and language archives for search engines to discover; indexing is decided by Google and is not guaranteed.

## Manual trigger
Go to GitHub → **Actions** → **Daily Article Generator** → **Run workflow**

## Rebuild navigation without generating articles

Run `python -c "import generate, json; m=json.load(open('docs/articles_meta.json')); generate.update_index(m); generate.generate_sitemap(m)"` from the repository root. This does not call the AI API or create new article content.

The home page links to the most recent articles using native HTML anchors. The five `/articles-<language>.html` archives link to every existing article in that language. Duplicate metadata entries and missing files are excluded from archives and the regular sitemap. Archive links lead to the corresponding language page on ARTROVEX.SHOP.

## Cost
~$0.03–0.05 per day (5 articles × 5 languages)
