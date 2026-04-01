from datetime import UTC, date, datetime

from news_feed.models import Article, Company, CompanyDigest
from news_feed.pipeline import render_markdown


def test_render_markdown_groups_companies() -> None:
    customer = Company(name="Oracle", category="customer", query="Oracle")
    competitor = Company(name="AWS", category="competitor", query="AWS")

    customer_digest = CompanyDigest(
        company=customer,
        bullets=["Oracle announced a new partner motion."],
        takeaway="Worth checking for account expansion relevance.",
        articles=[
            Article(
                title="Oracle expands partner program - Example News",
                link="https://example.com/oracle",
                source="Example News",
                published=datetime(2026, 4, 1, tzinfo=UTC),
            )
        ],
    )
    competitor_digest = CompanyDigest(
        company=competitor,
        bullets=["AWS highlighted a new enterprise AI launch."],
        takeaway="Competitive cloud messaging may intensify.",
        articles=[],
    )

    markdown = render_markdown([customer_digest, competitor_digest], report_date=date(2026, 4, 1), lookback_days=2)

    assert "# Daily News Check-In - 2026-04-01" in markdown
    assert "## Customers" in markdown
    assert "## Competitors" in markdown
    assert "### Oracle" in markdown
    assert "### AWS" in markdown

