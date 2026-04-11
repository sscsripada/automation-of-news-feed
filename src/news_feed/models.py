from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class Company:
    name: str
    category: str
    query: str
    notes: str = ""


@dataclass(slots=True)
class Recipient:
    name: str
    slack_user_id: str
    companies: list[str]


@dataclass(slots=True)
class Article:
    title: str
    link: str
    published: datetime | None
    source: str
    summary: str = ""


@dataclass(slots=True)
class CompanyDigest:
    company: Company
    articles: list[Article] = field(default_factory=list)
    bullets: list[str] = field(default_factory=list)
    takeaway: str = ""
    used_llm: bool = False
    fetch_error: str = ""
