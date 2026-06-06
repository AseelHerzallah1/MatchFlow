# n8n Workflows

## `matchflow-main.json`

Full Quest #2 automatic flow:

```
▶ Manual (demo)  ──┐
Every 6 hours    ──┼──► ⚙️ Config ──► RSS ──► Brain ──► Score >= 80?
```

**Setup guide:** [docs/N8N_SETUP.md](../../docs/N8N_SETUP.md)

### Quick import

1. n8n → Import `matchflow-main.json`
2. Edit **⚙️ Config** → paste your `BRAIN_API_KEY`
3. **Test workflow** via **▶ Manual (demo)**
4. Toggle **Active** for schedule

### Demo tip

Add a **Limit** node (max 1 item) between RSS and Brain when testing — saves OpenAI credits.
