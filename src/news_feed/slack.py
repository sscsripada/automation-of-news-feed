from __future__ import annotations

import json
from datetime import date
from typing import Any

import requests

from news_feed.models import CompanyDigest, Recipient


SLACK_API_BASE_URL = "https://slack.com/api"


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


def post_slack_dm(bot_token: str, user_id: str, payload: dict[str, Any], timeout: int = 20) -> None:
    headers = {
        "Authorization": f"Bearer {bot_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    open_response = requests.post(
        f"{SLACK_API_BASE_URL}/conversations.open",
        headers=headers,
        json={"users": user_id},
        timeout=timeout,
    )
    open_response.raise_for_status()
    open_data = open_response.json()
    if not open_data.get("ok"):
        raise RuntimeError(f"Slack conversations.open failed: {open_data.get('error', 'unknown_error')}")

    channel_id = open_data["channel"]["id"]
    message_payload = {
        "channel": channel_id,
        "text": payload["text"],
        "blocks": payload["blocks"],
    }
    message_response = requests.post(
        f"{SLACK_API_BASE_URL}/chat.postMessage",
        headers=headers,
        json=message_payload,
        timeout=timeout,
    )
    message_response.raise_for_status()
    message_data = message_response.json()
    if not message_data.get("ok"):
        raise RuntimeError(f"Slack chat.postMessage failed: {message_data.get('error', 'unknown_error')}")


def post_slack_dms(bot_token: str, recipient_payloads: list[tuple[Recipient, dict[str, Any]]], timeout: int = 20) -> None:
    for recipient, payload in recipient_payloads:
        post_slack_dm(bot_token, recipient.slack_user_id, payload, timeout=timeout)


def write_slack_payload(output_path: str, payload: dict[str, Any]) -> None:
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")


def _trim_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."
