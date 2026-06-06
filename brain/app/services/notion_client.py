"""Notion CRM writer — maps to your Career Quest / Job Hunting database."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from brain.app.config import settings
from brain.app.models import AnalyzeResponse


class NotionCRM:
    """Writes analyzed jobs into the Career Quest → Job Hunting table."""

    def __init__(
        self,
        api_key: str | None = None,
        database_id: str | None = None,
    ) -> None:
        self.api_key = api_key or settings.notion_api_key
        self.database_id = database_id or settings.notion_database_id
        self.base = "https://api.notion.com/v1"
        self.version = "2022-06-28"

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.database_id)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": self.version,
            "Content-Type": "application/json",
        }

    def create_job_row(self, result: AnalyzeResponse, job_text: str) -> dict[str, Any]:
        if not self.configured:
            raise RuntimeError("Notion API key or database ID missing")

        e = result.entities
        m = result.match
        cover = ""
        if result.cover_letter:
            cover = result.cover_letter.body_en

        now = datetime.now(timezone.utc).isoformat()

        properties: dict[str, Any] = {
            "Company": {"title": [{"text": {"content": e.company[:100]}}]},
            "Job Title": {"rich_text": [{"text": {"content": e.title[:100]}}]},
            "Match Score": {"number": m.score},
            "Match Summary": {
                "rich_text": [{"text": {"content": m.summary_en[:2000]}}]
            },
            "Status": {"select": {"name": "New"}},
            "Source": {"select": {"name": result.source.value.capitalize()}},
            "Cover Letter": {"rich_text": [{"text": {"content": cover[:2000]}}]},
            "Processed At": {"date": {"start": now}},
        }

        if result.job_url:
            properties["Job description"] = {"url": result.job_url}

        if e.technologies:
            properties["Technologies"] = {
                "multi_select": [{"name": t[:100]} for t in e.technologies[:10]]
            }
        if e.years_experience_required is not None:
            properties["Years Required"] = {"number": e.years_experience_required}

        payload = {
            "parent": {"database_id": self.database_id},
            "properties": properties,
        }

        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{self.base}/pages",
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()
