from news_feed.models import Company, CompanyDigest, Recipient
from news_feed.pipeline import build_recipient_digests


def test_build_recipient_digests_filters_by_company_name(tmp_path) -> None:
    config = tmp_path / "recipients.csv"
    config.write_text(
        "\n".join(
            [
                "name,slack_user_id,company",
                "Alice,U123,Oracle",
                "Alice,U123,AWS",
                "Bob,U456,JLL",
            ]
        )
    )

    digests = [
        CompanyDigest(company=Company(name="Oracle", category="customer", query="Oracle")),
        CompanyDigest(company=Company(name="AWS", category="competitor", query="AWS")),
        CompanyDigest(company=Company(name="Microsoft", category="competitor", query="Microsoft")),
    ]

    recipient_digests = build_recipient_digests(config, digests)

    assert len(recipient_digests) == 1
    recipient, personalized = recipient_digests[0]
    assert recipient.name == "Alice"
    assert [digest.company.name for digest in personalized] == ["Oracle", "AWS"]
