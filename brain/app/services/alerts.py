"""Send high-match alerts to Slack and/or Telegram."""

from __future__ import annotations

import os

import httpx

from brain.app.models import AnalyzeResponse


def format_alert_message(result: AnalyzeResponse) -> str:
    e = result.entities
    m = result.match
    lines = [
        f"🎯 *MatchFlow* — Score *{m.score}/100*",
        f"*{e.title}* @ {e.company}",
    ]
    if result.job_url:
        lines.append(f"🔗 {result.job_url}")
    lines.append("")
    lines.append(f"✓ {m.summary_en}")
    if m.gaps:
        lines.append(f"△ Gaps: {', '.join(m.gaps)}")
    if result.cover_letter:
        lines.extend(
            [
                "",
                "—— Cover letter (EN) ——",
                result.cover_letter.body_en,
            ]
        )
    return "\n".join(lines)


def send_slack_alert(message: str, webhook_url: str | None = None) -> bool:
    url = webhook_url or os.getenv("SLACK_WEBHOOK_URL", "")
    if not url:
        return False
    with httpx.Client(timeout=15.0) as client:
        resp = client.post(url, json={"text": message})
        resp.raise_for_status()
    return True


def send_telegram_alert(
    message: str,
    bot_token: str | None = None,
    chat_id: str | None = None,
) -> bool:
    token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat = chat_id or os.getenv("TELEGRAM_ALERT_CHAT_ID", "")
    if not token or not chat:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    with httpx.Client(timeout=15.0) as client:
        resp = client.post(
            url,
            json={"chat_id": chat, "text": message, "parse_mode": "Markdown"},
        )
        resp.raise_for_status()
    return True


def dispatch_alerts(result: AnalyzeResponse) -> dict[str, bool]:
    if not result.should_alert:
        return {"slack": False, "telegram": False}
    msg = format_alert_message(result)
    return {
        "slack": send_slack_alert(msg),
        "telegram": send_telegram_alert(msg),
    }
