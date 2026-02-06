# Brief

An AI-powered daily content digest. Brief ingests from curated sources, enriches content with Claude, clusters related stories, and generates a clean 3-lane HTML digest covering **Builders**, **Security**, and **Business**.

## How It Works

1. **Ingest** — Pulls new content from RSS feeds and APIs
2. **Enrich** — Claude summarizes each item, tags topics, scores lane relevance
3. **Rank & Cluster** — Groups related stories, scores by recency/trust/relevance
4. **Generate** — Claude synthesizes cluster summaries and picks a Top 3
5. **Deliver** — Saves a self-contained HTML file to `~/Briefs/` and opens it in your browser

## Quick Start

```bash
# Clone the repo
git clone https://github.com/caitlinconsults/brief.git
cd brief

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Add your Anthropic API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run the pipeline
python -m src.main
```

Your digest will appear in `~/Briefs/` and open in your default browser.

## Configuration

### Sources

Edit `config/sources.yaml` to enable/disable sources or add your own. Each source needs:

- `name` — Display name
- `slug` — Unique identifier
- `enabled` — Set to `true` to include in the daily run
- `fetch_method` — `rss`, `api`, or `web_scrape`
- `fetch_url` — The feed or API URL
- `lanes` — Which digest lanes this source feeds (`builders`, `security`, `business`)
- `trust_weight` — How much to trust this source (0.0–1.0)

### Ranking

Edit `config/ranking_weights.yaml` to adjust how content is scored:

- `recency` — Newer content scores higher
- `source_trust` — Trusted sources score higher
- `lane_affinity` — Content matching its primary lane scores higher
- `popularity` — Engagement signals (when available)
- `novelty` — Content on underrepresented topics gets a boost

## Running It Daily

The core pipeline (`python -m src.main`) works on **any operating system** — Mac, Linux, or Windows. You just need Python and an API key.

To run it automatically every morning, you need to set up scheduling, and that part depends on your OS:

### macOS

The `scripts/` folder has ready-to-go automation for Mac. Run this once:

```bash
bash scripts/setup_schedule.sh
```

This wakes your Mac at 4:55 AM, runs the pipeline at 5 AM, opens the digest when you next log in, and puts the Mac back to sleep. You don't need to think about it after setup.

### Linux

Set up a cron job to run the pipeline on your preferred schedule:

```bash
crontab -e
# Add: 0 5 * * * cd /path/to/brief && venv/bin/python -m src.main
```

### Windows

Use Task Scheduler to run `python -m src.main` on a daily schedule.

> **Note:** Everything in the `scripts/` folder is macOS-only. If you're not on a Mac, ignore that folder entirely and just schedule `python -m src.main` however your OS handles it.

## Project Structure

```
brief/
├── config/
│   ├── sources.yaml          # Source registry
│   └── ranking_weights.yaml  # Ranking weights
├── src/                      # The pipeline (works on any OS)
│   ├── main.py               # Pipeline orchestrator
│   ├── ingestion.py          # RSS/API fetching
│   ├── enrichment.py         # Claude-powered enrichment
│   ├── ranking.py            # Scoring and clustering
│   ├── digest.py             # Digest generation
│   ├── delivery.py           # File output and browser open
│   ├── security.py           # Input sanitization
│   └── database.py           # SQLite storage
├── templates/
│   └── digest.html           # Jinja2 digest template
├── scripts/                  # macOS-only scheduling helpers
│   ├── run_brief.sh          # Pipeline runner
│   ├── check_digest.sh       # Auto-open on login
│   └── setup_schedule.sh     # LaunchAgent setup
└── milestones/               # Project specs
```

## Requirements

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/)

## License

MIT
