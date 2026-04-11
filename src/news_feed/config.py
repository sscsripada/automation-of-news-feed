from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import openpyxl
import xlrd
import yaml

from news_feed.models import Company, Recipient


def load_watchlist(config_path: str | Path) -> list[Company]:
    path = Path(config_path)
    companies = _load_company_records(path)
    watchlist: list[Company] = []

    for item in companies:
        watchlist.append(
            Company(
                name=item["name"].strip(),
                category=item["category"].strip().lower(),
                query=item["query"].strip(),
                notes=(item.get("notes") or "").strip(),
            )
        )

    return watchlist


def load_recipients(config_path: str | Path) -> list[Recipient]:
    path = Path(config_path)
    entries = _load_recipient_records(path)
    recipients_by_user: dict[str, Recipient] = {}

    for item in entries:
        user_id = item["slack_user_id"].strip()
        if user_id not in recipients_by_user:
            recipients_by_user[user_id] = Recipient(
                name=item["name"].strip(),
                slack_user_id=user_id,
                companies=[],
            )

        companies = _normalize_company_list(item)
        for company in companies:
            if company not in recipients_by_user[user_id].companies:
                recipients_by_user[user_id].companies.append(company)

    return list(recipients_by_user.values())


def _load_company_records(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        data = yaml.safe_load(path.read_text()) or {}
        return data.get("companies", [])
    if suffix == ".csv":
        return _load_csv_records(path)
    if suffix == ".xlsx":
        return _load_xlsx_records(path)
    if suffix == ".xls":
        return _load_xls_records(path)
    raise ValueError(f"Unsupported watchlist format: {path.suffix}")


def _load_recipient_records(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        data = yaml.safe_load(path.read_text()) or {}
        return data.get("employees", [])
    if suffix == ".csv":
        return _load_csv_records(path)
    if suffix == ".xlsx":
        return _load_xlsx_records(path)
    if suffix == ".xls":
        return _load_xls_records(path)
    raise ValueError(f"Unsupported recipient format: {path.suffix}")


def _load_csv_records(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return [_normalize_row(row) for row in reader]


def _load_xlsx_records(path: Path) -> list[dict[str, str]]:
    workbook = openpyxl.load_workbook(path, data_only=True)
    sheet = workbook.active
    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        return []
    headers = [str(cell).strip() if cell is not None else "" for cell in rows[0]]
    records: list[dict[str, str]] = []
    for row in rows[1:]:
        mapped = {
            headers[index]: _stringify_cell(row[index]) if index < len(row) else ""
            for index in range(len(headers))
            if headers[index]
        }
        records.append(_normalize_row(mapped))
    return records


def _load_xls_records(path: Path) -> list[dict[str, str]]:
    workbook = xlrd.open_workbook(path)
    sheet = workbook.sheet_by_index(0)
    if sheet.nrows == 0:
        return []
    headers = [str(sheet.cell_value(0, col)).strip() for col in range(sheet.ncols)]
    records: list[dict[str, str]] = []
    for row_index in range(1, sheet.nrows):
        mapped = {
            headers[col_index]: _stringify_cell(sheet.cell_value(row_index, col_index))
            for col_index in range(len(headers))
            if headers[col_index]
        }
        records.append(_normalize_row(mapped))
    return records


def _normalize_row(row: dict[str, Any]) -> dict[str, str]:
    return {str(key).strip().lower(): _stringify_cell(value) for key, value in row.items() if key is not None}


def _normalize_company_list(item: dict[str, str]) -> list[str]:
    if item.get("companies"):
        return [value.strip() for value in _split_multi_value(item["companies"]) if value.strip()]
    if item.get("company"):
        return [item["company"].strip()]
    return []


def _split_multi_value(value: str) -> list[str]:
    normalized = value.replace("|", ",").replace(";", ",")
    return normalized.split(",")


def _stringify_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()
