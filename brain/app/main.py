from fastapi import Depends, FastAPI, Header, HTTPException

from brain.app.config import CV_PATH, GITHUB_CONTEXT_PATH, settings
from brain.app.services.github_profile import sync_github_context
from brain.app.models import AnalyzeRequest, AnalyzeResponse, HealthResponse
from brain.app.services.alerts import dispatch_alerts
from brain.app.services.analyzer import BrainAnalyzer
from brain.app.services.notion_client import NotionCRM

app = FastAPI(
    title="MatchFlow Brain",
    description="Place-IL Quest #2 — job analysis, match scoring, cover letters",
    version="0.1.0",
)

analyzer = BrainAnalyzer()


def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if not x_api_key or x_api_key != settings.brain_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        cv_loaded=CV_PATH.is_file(),
        github_loaded=GITHUB_CONTEXT_PATH.is_file(),
        github_username=settings.github_username,
        model=settings.openai_model,
    )


@app.post("/api/v1/sync-github")
def sync_github(_: None = Depends(verify_api_key)) -> dict:
    if not settings.github_username:
        raise HTTPException(status_code=400, detail="GITHUB_USERNAME not set in .env")
    text = sync_github_context(settings.github_username, force=True)
    return {"ok": True, "chars": len(text), "username": settings.github_username}


@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
def analyze_job(
    body: AnalyzeRequest,
    _: None = Depends(verify_api_key),
) -> AnalyzeResponse:
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY not configured")
    return analyzer.analyze(
        job_text=body.job_text.strip(),
        job_url=body.job_url,
        source=body.source,
    )


@app.post("/api/v1/pipeline")
def full_pipeline(
    body: AnalyzeRequest,
    persist_notion: bool = True,
    send_alerts: bool = True,
    notion_min_score: int = 0,
    _: None = Depends(verify_api_key),
) -> dict:
    """Analyze + optional Notion row + optional alerts — one call for n8n/Telegram."""
    result = analyzer.analyze(
        job_text=body.job_text.strip(),
        job_url=body.job_url,
        source=body.source,
    )
    out: dict = {"analysis": result.model_dump(), "notion": None, "alerts": None}

    if persist_notion and result.match.score < notion_min_score:
        out["notion_skipped"] = (
            f"Score {result.match.score} below notion_min_score={notion_min_score}"
        )
    elif persist_notion:
        crm = NotionCRM()
        if not crm.configured:
            out["notion_error"] = "NOTION_API_KEY or NOTION_DATABASE_ID missing in .env"
        else:
            try:
                out["notion"] = crm.create_job_row(result, body.job_text)
            except Exception as exc:  # noqa: BLE001
                out["notion_error"] = str(exc)

    if send_alerts:
        out["alerts"] = dispatch_alerts(result)

    return out
