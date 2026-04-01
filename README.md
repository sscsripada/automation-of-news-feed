# Daily company news feed

This repo generates a daily Markdown check-in covering news for a configurable watchlist of customers and competitors.

## What it does

- Reads the company watchlist from `config/watchlist.yaml`
- Pulls recent articles from Google News RSS for each company
- Summarizes the news with OpenAI when `OPENAI_API_KEY` is available
- Falls back to a simple headline-based summary when no API key is set
- Writes a dated check-in document to `checkins/YYYY-MM-DD.md`
- Includes a GitHub Actions workflow that can generate, commit, and post the check-in to Slack every weekday morning

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

To preview the Slack payload locally:

```bash
generate-news-checkin --slack-output tmp/slack_payload.json
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
3. Create a Slack app with an incoming webhook and add it to your target channel.
4. Add a repository secret named `SLACK_WEBHOOK_URL` with the incoming webhook URL.
5. The workflow in `.github/workflows/daily-news-checkin.yml` is set up to run close to `8:05 AM` Chicago time on weekdays using separate UTC schedules for standard time and daylight time.
6. Each run writes a new file in `checkins/`, commits it back to the repo when there are changes, and posts the digest to Slack when `SLACK_WEBHOOK_URL` is configured.

Because GitHub Actions scheduled workflows use UTC rather than a named local timezone, the run can be off by an hour for a few weekdays around the March and November daylight-saving transitions.

## Slack setup

Use a Slack app with Incoming Webhooks.

1. In Slack, create a new app from scratch.
2. Enable `Incoming Webhooks`.
3. Add a webhook for the channel where you want the daily update posted.
4. Copy the webhook URL into the GitHub secret `SLACK_WEBHOOK_URL`.

The workflow posts a formatted message containing each watched company, top bullets, and quick source links.

## Tests

```bash
pytest
```
