from __future__ import annotations

import argparse
import os
from datetime import date
from pathlib import Path

from news_feed.pipeline import generate_checkin


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
    return parser


def main() -> None:
    args = build_parser().parse_args()
    output = generate_checkin(
        config_path=Path(args.config),
        output_path=Path(args.output),
        lookback_days=args.lookback_days,
        max_articles=args.max_articles,
        model=args.model,
    )
    print(f"Generated {output}")


if __name__ == "__main__":
    main()

