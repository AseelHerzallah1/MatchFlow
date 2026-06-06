# Referally + MatchFlow — Entry-Level Job Sources

[Referally](https://tr.ee/VhBuk3A8HR) runs WhatsApp communities by level:

| Group | For you? |
|-------|----------|
| **Entry Level (0+)** | ✅ Best fit |
| **Student** | ✅ Good fit |
| **Junior (1-2)** | ✅ Good fit |
| Mid (3-4) | ❌ Too senior |
| Senior (5+) | ❌ Why RSS scores were ~65 |

Join via [Referally Linktree](https://tr.ee/VhBuk3A8HR) → **Entry Level (0+)** WhatsApp.

---

## Can we auto-read the WhatsApp group?

**Not directly.** WhatsApp does not offer a public API to scrape group messages. Automating group reads also violates Meta’s terms.

### ✅ What works today (recommended)

**Referally WhatsApp → copy → MatchFlow Telegram bot**

1. See a junior job in Referally **Entry Level (0+)** or **SW Entry 0+** (PRO)
2. Copy the full posting text
3. Paste into **@aseel_matchflow_bot**
4. Get score + Notion row (Helfy 85/100 is this path)

This is a valid **manual trigger** for Quest #2 and matches how Israeli job hunters actually use Referally.

---

## Automatic RSS (n8n) — junior dev feeds

WeWorkRemotely’s main feed is **mostly senior** (Design Manager, Dynamics Consultant, etc.) — scores ~65 and wastes OpenAI calls.

### ✅ Default feed (tested with your CV)

**RemoteOK — junior jobs** (now the MatchFlow default):

```
https://remoteok.com/remote-junior-jobs.rss
```

| Job from feed | Your score |
|---------------|------------|
| Junior Front End Developer | **79–85** |
| Software Engineer New Grad | **75** |
| AI Engineer I | **75** |

Re-import `n8n/workflows/matchflow-main.json` or set this URL in **⚙️ Config** → `rssUrl`.

### A) Dev + junior filter (included in workflow)

Between **RSS Job Feed** and **Top N jobs**, the **Junior/Entry filter** Code node keeps only **junior + software/dev** roles and drops senior + non-tech junior (HR, illustrator, etc.).

**Mode:** `Run Once for Each Item`

If output is **0 items**, run again later or paste from **Referally → Telegram**.

### B) Other feeds we tested

| Feed | Verdict |
|------|---------|
| `remoteok.com/remote-junior-jobs.rss` | ✅ **Best** — real junior dev roles, high scores |
| `weworkremotely.com/remote-jobs.rss` | ❌ Mostly senior |
| `weworkremotely.com/.../full-stack-programming-jobs.rss` | ⚠️ Better than main, still ~50% senior |
| `jobicy.com/?feed=job_feed` | ❌ Senior-heavy |
| `jobicy.com/jobs-feed?job_categories=junior` | ❌ 404 |
| Israeli boards (Drushim, AllJobs, LinkedIn) | ❌ No free RSS — use Referally or [rssjobs.app](https://rssjobs.app) + LinkedIn search URL |

### C) Israeli junior jobs (no RSS)

**Referally Entry Level (0+)** and **Student** WhatsApp groups remain the best source for Israel. Paste into Telegram — that path already scored **Helfy 85/100**.

Optional: create a custom RSS at [rssjobs.app](https://rssjobs.app) from  
`https://il.linkedin.com/jobs/junior-software-engineer-jobs` and paste that RSS URL into **⚙️ Config**.

---

## Your two-channel strategy

| Source | Channel | Best for |
|--------|---------|----------|
| **Referally 0+** | Telegram (paste) | Israeli junior + referral jobs |
| **RSS + filter** | n8n every 6h | Extra junior remote roles |

**Notion:** Sort by **Match Score** → apply to the best fits first.

---

## Demo story for judges

> "Referally’s WhatsApp groups don’t have an API — so MatchFlow uses Telegram for the jobs I actually care about (0+ / junior). RSS runs in parallel with a junior keyword filter so automation doesn’t waste scores on senior SWE posts."
