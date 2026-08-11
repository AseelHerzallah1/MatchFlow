from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class JobSource(str, Enum):
    rss = "rss"
    telegram = "telegram"
    manual = "manual"
    scraper = "scraper"
    form = "form"


class AnalyzeRequest(BaseModel):
    job_text: str = Field(..., min_length=40, description="Raw job posting text")
    job_url: str | None = None
    source: JobSource = JobSource.manual


class JobEntities(BaseModel):
    company: str
    title: str
    technologies: list[str] = Field(default_factory=list)
    years_experience_required: float | None = Field(
        None, description="Minimum years if stated; null if unclear"
    )
    location: str | None = None
    employment_type: str | None = None


class MatchResult(BaseModel):
    score: int = Field(..., ge=1, le=100)
    summary_en: str = Field(..., description="2-3 sentence fit explanation in English")
    summary_he: str = Field(..., description="Same explanation in Hebrew")
    strengths: list[str] = Field(default_factory=list, max_length=5)
    gaps: list[str] = Field(default_factory=list, max_length=5)


class CoverLetter(BaseModel):
    subject_line: str
    body_en: str
    body_he: str


class TokenUsage(BaseModel):
    """OpenAI token accounting for one analyze/pipeline run."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    calls: int = 0
    cover_letter_generated: bool = False
    estimated_cost_usd: float = 0.0


class AnalyzeResponse(BaseModel):
    entities: JobEntities
    match: MatchResult
    cover_letter: CoverLetter | None = None
    should_alert: bool
    alert_threshold: int
    job_url: str | None = None
    source: JobSource
    dedupe_key: str | None = None
    token_usage: TokenUsage | None = None


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    cv_loaded: bool
    github_loaded: bool
    github_username: str
    model: str
