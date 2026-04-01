from pathlib import Path

from news_feed.config import load_watchlist


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

