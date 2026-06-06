# MatchFlow

**My personal job-search copilot** — built to help me hunt entry-level SWE roles without drowning in irrelevant postings.

I paste or auto-collect jobs, MatchFlow scores each one against my real CV (plus GitHub), logs everything in **Notion**, and only pings me when the fit is **≥ 80** — with a cover letter ready to send. Along the way I practiced **workflow automation** (n8n), **API design** (FastAPI), and **structured AI** (OpenAI + Pydantic).

> Separate from **[AseelIndex](https://github.com/AseelHerzallah1)** (portfolio RAG chatbot). AseelIndex *talks* to recruiters; MatchFlow *acts* on opportunities.

---

## How it works

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

Import `n8n/workflows/matchflow-main.json` — see [n8n/workflows/README.md](n8n/workflows/README.md) and [n8n setup](docs/N8N_SETUP.md).

---

## Project layout

```
PLACE-IL-Quest/
├── brain/              # FastAPI "Brain" API
├── telegram_bot/       # Manual job intake
├── cv/                 # Your CV (markdown)
├── n8n/workflows/      # Visual automation
├── docs/               # Architecture & setup
└── scripts/            # run_brain.ps1, test helpers
```

---

## Docs

- [Architecture & Notion schema](docs/ARCHITECTURE.md)
- [n8n setup](docs/N8N_SETUP.md)

---

*Built by Aseel Herzallah — BGU CS, junior SWE.*
