# Refresh cv/github_context.md from your public GitHub repos
Set-Location $PSScriptRoot\..
$env:PYTHONPATH = (Get-Location).Path
.\.venv\Scripts\python -c "
from brain.app.config import settings
from brain.app.services.github_profile import sync_github_context
u = settings.github_username
if not u:
    raise SystemExit('Set GITHUB_USERNAME in .env first')
text = sync_github_context(u, force=True)
print(f'Synced {len(text)} chars for @{u}')
"
