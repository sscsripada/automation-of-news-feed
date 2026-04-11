from pathlib import Path

from news_feed.config import load_recipients, load_watchlist


def test_load_watchlist(tmp_path: Path) -> None:
    config = tmp_path / "watchlist.yaml"
    config.write_text(
        "\n".join(
            [
                "companies:",
                "  - name: Example Corp",
                "    category: customer",
                "    query: Example Corp news",
                "    notes: account watch",
            ]
        )
    )

    companies = load_watchlist(config)

    assert len(companies) == 1
    assert companies[0].name == "Example Corp"
    assert companies[0].category == "customer"
    assert companies[0].query == "Example Corp news"


def test_load_watchlist_from_csv(tmp_path: Path) -> None:
    config = tmp_path / "watchlist.csv"
    config.write_text(
        "\n".join(
            [
                "name,category,query,notes",
                "Oracle,customer,Oracle cloud,enterprise account",
                "AWS,competitor,AWS OR Amazon Web Services,cloud competition",
            ]
        )
    )

    companies = load_watchlist(config)

    assert [company.name for company in companies] == ["Oracle", "AWS"]
    assert companies[1].category == "competitor"


def test_load_recipients_from_csv_groups_companies(tmp_path: Path) -> None:
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

    recipients = load_recipients(config)

    assert len(recipients) == 2
    assert recipients[0].companies == ["Oracle", "AWS"]
    assert recipients[1].slack_user_id == "U456"
