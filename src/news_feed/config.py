from __future__ import annotations

from pathlib import Path

import yaml

from news_feed.models import Company


def load_watchlist(config_path: str | Path) -> list[Company]:
    path = Path(config_path)
    data = yaml.safe_load(path.read_text()) or {}
    companies = data.get("companies", [])
    watchlist: list[Company] = []

    for item in companies:
        watchlist.append(
            Company(
                name=item["name"].strip(),
                category=item["category"].strip().lower(),
                query=item["query"].strip(),
                notes=(item.get("notes") or "").strip(),
            )
        )

    return watchlist

