# MatchFlow

**My personal job-search copilot** — built to help me hunt entry-level SWE roles without drowning in irrelevant postings.

I paste or auto-collect jobs, MatchFlow scores each one against my real CV (plus GitHub), logs everything in **Notion**, and only pings me when the fit is **≥ 80** — with a cover letter ready to send. Along the way I practiced **workflow automation** (n8n), **API design** (FastAPI), and **structured AI** (OpenAI + Pydantic).

---

## Live deployment

| Service | URL |
|---------|-----|
| **Brain API (Render)** | https://matchflow-tgvm.onrender.com |
| **Health** | https://matchflow-tgvm.onrender.com/health |
| **API docs** | https://matchflow-tgvm.onrender.com/docs |

n8n and Telegram should point at the Render URL (`MATCHFLOW_BRAIN_URL` / Config `brainUrl`), not localhost — so the pipeline runs even when your laptop is off (Brain sleeps on free-tier idle; first request may take ~30s).

---

## How it works

| Phase | What | Implementation |
|-------|------|----------------|
| **01 Trigger** | Auto + manual intake | n8n RSS + Telegram bot |
| **02 Brain** | Extract entities + 1–100 score | FastAPI + OpenAI structured output (hosted on Render) |
| **03 Action** | CRM + smart alerts | Notion + Telegram when ≥ 80 |

---

## Quick start

### 1. Configure

```powershell
cd PLACE-IL-Quest
copy .env.example .env
# Edit .env — OPENAI_API_KEY, BRAIN_API_KEY, Notion, Telegram, etc.
# MATCHFLOW_BRAIN_URL=https://matchflow-tgvm.onrender.com
# Paste / update your CV in cv/candidate_cv.md
```

### 2. Use the live Brain (recommended)

No need to run uvicorn locally if Render is up:

- Health: https://matchflow-tgvm.onrender.com/health  
- Swagger: https://matchflow-tgvm.onrender.com/docs — `POST /api/v1/analyze` with header `X-API-Key`

### 3. Telegram bot (manual trigger)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r telegram_bot/requirements.txt
python telegram_bot/bot.py
```

Set `MATCHFLOW_BRAIN_URL=https://matchflow-tgvm.onrender.com` in `.env` so the bot calls Render.

### 4. n8n (automatic RSS)

1. `n8n start` → http://localhost:5678  
2. Import `n8n/workflows/matchflow-main.json`  
3. **⚙️ Config:**  
   - `brainUrl` = `https://matchflow-tgvm.onrender.com`  
   - `brainApiKey` = your `BRAIN_API_KEY`  
   - `rssUrl` = WeWorkRemotely full-stack feed (or your preferred junior-friendly RSS)  
4. **Publish** the workflow  

See [n8n setup](docs/N8N_SETUP.md).

### Optional — run Brain locally

```powershell
pip install -r brain/requirements.txt
$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn brain.app.main:app --port 8001 --reload
```

Then temporarily set `MATCHFLOW_BRAIN_URL=http://127.0.0.1:8001`.

---

## Project layout

```
MatchFlow/
├── brain/              # FastAPI Brain API (also deployed on Render)
├── telegram_bot/       # Manual job intake
├── cv/                 # CV + GitHub enrichment
├── n8n/workflows/      # Automation export
├── docs/               # Architecture & setup
└── scripts/            # Helpers
```

---

## Docs

- [Architecture & Notion schema](docs/ARCHITECTURE.md)
- [n8n setup](docs/N8N_SETUP.md)

---

*Built by Aseel Herzallah — BGU CS, junior SWE.*
