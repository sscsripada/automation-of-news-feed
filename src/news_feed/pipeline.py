from __future__ import annotations

from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
import sys
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

import feedparser

from news_feed.config import load_watchlist
from news_feed.models import Article, Company, CompanyDigest
from news_feed.summarizer import NewsSummarizer


GOOGLE_NEWS_URL = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"


def generate_checkin(
    config_path: str | Path,
    output_path: str | Path,
    lookback_days: int = 2,
    max_articles: int = 5,
    model: str | None = None,
) -> Path:
    companies = load_watchlist(config_path)
    summarizer = NewsSummarizer(model=model)
    digests = build_digests(companies, lookback_days=lookback_days, max_articles=max_articles, summarizer=summarizer)

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_markdown(digests, report_date=date.today(), lookback_days=lookback_days))
    return target


def collect_digests(
    config_path: str | Path,
    lookback_days: int = 2,
    max_articles: int = 5,
    model: str | None = None,
) -> tuple[list[CompanyDigest], date]:
    companies = load_watchlist(config_path)
    summarizer = NewsSummarizer(model=model)
    digests = build_digests(companies, lookback_days=lookback_days, max_articles=max_articles, summarizer=summarizer)
    return digests, date.today()


def build_digests(
    companies: list[Company],
    lookback_days: int,
    max_articles: int,
    summarizer: NewsSummarizer,
) -> list[CompanyDigest]:
    digests: list[CompanyDigest] = []
    for company in companies:
        fetch_error = ""
        try:
            articles = fetch_company_news(company, lookback_days=lookback_days, max_articles=max_articles)
        except Exception as exc:
            articles = []
            fetch_error = str(exc)
            print(f"Warning: failed to fetch news for {company.name}: {exc}", file=sys.stderr)

        if fetch_error:
            bullets = ["Unable to fetch live news for this company during the current run."]
            takeaway = "Retry the run or adjust the company query if this keeps happening."
            used_llm = False
        else:
            bullets, takeaway, used_llm = summarizer.summarize(company, articles)

        digests.append(
            CompanyDigest(
                company=company,
                articles=articles,
                bullets=bullets,
                takeaway=takeaway,
                used_llm=used_llm,
                fetch_error=fetch_error,
            )
        )
    return digests


def fetch_company_news(company: Company, lookback_days: int, max_articles: int) -> list[Article]:
    url = GOOGLE_NEWS_URL.format(query=quote_plus(company.query))
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    cutoff = datetime.now(UTC) - timedelta(days=lookback_days)

    with urlopen(request, timeout=20) as response:
        parsed = feedparser.parse(response.read())

    seen: set[tuple[str, str]] = set()
    articles: list[Article] = []

    for entry in parsed.entries:
        published = _parse_published(entry.get("published"))
        if published and published < cutoff:
            continue

        title = (entry.get("title") or "").strip()
        link = (entry.get("link") or "").strip()
        source = _extract_source(title)
        normalized = (title.lower(), link.lower())

        if not title or not link or normalized in seen:
            continue

        seen.add(normalized)
        articles.append(
            Article(
                title=title,
                link=link,
                published=published,
                source=source,
                summary=(entry.get("summary") or "").strip(),
            )
        )

        if len(articles) >= max_articles:
            break

    return articles


def render_markdown(digests: list[CompanyDigest], report_date: date, lookback_days: int) -> str:
    grouped: dict[str, list[CompanyDigest]] = defaultdict(list)
    for digest in digests:
        grouped[digest.company.category].append(digest)

    lines = [
        f"# Daily News Check-In - {report_date.isoformat()}",
        "",
        f"Recent coverage window: last {lookback_days} day(s).",
        "",
    ]

    category_order = ["customer", "competitor"]
    ordered_categories = [category for category in category_order if category in grouped]
    ordered_categories.extend(category for category in grouped if category not in ordered_categories)

    for category in ordered_categories:
        lines.append(f"## {category.title()}s")
        lines.append("")
        for digest in grouped[category]:
            lines.extend(_render_company_block(digest))
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def _render_company_block(digest: CompanyDigest) -> list[str]:
    lines = [f"### {digest.company.name}", ""]

    for bullet in digest.bullets:
        lines.append(f"- {bullet}")

    lines.extend(["", f"**Takeaway:** {digest.takeaway}", ""])

    if digest.articles:
        lines.append("**Sources**")
        lines.append("")
        for article in digest.articles:
            published = article.published.date().isoformat() if article.published else "Unknown date"
            lines.append(f"- [{article.title}]({article.link}) - {article.source or 'Unknown source'} - {published}")
    else:
        lines.append("No source links captured.")

    lines.append("")
    return lines


def _parse_published(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _extract_source(title: str) -> str:
    if " - " not in title:
        return ""
    return title.rsplit(" - ", 1)[-1].strip()
