import hashlib

from openai import OpenAI
from pydantic import BaseModel

from brain.app.config import settings
from brain.app.models import (
    AnalyzeResponse,
    CoverLetter,
    JobEntities,
    JobSource,
    MatchResult,
)
from brain.app.prompts import (
    SYSTEM_ANALYZE,
    SYSTEM_COVER_LETTER,
    USER_ANALYZE,
    USER_COVER_LETTER,
)


class BrainAnalyzer:
    def __init__(self) -> None:
        self._client: OpenAI | None = None
        self.model = settings.openai_model

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            if not settings.openai_api_key:
                raise RuntimeError("OPENAI_API_KEY not configured")
            self._client = OpenAI(api_key=settings.openai_api_key)
        return self._client

    def _dedupe_key(self, job_url: str | None, job_text: str) -> str:
        raw = (job_url or "").strip() or job_text[:2000]
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def analyze(
        self,
        job_text: str,
        job_url: str | None,
        source: JobSource,
    ) -> AnalyzeResponse:
        cv = settings.candidate_context

        entities, match = self._extract_and_match(cv, job_text, job_url)
        threshold = settings.alert_threshold
        should_alert = match.score >= threshold

        cover: CoverLetter | None = None
        if should_alert:
            cover = self._generate_cover_letter(
                cv=cv,
                entities=entities,
                match=match,
            )

        return AnalyzeResponse(
            entities=entities,
            match=match,
            cover_letter=cover,
            should_alert=should_alert,
            alert_threshold=threshold,
            job_url=job_url,
            source=source,
            dedupe_key=self._dedupe_key(job_url, job_text),
        )

    def _extract_and_match(
        self, cv: str, job_text: str, job_url: str | None
    ) -> tuple[JobEntities, MatchResult]:
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_ANALYZE},
                {
                    "role": "user",
                    "content": USER_ANALYZE.format(
                        cv=cv, job=job_text, url=job_url or "N/A"
                    ),
                },
            ],
            response_format=_CombinedAnalysis,
        )
        parsed = completion.choices[0].message.parsed
        if parsed is None:
            raise RuntimeError("Model returned empty structured output")
        return parsed.entities, parsed.match

    def _generate_cover_letter(
        self,
        cv: str,
        entities: JobEntities,
        match: MatchResult,
    ) -> CoverLetter:
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_COVER_LETTER},
                {
                    "role": "user",
                    "content": USER_COVER_LETTER.format(
                        company=entities.company,
                        title=entities.title,
                        tech=", ".join(entities.technologies),
                        score=match.score,
                        summary=match.summary_en,
                        gaps=", ".join(match.gaps) or "none noted",
                        cv=cv[:4000],
                    ),
                },
            ],
            response_format=CoverLetter,
        )
        letter = completion.choices[0].message.parsed
        if letter is None:
            raise RuntimeError("Cover letter generation failed")
        return letter


class _CombinedAnalysis(BaseModel):
    entities: JobEntities
    match: MatchResult
