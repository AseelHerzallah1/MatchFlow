# n8n Setup — Automatic RSS Trigger (Quest Phase 01)

MatchFlow already has **manual** intake via Telegram. This adds **automatic** intake via RSS + schedule — required for a complete Quest #2 submission.

---

## Prerequisites

Before importing the workflow:

1. **Brain running** (Terminal 1):
   ```powershell
   $env:PYTHONPATH = (Get-Location).Path
   python -m uvicorn brain.app.main:app --host 127.0.0.1 --port 8001 --reload --reload-dir brain
   ```
2. **Health check:** [http://127.0.0.1:8001/health](http://127.0.0.1:8001/health) → `ok`
3. Your `.env` has `OPENAI_API_KEY`, `NOTION_*`, `BRAIN_API_KEY`

> With **npm**, n8n and Brain both run on your PC — use `brainUrl` = `http://127.0.0.1:8001`.

### Terminals while testing

| Terminal | Command |
|----------|---------|
| **1** | Brain (`uvicorn` port 8001) |
| **2** | Telegram bot (optional) |
| **3** | `n8n start` (port 5678) |

---

## Step 1 — Install n8n (Windows)

> The old **n8n Desktop app** is deprecated. Use **npm** (easiest if you have Node.js) or **Docker**.

### Option A — npm (recommended for you)

You already have Node.js — use this:

**One-time install:**
```powershell
npm install -g n8n
```

**Start n8n (new terminal — Terminal 3):**
```powershell
n8n start
```

Or from the project folder:
```powershell
.\scripts\run_n8n.ps1
```

Open in browser: **http://localhost:5678**

First launch may ask you to create a local owner account (email + password) — that's only stored on your PC.

### Option B — Docker (if you install Docker Desktop later)

```powershell
docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
```

If using Docker, change **brainUrl** in the Config node to:
`http://host.docker.internal:8001` (so the container can reach Brain on your PC).

### Official docs

[https://docs.n8n.io/hosting/installation/npm/](https://docs.n8n.io/hosting/installation/npm/)

---

## Step 2 — Import workflow

1. n8n → **Workflows** → **⋮** menu → **Import from file**
2. Select: `n8n/workflows/matchflow-main.json`
3. Open the imported workflow **"MatchFlow — RSS → Brain → Notion"**

---

## Step 3 — Edit the Config node (one time)

Click the **⚙️ Config** node and set:

| Field | Value |
|-------|--------|
| `rssUrl` | WeWorkRemotely full-stack RSS (or another junior-friendly feed) |
| `brainUrl` | `https://matchflow-tgvm.onrender.com` (live Brain — not localhost) |
| `brainApiKey` | Your `BRAIN_API_KEY` from `.env` (same value as Telegram / Render) |

**Save** the workflow (Ctrl+S).

---

## Step 4 — Test manually (for demo video)

1. Make sure **Brain is running**
2. In n8n, open the workflow
3. Click **▶ Manual (demo)** node → **Test workflow** (or **Execute workflow**)
4. Watch execution:
   - ⚙️ Config → RSS Job Feed → MatchFlow Brain → Score >= 80?
5. Open **Notion → Career Quest** — new row(s) with **Source: Rss**
6. Open **Executions** tab in n8n — screenshot for submission

**Note:** RSS may return many jobs — each one calls OpenAI (costs $). For first test, you can temporarily change `rssUrl` to a smaller feed or limit items (see below).

---

## Step 5 — Activate automatic schedule

1. Toggle **Active** (top-right) to ON
2. Workflow runs every **6 hours** via **Every 6 hours** node
3. For submission demo, manual trigger is enough; schedule proves automation

---

## RSS feed options

| Feed | URL | Good for |
|------|-----|----------|
| **RemoteOK junior (default)** | `https://remoteok.com/remote-junior-jobs.rss` | Junior/entry dev — scores 75–85 vs your CV |
| WeWorkRemotely full-stack | `https://weworkremotely.com/categories/remote-full-stack-programming-jobs.rss` | Backup — still many senior roles |
| WeWorkRemotely (all) | `https://weworkremotely.com/remote-jobs.rss` | ❌ Avoid — mostly senior |
| LinkedIn Israel (custom) | via [rssjobs.app](https://rssjobs.app) + `il.linkedin.com/jobs/junior-software-engineer-jobs` | Israeli junior SWE |
| Referally WhatsApp | Telegram paste (manual) | Best for Israel + referrals |

Update `rssUrl` in **⚙️ Config** node. Re-import `n8n/workflows/matchflow-main.json` if you already have an older workflow open.

Also set in `.env` (optional, for `scripts/test_rss_pipeline.ps1`):
```env
RSS_FEED_URL=https://remoteok.com/remote-junior-jobs.rss
```

---

## How many jobs per run?

The workflow includes **Top N jobs** (Limit node), controlled by **`jobsPerRun`** in **⚙️ Config**:

| Value | Use case |
|-------|----------|
| **1** | Quick test / demo only |
| **10** | Default — good balance (recommended) |
| **20** | Aggressive hunt (more OpenAI cost) |

**Do not use 1 in production** — you’ll only ever see one random job (like that 65 score).

### Pick the best matches

1. Each job gets a **Match Score** in Notion  
2. In Notion → **Sort** by **Match Score** descending → best jobs at top  
3. **Alerts + cover letters** only fire automatically when score **≥ 80**  
4. Optional: add `?notion_min_score=70` to the Brain HTTP URL so scores below 70 skip Notion (less clutter)

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ECONNREFUSED 127.0.0.1:8001` | Start Brain (`uvicorn`) |
| `401 Unauthorized` | Wrong `brainApiKey` in Config node |
| `503 OPENAI_API_KEY` | Check `.env`, restart Brain |
| Notion empty | Same fix as Telegram — Brain must load `.env` |
| Too many API calls | Add **Limit** node (1 item) for tests |

---

## Test without n8n (optional)

```powershell
.\scripts\test_rss_pipeline.ps1
```

Runs one RSS item through Brain from PowerShell.

---

## What to show in a demo

1. Telegram manual trigger — paste a job, get score + Notion row
2. n8n canvas with 3 phases (sticky notes)
3. Manual execution → **Executions** log
4. Notion row with **Source: Rss**
5. High-match row with cover letter (score ≥ 80)
