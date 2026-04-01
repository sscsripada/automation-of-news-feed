from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI

from news_feed.models import Article, Company


class NewsSummarizer:
    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5-mini")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    @property
    def enabled(self) -> bool:
        return self.client is not None

    def summarize(self, company: Company, articles: list[Article]) -> tuple[list[str], str, bool]:
        if not articles:
            return ["No recent articles found in the selected window."], "No notable update detected.", False

        if self.client is None:
            return self._fallback_summary(company, articles), self._fallback_takeaway(company, articles), False

        try:
            payload = self._llm_summary(company, articles)
            bullets = [bullet.strip() for bullet in payload.get("bullets", []) if bullet.strip()]
            takeaway = (payload.get("takeaway") or "").strip()

            if bullets and takeaway:
                return bullets[:3], takeaway, True
        except Exception:
            pass

        return self._fallback_summary(company, articles), self._fallback_takeaway(company, articles), False

    def _llm_summary(self, company: Company, articles: list[Article]) -> dict[str, Any]:
        rendered_articles = []
        for article in articles:
            published = article.published.isoformat() if article.published else "unknown"
            rendered_articles.append(
                {
                    "title": article.title,
                    "source": article.source,
                    "published": published,
                    "summary": article.summary,
                    "link": article.link,
                }
            )

        prompt = {
            "company": company.name,
            "category": company.category,
            "notes": company.notes,
            "articles": rendered_articles,
            "instructions": [
                "Return strict JSON.",
                "Include keys: bullets, takeaway.",
                "bullets must be an array of 2 or 3 concise business-focused bullets.",
                "takeaway must be one sentence about why this matters for account planning or competitive intelligence.",
                "Do not invent facts that are not present in the provided articles.",
            ],
        }

        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": "You summarize company news for daily executive check-ins. Return only JSON.",
                },
                {
                    "role": "user",
                    "content": json.dumps(prompt),
                },
            ],
        )
        content = response.output_text.strip()
        return json.loads(content)

    def _fallback_summary(self, company: Company, articles: list[Article]) -> list[str]:
        bullets = []
        for article in articles[:3]:
            source_text = f" ({article.source})" if article.source else ""
            bullets.append(f"{article.title}{source_text}")

        if not bullets:
            bullets.append(f"No headlines surfaced for {company.name}.")

        return bullets

    def _fallback_takeaway(self, company: Company, articles: list[Article]) -> str:
        if not articles:
            return "No immediate action is suggested."
        return f"Monitor {company.name} for follow-up coverage and decide whether any of these headlines merit direct outreach."

