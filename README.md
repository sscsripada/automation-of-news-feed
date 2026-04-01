# Daily company news feed

This repo generates a daily Markdown check-in covering news for a configurable watchlist of customers and competitors.

## What it does

- Reads the company watchlist from `config/watchlist.yaml`
- Pulls recent articles from Google News RSS for each company
- Summarizes the news with OpenAI when `OPENAI_API_KEY` is available
- Falls back to a simple headline-based summary when no API key is set
- Writes a dated check-in document to `checkins/YYYY-MM-DD.md`
- Includes a GitHub Actions workflow that can generate, commit, and DM the check-in in Slack every weekday morning

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
3. Create a Slack app with a bot token and install it to your workspace.
4. Add a repository secret named `SLACK_BOT_TOKEN` with the bot token.
5. Set the target Slack user ID in `.github/workflows/daily-news-checkin.yml`.
6. The workflow in `.github/workflows/daily-news-checkin.yml` is set up to run close to `8:05 AM` Chicago time on weekdays using separate UTC schedules for standard time and daylight time.
7. Each run writes a new file in `checkins/`, commits it back to the repo when there are changes, and sends the digest to Slack DM when `SLACK_BOT_TOKEN` is configured.

Because GitHub Actions scheduled workflows use UTC rather than a named local timezone, the run can be off by an hour for a few weekdays around the March and November daylight-saving transitions.

## Slack setup

Use a Slack app with a bot token.

1. In Slack, create a new app from scratch.
2. In `OAuth & Permissions`, add the bot scope `chat:write`.
3. Install or reinstall the app to your workspace.
4. Copy the bot token into the GitHub secret `SLACK_BOT_TOKEN`.
5. Find your Slack user ID and place it in the workflow as `SLACK_USER_ID`.

The workflow sends a formatted DM containing each watched company, top bullets, and quick source links.

## Tests

```bash
pytest
```
