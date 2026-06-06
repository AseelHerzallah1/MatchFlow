"""
MatchFlow Telegram bot — manual job trigger (Quest Phase 1).

Usage (from repo root):
  pip install -r telegram_bot/requirements.txt
  python telegram_bot/bot.py
"""

from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.error import NetworkError, RetryAfter, TimedOut
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.request import HTTPXRequest

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ALLOWED = {
    int(x.strip())
    for x in os.getenv("TELEGRAM_ALLOWED_USER_IDS", "").split(",")
    if x.strip().isdigit()
}
BRAIN_URL = os.getenv("MATCHFLOW_BRAIN_URL", "http://localhost:8001").rstrip("/")
API_KEY = os.getenv("BRAIN_API_KEY", "dev-key")

WELCOME = """שלום! 👋 MatchFlow — בוט חיפוש העבודה שלך

שלח/י:
• טקסט מלא של מודעת משרה, או
• קישור למשרה (נשלח כטקסט — שלב שאיבה ב-n8n לקישורים)

פקודות: /start /help

---
Hi! I'm MatchFlow. Paste a full job posting and I'll score it against your CV.

Tip: Copy jobs from Referally Entry Level (0+) WhatsApp → paste here.
"""


def _allowed(user_id: int) -> bool:
    return not ALLOWED or user_id in ALLOWED


async def _safe_reply(update: Update, text: str, retries: int = 5) -> bool:
    """Send plain-text reply with retries for flaky Telegram connections."""
    if not update.message:
        return False
    chunk = text[:4000]
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            await update.message.reply_text(chunk)
            return True
        except RetryAfter as exc:
            wait = int(exc.retry_after) + 1
            print(f"Telegram rate limit — waiting {wait}s…")
            await asyncio.sleep(wait)
            last_exc = exc
        except (NetworkError, TimedOut, httpx.HTTPError) as exc:
            last_exc = exc
            print(f"Reply attempt {attempt}/{retries} failed: {exc}")
            await asyncio.sleep(2 * attempt)
        except Exception as exc:
            last_exc = exc
            print(f"Reply failed: {exc}")
            break
    print(f"Could not deliver Telegram message: {last_exc}")
    return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user and not _allowed(update.effective_user.id):
        await update.message.reply_text("Unauthorized.")
        return
    await update.message.reply_text(WELCOME)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Paste job text (min ~40 chars). For URLs, use n8n RSS/scraper flow."
    )


async def handle_job_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    if not _allowed(update.effective_user.id):
        await update.message.reply_text("Unauthorized.")
        return

    text = (update.message.text or "").strip()
    if len(text) < 40:
        await update.message.reply_text("Please send a longer job description (40+ chars).")
        return

    await _safe_reply(
        update,
        "מנתח/ת… ⏳ Analyzing (30–60 sec). Results also go to Notion.",
    )

    payload = {
        "job_text": text,
        "job_url": text if text.startswith("http") else None,
        "source": "telegram",
    }

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            resp = await client.post(
                f"{BRAIN_URL}/api/v1/pipeline",
                headers={"X-API-Key": API_KEY},
                json=payload,
                params={"persist_notion": True, "send_alerts": True},
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.ConnectError:
        await update.message.reply_text(
            "Brain API error: cannot reach Brain. Is uvicorn running on port 8001?"
        )
        return
    except Exception as exc:  # noqa: BLE001
        await update.message.reply_text(f"Brain API error: {exc}")
        return

    analysis = data.get("analysis", {})
    entities = analysis.get("entities", {})
    match = analysis.get("match", {})
    score = match.get("score", "?")

    notion_ok = bool(data.get("notion")) and not data.get("notion_error")

    # Message 1 — short (delivers even on weak network)
    headline = (
        f"📊 {entities.get('title', 'Role')} @ {entities.get('company', '?')}\n"
        f"Score: {score}/100\n"
    )
    if notion_ok:
        headline += "📁 Saved to Notion."
    elif data.get("notion_error"):
        headline += f"⚠️ Notion error: {data['notion_error']}"
    if analysis.get("should_alert"):
        headline += "\n✅ High match — cover letter in Notion."

    sent = await _safe_reply(update, headline)

    # Message 2 — details (optional)
    detail = match.get("summary_he") or match.get("summary_en") or ""
    if match.get("gaps"):
        detail += f"\n△ Gaps: {', '.join(match['gaps'])}"
    if detail.strip():
        sent = await _safe_reply(update, detail.strip()) or sent

    if not sent and notion_ok:
        await _safe_reply(
            update,
            f"Analysis saved to Notion (score {score}/100). Open Career Quest to view.",
        )


def _check_telegram_reachable() -> None:
    """Warn if Telegram is unreachable; retry instead of exiting immediately."""
    skip = os.getenv("SKIP_TELEGRAM_CHECK", "").lower() in ("1", "true", "yes")
    if skip:
        print("Skipping Telegram connectivity check (SKIP_TELEGRAM_CHECK).")
        return

    last_err: Exception | None = None
    for attempt in range(1, 4):
        try:
            httpx.get("https://api.telegram.org", timeout=20.0)
            return
        except httpx.HTTPError as exc:
            last_err = exc
            print(f"Telegram check {attempt}/3 failed — retrying…")
            time.sleep(2)

    print(
        "WARNING: Cannot reach api.telegram.org right now.\n"
        "  → Try: toggle VPN off/on, switch Wi‑Fi/hotspot, or wait 1 minute.\n"
        "  → To force start anyway: set SKIP_TELEGRAM_CHECK=true in .env\n"
        f"  → Last error: {last_err}"
    )


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    err = context.error
    print(f"Bot error: {type(err).__name__}: {err}")
    # Transient Telegram outages — library retries; don't alarm the user
    if isinstance(err, (NetworkError, TimedOut)):
        return
    if update and getattr(update, "message", None):
        await _safe_reply(
            update,
            f"Error: {type(err).__name__}. If a job was sent, check Notion.",
        )


def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN in .env")

    force_start = os.getenv("SKIP_TELEGRAM_CHECK", "").lower() in ("1", "true", "yes")
    if not force_start:
        _check_telegram_reachable()

    proxy = os.getenv("TELEGRAM_PROXY_URL") or None
    request = HTTPXRequest(
        connect_timeout=60.0,
        read_timeout=60.0,
        write_timeout=60.0,
        pool_timeout=60.0,
        proxy=proxy,
    )

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .request(request)
        .build()
    )
    app.add_error_handler(on_error)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_job_text))
    print("MatchFlow Telegram bot running — open @aseel_matchflow_bot and send /start")
    print("TIP: run only ONE bot instance (close other terminals running bot.py)")
    # bootstrap_retries=-1 → keep running through network blips (don't exit)
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
        bootstrap_retries=-1,
    )


if __name__ == "__main__":
    main()
