from __future__ import annotations

import json
from datetime import date
from typing import Any

import requests

from news_feed.models import CompanyDigest


def build_slack_payload(digests: list[CompanyDigest], report_date: date, lookback_days: int) -> dict[str, Any]:
    summary_text = f"Daily company news check-in for {report_date.isoformat()}."
    blocks: list[dict[str, Any]] = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"Daily News Check-In | {report_date.isoformat()}"},
        },
        {
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": f"Coverage window: last {lookback_days} day(s)."}],
        },
    ]

    for digest in digests:
        emoji = ":handshake:" if digest.company.category == "customer" else ":crossed_swords:"
        section_lines = [f"{emoji} *{digest.company.name}* ({digest.company.category})"]

        for bullet in digest.bullets[:3]:
            section_lines.append(f"• {bullet}")

        section_lines.append(f"*Takeaway:* {digest.takeaway}")

        if digest.articles:
            top_links = []
            for article in digest.articles[:2]:
                title = _trim_text(article.title, 100)
                top_links.append(f"<{article.link}|{title}>")
            section_lines.append("*Links:* " + " | ".join(top_links))

        blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "\n".join(section_lines)},
            }
        )
        blocks.append({"type": "divider"})

    if blocks and blocks[-1]["type"] == "divider":
        blocks.pop()

    return {"text": summary_text, "blocks": blocks}


def post_slack_webhook(webhook_url: str, payload: dict[str, Any], timeout: int = 20) -> None:
    response = requests.post(webhook_url, json=payload, timeout=timeout)
    response.raise_for_status()


def write_slack_payload(output_path: str, payload: dict[str, Any]) -> None:
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def _trim_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."
