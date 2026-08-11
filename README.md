# MatchFlow

**My personal job-search copilot** — built to help me hunt entry-level SWE roles without drowning in irrelevant postings.

I paste or auto-collect jobs, MatchFlow scores each one against my real CV (plus GitHub), logs everything in **Notion**, and only pings me when the fit is **≥ 80** — with a cover letter ready to send. Along the way I practiced **workflow automation** (n8n), **API design** (FastAPI), and **structured AI** (OpenAI + Pydantic).

> Separate from **[AseelIndex](https://github.com/AseelHerzallah1)** (portfolio RAG chatbot). AseelIndex *talks* to recruiters; MatchFlow *acts* on opportunities.

**Brain API (live):** https://matchflow-tgvm.onrender.com · [health](https://matchflow-tgvm.onrender.com/health) · [docs](https://matchflow-tgvm.onrender.com/docs)

---

## How it works

| Phase | What | Implementation |
|-------|------|----------------|
| **01 Trigger** | Auto + manual intake | n8n RSS + Telegram bot |
| **02 Brain** | Extract entities + 1–100 score | FastAPI + OpenAI structured output (Render) |
| **03 Action** | CRM + smart alerts | Notion + Telegram when ≥ 80 |

---

## Quick start

### 1. Configure

```powershell
cd PLACE-IL-Quest
copy .env.example .env
# Edit .env — OPENAI_API_KEY, BRAIN_API_KEY, Notion, Telegram
# MATCHFLOW_BRAIN_URL=https://matchflow-tgvm.onrender.com
```

### 2. Telegram bot (manual trigger)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r telegram_bot/requirements.txt
python telegram_bot/bot.py
```

The bot calls the live Brain on Render (see `MATCHFLOW_BRAIN_URL` in `.env`).

### 3. n8n (automatic RSS)

1. `n8n start` → open the editor  
2. Import `n8n/workflows/matchflow-main.json`  
3. **⚙️ Config:** `brainUrl` = `https://matchflow-tgvm.onrender.com`, plus your `brainApiKey`  
4. **Publish** the workflow  

See [n8n setup](docs/N8N_SETUP.md).

---

## Project layout

```
MatchFlow/
├── brain/              # FastAPI Brain API (deployed on Render)
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
