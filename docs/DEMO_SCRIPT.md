# 2-Minute Demo Script (for judges / video)

**Title:** MatchFlow — Your job search on autopilot, with judgment.

1. **Hook (15s)**  
   "I built MatchFlow for Place-IL Quest #2: it collects jobs, scores them against *my* CV, logs everything in Notion, and only interrupts me when the fit is ≥ 80—with a cover letter ready to send."

2. **Trigger — manual (30s)**  
   - Open Telegram → send `/start`, then paste a real job posting (or a link).  
   - Show bot reply: "Analyzing…" then summary card with score + gaps.

3. **Trigger — automatic (20s)**  
   - Open n8n → workflow **MatchFlow — RSS → Brain → Notion**.  
   - Point at sticky notes: Phase 01 / 02 / 03.  
   - Click **▶ Manual (demo)** → **Execute workflow**.  
   - Show **Executions** tab: RSS → Brain → score.  
   - Notion: new row with **Source: Rss**.

4. **Brain (25s)**  
   - Open `brain/app/prompts.py` briefly: structured extraction + honest scoring.  
   - Optional: Swagger `/docs` → run sample `POST /analyze`.

5. **CRM (20s)**  
   - Open Notion board: sorted by Match Score, Status = New, filter ≥ 80.

6. **Alert (20s)**  
   - Show Slack/Telegram message: score, company, 3-bullet fit summary, full cover letter.  
   - Emphasize: below 80 → logged silently, no notification spam.

7. **Close (10s)**  
   - "Separated from my portfolio bot AseelIndex—this is the *action* layer of my job search."  
   - Repo + n8n export + deadline 06.06.2026.

## Backup if live APIs fail

- Pre-record screen capture with one frozen Notion row and one alert screenshot in `docs/screenshots/`.
