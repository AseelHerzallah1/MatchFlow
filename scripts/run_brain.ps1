# Run MatchFlow Brain API from repo root
# --reload-dir brain  → only restarts when brain/ changes, NOT telegram_bot/
$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn brain.app.main:app --host 127.0.0.1 --port 8001 --reload --reload-dir brain
