"""Fetch public GitHub repos/languages to enrich job matching beyond the CV file."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

from brain.app.config import GITHUB_CONTEXT_PATH, ROOT

CACHE_HOURS = 6


def _format_repo(repo: dict) -> str:
    langs = repo.get("languages") or {}
    top_langs = sorted(langs, key=langs.get, reverse=True)[:6]
    lang_str = ", ".join(top_langs) if top_langs else "see repo"
    desc = (repo.get("description") or "").strip()
    lines = [f"- **{repo['name']}** ({lang_str}) — {repo['url']}"]
    if desc:
        lines.append(f"  {desc}")
    return "\n".join(lines)


def fetch_repos(username: str) -> list[dict]:
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(
            f"https://api.github.com/users/{username}/repos",
            params={"per_page": 100, "sort": "updated"},
            headers={"Accept": "application/vnd.github+json"},
        )
        resp.raise_for_status()
        repos = resp.json()
        enriched = []
        for repo in repos:
            langs: dict[str, int] = {}
            if repo.get("languages_url"):
                lr = client.get(repo["languages_url"], timeout=15.0)
                if lr.status_code == 200:
                    langs = lr.json()
            enriched.append(
                {
                    "name": repo["name"],
                    "description": repo.get("description") or "",
                    "url": repo["html_url"],
                    "languages": langs,
                }
            )
        return enriched


def _matching_notes(repos: list[dict], skills: list[str]) -> str:
    """Auto-generated hints for the LLM — derived from live repo data."""
    names = {r["name"].lower() for r in repos}
    lines: list[str] = []
    lang_blob = ", ".join(skills).lower()

    if any(k in lang_blob for k in ("javascript", "typescript", "html", "css")):
        front = [r["name"] for r in repos if any(
            x in (r.get("languages") or {}) for x in ("JavaScript", "TypeScript", "HTML", "CSS")
        )][:4]
        if front:
            lines.append(f"- Frontend / web: {', '.join(front)}.")

    if any(k in lang_blob for k in ("python",)) or any("genai" in n or "ai" in n for n in names):
        ai = [r["name"] for r in repos if "ai" in r["name"].lower() or "genai" in r["name"].lower() or "camera" in r["name"].lower()][:4]
        if ai:
            lines.append(f"- AI / ML projects: {', '.join(ai)}.")

    if any(k in lang_blob for k in ("c", "c++", "java")) or any("os" in n or "spl" in n or "scheme" in n for n in names):
        sys_repos = [r["name"] for r in repos if any(
            x in r["name"].lower() for x in ("os", "spl", "scheme", "operating", "system")
        )][:4]
        if sys_repos:
            lines.append(f"- Systems / low-level: {', '.join(sys_repos)}.")

    recent = [r["name"] for r in repos[:5]]
    if recent:
        lines.append(f"- Most recently updated repos: {', '.join(recent)}.")

    return "\n".join(lines) if lines else "- See repository list above for demonstrated skills."


def build_github_markdown(username: str, repos: list[dict]) -> str:
    all_langs: dict[str, int] = {}
    for repo in repos:
        for lang, count in (repo.get("languages") or {}).items():
            all_langs[lang] = all_langs.get(lang, 0) + count

    skills = sorted(all_langs, key=all_langs.get, reverse=True)
    repo_blocks = "\n".join(_format_repo(r) for r in repos)
    notes = _matching_notes(repos, skills)

    return f"""# GitHub portfolio — @{username}
Profile: https://github.com/{username}
Synced: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}

## Languages used across repositories (evidence)
{", ".join(skills) if skills else "n/a"}

## Repositories
{repo_blocks}

## Notes for matching (auto-generated from live GitHub data)
{notes}
"""


def _cache_stale(path: Path) -> bool:
    if not path.is_file():
        return True
    age_h = (datetime.now(timezone.utc).timestamp() - path.stat().st_mtime) / 3600
    return age_h > CACHE_HOURS


def sync_github_context(username: str, force: bool = False) -> str:
    if not username:
        return ""
    path = GITHUB_CONTEXT_PATH
    if not force and not _cache_stale(path):
        return path.read_text(encoding="utf-8")

    repos = fetch_repos(username)
    markdown = build_github_markdown(username, repos)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")
    snapshot = ROOT / "cv" / "github_snapshot.json"
    snapshot.write_text(
        json.dumps(repos, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return markdown


def get_github_context(username: str) -> str:
    if not username:
        return ""
    try:
        return sync_github_context(username, force=False)
    except Exception:
        if GITHUB_CONTEXT_PATH.is_file():
            return GITHUB_CONTEXT_PATH.read_text(encoding="utf-8")
        return ""
