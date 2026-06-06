# MatchFlow — Place-IL Quest #2

**Smart automated job search** for the [Place-IL](https://www.place-il.org) competition (deadline **06.06.2026**).

MatchFlow collects jobs (RSS + Telegram), analyzes them with AI against your CV, logs everything in **Notion**, and sends **instant alerts with a cover letter** when the match score is **≥ 80**.

---

## Quest coverage

| Phase | Requirement | Implementation |
|-------|-------------|----------------|
| **01 Trigger** | Auto + manual intake | n8n RSS workflow + Telegram bot |
| **02 Brain** | Extract entities + 1–100 score | FastAPI + OpenAI structured output |
| **03 Action** | CRM + smart alerts | Notion API + Slack/Telegram when ≥ 80 |

---

## Quick start

### 1. Configure

```powershell
cd PLACE-IL-Quest
copy .env.example .env
# Edit .env — at minimum OPENAI_API_KEY, BRAIN_API_KEY
# Paste your real CV into cv/candidate_cv.md
```

### 2. Install & run Brain

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r brain/requirements.txt
$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn brain.app.main:app --port 8001 --reload
```

Open http://localhost:8001/docs — try `POST /api/v1/analyze` with header `X-API-Key`.

### 3. Telegram bot (manual trigger)

```powershell
pip install -r telegram_bot/requirements.txt
python telegram_bot/bot.py
```

### 4. n8n (automatic trigger)

Import `n8n/workflows/matchflow-main.json` — see [n8n/workflows/README.md](n8n/workflows/README.md).

---

## Project layout

```
PLACE-IL-Quest/
├── brain/              # FastAPI "Brain" API
├── telegram_bot/       # Manual job intake
├── cv/                 # Your CV (markdown)
├── n8n/workflows/      # Visual automation for judges
├── docs/               # Architecture, demo script, checklist
└── scripts/            # run_brain.ps1
```

---

## Docs

- [Architecture & Notion schema](docs/ARCHITECTURE.md)
- [2-minute demo script](docs/DEMO_SCRIPT.md)
- [Submission checklist](docs/SUBMISSION_CHECKLIST.md)

---

## Winning tips

1. **Record a crisp demo** following `docs/DEMO_SCRIPT.md`.
2. **Use your real CV** — scores and cover letters become believable.
3. **Show the n8n canvas** — judges expect Make/n8n/Zapier fluency.
4. **Bilingual UX** — Hebrew + English in Telegram and summaries.
5. **Honest scoring** — mention gaps; it reads as engineering, not marketing.

---

*Built by Aseel Herzallah for Place-IL × Eretz Ir — Quest #2.*
