# Submission Checklist — Deadline 06.06.2026

## Required by quest

- [ ] **Phase 1 — Trigger**: at least one automatic (RSS) + one manual (Telegram or form)
- [ ] **Phase 2 — Brain**: LLM extracts company, title, tech, years; returns score 1–100 + explanation vs CV
- [ ] **Phase 3 — Action**: Notion/Airtable CRM with status; alert if score > 80 with cover letter

## Deliverables to prepare

- [ ] GitHub repo link (this project, *not* AseelIndex)
- [ ] Exported n8n workflow JSON (`n8n/workflows/matchflow-main.json`)
- [ ] n8n manual test run (see `docs/N8N_SETUP.md`)
- [ ] Screenshot: n8n Executions + Notion row Source=Rss
- [ ] Short demo video or Loom (follow `DEMO_SCRIPT.md`)
- [ ] README with setup steps under 15 minutes
- [ ] Screenshots: n8n canvas, Notion board, one alert

## Your setup tasks (one-time)

1. Copy `.env.example` → `.env` and fill keys
2. Paste your CV into `cv/candidate_cv.md`
3. Create Notion database (see `ARCHITECTURE.md`) and share with integration
4. Create Telegram bot via [@BotFather](https://t.me/BotFather)
5. Import n8n workflow and set credentials
6. Run: `pip install -r brain/requirements.txt` → `uvicorn brain.app.main:app --port 8001`

## Competition polish

- [ ] Hebrew + English in Telegram welcome and alerts
- [ ] Custom project name + logo in README (optional)
- [ ] Mention Place-IL + Eretz Ir in README footer
