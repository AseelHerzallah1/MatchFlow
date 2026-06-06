# Test RSS → Brain pipeline without n8n (1 job)
Set-Location $PSScriptRoot\..
$env:PYTHONPATH = (Get-Location).Path

.\.venv\Scripts\python -c @"
import os, httpx
from dotenv import load_dotenv
load_dotenv('.env')

feed = os.getenv('RSS_FEED_URL', 'https://remoteok.com/remote-junior-jobs.rss')
brain = os.getenv('MATCHFLOW_BRAIN_URL', 'http://127.0.0.1:8001').rstrip('/')
key = os.getenv('BRAIN_API_KEY', '')

import xml.etree.ElementTree as ET
r = httpx.get(feed, timeout=30, follow_redirects=True, headers={'User-Agent': 'MatchFlow/1.0'})
r.raise_for_status()
root = ET.fromstring(r.text)
ns = {'a': 'http://www.w3.org/2005/Atom', 'r': 'http://purl.org/rss/1.0/'}
item = root.find('.//item') or root.find('.//a:entry', ns)
if item is None:
    raise SystemExit('No RSS items found')

def txt(el, tag):
    e = el.find(tag)
    return (e.text or '').strip() if e is not None else ''

title = txt(item, 'title')
desc = txt(item, 'description') or txt(item, 'summary')
link_el = item.find('link')
link = link_el.text if link_el is not None and link_el.text else (link_el.get('href') if link_el is not None else '')
job_text = f'{title}\n\n{desc}'[:8000]

resp = httpx.post(
    f'{brain}/api/v1/pipeline',
    headers={'X-API-Key': key},
    json={'job_text': job_text, 'job_url': link, 'source': 'rss'},
    params={'persist_notion': True, 'send_alerts': False},
    timeout=180,
)
print('HTTP', resp.status_code)
d = resp.json()
a = d.get('analysis', {})
print('Title:', a.get('entities', {}).get('title'))
print('Score:', a.get('match', {}).get('score'))
print('Notion:', 'OK' if d.get('notion') else d.get('notion_error', 'skipped'))
"@
