import hashlib
import logging

from openai import OpenAI
from pydantic import BaseModel

from brain.app.config import settings
from brain.app.models import (
    AnalyzeResponse,
    CoverLetter,
    JobEntities,
    JobSource,
    MatchResult,
    TokenUsage,
)
from brain.app.prompts import (
    SYSTEM_ANALYZE,
    SYSTEM_COVER_LETTER,
    USER_ANALYZE,
    USER_COVER_LETTER,
)

logger = logging.getLogger(__name__)

# gpt-4o-mini list prices (USD per 1M tokens) — update if you change models
_PRICE_PROMPT_PER_1M = 0.15
_PRICE_COMPLETION_PER_1M = 0.60


def _usage_from_completion(completion) -> tuple[int, int, int]:
    usage = getattr(completion, "usage", None)
    if usage is None:
        return 0, 0, 0
    prompt = int(getattr(usage, "prompt_tokens", 0) or 0)
    completion_tok = int(getattr(usage, "completion_tokens", 0) or 0)
    total = int(getattr(usage, "total_tokens", 0) or (prompt + completion_tok))
    return prompt, completion_tok, total


def _estimate_cost_usd(prompt_tokens: int, completion_tokens: int) -> float:
    return round(
        (prompt_tokens / 1_000_000) * _PRICE_PROMPT_PER_1M
        + (completion_tokens / 1_000_000) * _PRICE_COMPLETION_PER_1M,
        6,
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
        usage = TokenUsage()

        entities, match = self._extract_and_match(cv, job_text, job_url, usage)
        threshold = settings.alert_threshold
        should_alert = match.score >= threshold

        # Cover letter only for high matches — saves tokens on weak fits
        cover: CoverLetter | None = None
        if should_alert:
            cover = self._generate_cover_letter(
                cv=cv,
                entities=entities,
                match=match,
                usage=usage,
            )
            usage.cover_letter_generated = True

        usage.estimated_cost_usd = _estimate_cost_usd(
            usage.prompt_tokens, usage.completion_tokens
        )
        logger.info(
            "token_usage score=%s cover=%s prompt=%s completion=%s total=%s "
            "calls=%s est_usd=%s company=%s title=%s",
            match.score,
            usage.cover_letter_generated,
            usage.prompt_tokens,
            usage.completion_tokens,
            usage.total_tokens,
            usage.calls,
            usage.estimated_cost_usd,
            entities.company,
            entities.title,
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
            token_usage=usage,
        )

    def _extract_and_match(
        self,
        cv: str,
        job_text: str,
        job_url: str | None,
        usage: TokenUsage,
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
        p, c, t = _usage_from_completion(completion)
        usage.prompt_tokens += p
        usage.completion_tokens += c
        usage.total_tokens += t
        usage.calls += 1

        parsed = completion.choices[0].message.parsed
        if parsed is None:
            raise RuntimeError("Model returned empty structured output")
        return parsed.entities, parsed.match

    def _generate_cover_letter(
        self,
        cv: str,
        entities: JobEntities,
        match: MatchResult,
        usage: TokenUsage,
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
        p, c, t = _usage_from_completion(completion)
        usage.prompt_tokens += p
        usage.completion_tokens += c
        usage.total_tokens += t
        usage.calls += 1

        letter = completion.choices[0].message.parsed
        if letter is None:
            raise RuntimeError("Cover letter generation failed")
        return letter


class _CombinedAnalysis(BaseModel):
    entities: JobEntities
    match: MatchResult
