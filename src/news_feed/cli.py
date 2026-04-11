from __future__ import annotations

import argparse
import os
from datetime import date
from pathlib import Path

from news_feed.pipeline import build_recipient_digests, collect_digests, generate_checkin, render_markdown
from news_feed.slack import build_slack_payload, post_slack_dm, post_slack_dms, write_slack_payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a daily customer and competitor news check-in.")
    parser.add_argument("--config", default="config/watchlist.yaml", help="Path to the watchlist config file.")
    parser.add_argument(
        "--output",
        default=f"checkins/{date.today().isoformat()}.md",
        help="Path to the generated markdown check-in.",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=int(os.getenv("NEWS_LOOKBACK_DAYS", "2")),
        help="Only include articles within this many days.",
    )
    parser.add_argument(
        "--max-articles",
        type=int,
        default=int(os.getenv("NEWS_MAX_ARTICLES", "5")),
        help="Maximum articles per company.",
    )
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL"), help="Optional OpenAI model override.")
    parser.add_argument("--slack-output", help="Optional path to write a Slack webhook payload JSON file.")
    parser.add_argument("--recipients-config", help="Optional path to CSV/XLS/XLSX/YAML recipient mappings.")
    parser.add_argument(
        "--post-to-slack",
        action="store_true",
        help="Post the digest to Slack DM using SLACK_BOT_TOKEN and either SLACK_USER_ID or --recipients-config.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    digests, report_date = collect_digests(
        config_path=Path(args.config),
        lookback_days=args.lookback_days,
        max_articles=args.max_articles,
        model=args.model,
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_markdown(digests, report_date=report_date, lookback_days=args.lookback_days))

    if args.slack_output:
        slack_payload = build_slack_payload(digests, report_date=report_date, lookback_days=args.lookback_days)
        slack_output = Path(args.slack_output)
        slack_output.parent.mkdir(parents=True, exist_ok=True)
        write_slack_payload(str(slack_output), slack_payload)

    if args.post_to_slack:
        bot_token = os.getenv("SLACK_BOT_TOKEN")
        user_id = os.getenv("SLACK_USER_ID")
        if not bot_token:
            raise SystemExit("SLACK_BOT_TOKEN is required when using --post-to-slack")

        if args.recipients_config:
            recipient_digests = build_recipient_digests(args.recipients_config, digests)
            recipient_payloads = [
                (
                    recipient,
                    build_slack_payload(personalized_digests, report_date=report_date, lookback_days=args.lookback_days),
                )
                for recipient, personalized_digests in recipient_digests
            ]
            post_slack_dms(bot_token, recipient_payloads)
        elif user_id:
            slack_payload = build_slack_payload(digests, report_date=report_date, lookback_days=args.lookback_days)
            post_slack_dm(bot_token, user_id, slack_payload)
        else:
            raise SystemExit("Provide SLACK_USER_ID or --recipients-config when using --post-to-slack")

    print(f"Generated {output}")


if __name__ == "__main__":
    main()
