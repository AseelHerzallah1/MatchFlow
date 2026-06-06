from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]
CV_PATH = ROOT / "cv" / "candidate_cv.md"
GITHUB_CONTEXT_PATH = ROOT / "cv" / "github_context.md"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    brain_api_key: str = "dev-key"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    alert_threshold: int = 80
    notion_api_key: str = ""
    notion_database_id: str = ""
    github_username: str = ""

    @property
    def cv_text(self) -> str:
        if CV_PATH.is_file():
            return CV_PATH.read_text(encoding="utf-8").strip()
        return "No CV loaded. Add cv/candidate_cv.md"

    @property
    def candidate_context(self) -> str:
        """CV + GitHub portfolio for richer matching."""
        from brain.app.services.github_profile import get_github_context

        parts = [self.cv_text]
        gh = get_github_context(self.github_username)
        if gh:
            parts.append(gh)
        return "\n\n---\n\n".join(parts)


settings = Settings()
