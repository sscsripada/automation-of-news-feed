# Daily company news feed

This repo generates a daily Markdown check-in covering news for a configurable watchlist of customers and competitors.

## What it does

- Reads the company watchlist from `config/watchlist.yaml`
- Pulls recent articles from Google News RSS for each company
- Summarizes the news with OpenAI when `OPENAI_API_KEY` is available
- Falls back to a simple headline-based summary when no API key is set
- Writes a dated check-in document to `checkins/YYYY-MM-DD.md`
- Includes a GitHub Actions workflow that can generate and commit the check-in daily

## Current starter watchlist

The initial config assumes:

- `customer`: 8x8 Inc, Oracle, JLL
- `competitor`: Microsoft, AWS

You can change both the category and search terms in `config/watchlist.yaml`.

## Local usage

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
generate-news-checkin
```

Optional:

```bash
OPENAI_API_KEY=... generate-news-checkin --output checkins/manual-run.md
```

## Edit the watchlist

Update `config/watchlist.yaml` and change:

- `category`: usually `customer` or `competitor`
- `name`: the display name in the report
- `query`: the search query sent to Google News RSS
- `notes`: optional context added to the LLM prompt

## GitHub setup

1. Create a GitHub repo and push this project.
2. Add a repository secret named `OPENAI_API_KEY` if you want AI summaries.
3. The workflow in `.github/workflows/daily-news-checkin.yml` runs on weekdays and on manual dispatch.
4. Each run writes a new file in `checkins/` and commits it back to the repo when there are changes.

## Tests

```bash
pytest
```

