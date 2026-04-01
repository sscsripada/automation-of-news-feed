from datetime import UTC, date, datetime

from news_feed.models import Article, Company, CompanyDigest
from news_feed.slack import build_slack_payload


def test_build_slack_payload_contains_company_sections() -> None:
    digest = CompanyDigest(
        company=Company(name="Oracle", category="customer", query="Oracle"),
        bullets=["Oracle launched an updated cloud offering."],
        takeaway="Worth sharing with the account team.",
        articles=[
            Article(
                title="Oracle launches updated cloud offering - Example",
                link="https://example.com/oracle",
                source="Example",
                published=datetime(2026, 4, 1, tzinfo=UTC),
            )
        ],
    )

    payload = build_slack_payload([digest], report_date=date(2026, 4, 1), lookback_days=2)

    assert payload["text"] == "Daily company news check-in for 2026-04-01."
    assert payload["blocks"][0]["type"] == "header"
    assert "Oracle" in payload["blocks"][2]["text"]["text"]
    assert "Takeaway" in payload["blocks"][2]["text"]["text"]
    assert "Links:" in payload["blocks"][2]["text"]["text"]
