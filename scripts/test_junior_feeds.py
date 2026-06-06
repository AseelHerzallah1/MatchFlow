"""Probe RSS feeds for junior/entry-level developer job density."""
import re
import xml.etree.ElementTree as ET

import httpx

DEV_KW = re.compile(
    r"software|developer|engineer|full.stack|backend|frontend|devops|"
    r"python|javascript|react|node|java|programmer|swe|coding",
    re.I,
)
JUNIOR_KW = re.compile(
    r"junior|entry|intern|graduate|student|new grad|0-2|1-2|associate|college grad",
    re.I,
)
SENIOR_KW = re.compile(r"senior|principal|staff|lead |manager|director|sr\.", re.I)

FEEDS = [
    ("RemoteOK junior", "https://remoteok.com/remote-junior-jobs.rss"),
    ("RemoteOK dev", "https://remoteok.com/remote-dev-jobs.rss"),
    ("RemoteOK software", "https://remoteok.com/remote-software-jobs.rss"),
    ("Jobicy all", "https://jobicy.com/?feed=job_feed"),
    ("WWR full-stack", "https://weworkremotely.com/categories/remote-full-stack-programming-jobs.rss"),
    ("WWR programming", "https://weworkremotely.com/categories/remote-programming-jobs.rss"),
]


def parse_rss(url: str) -> tuple[int, list[tuple[str, str, str]]]:
    r = httpx.get(
        url, timeout=25, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0 MatchFlow/1.0"}
    )
    root = ET.fromstring(r.content)
    items: list[tuple[str, str, str]] = []
    for item in root.findall(".//item"):
        title = item.findtext("title", "") or ""
        link = item.findtext("link", "") or ""
        desc = (item.findtext("description", "") or "")[:400]
        items.append((title, link, desc))
    return r.status_code, items


def main() -> None:
    for name, url in FEEDS:
        try:
            code, items = parse_rss(url)
            dev = [(t, l, d) for t, l, d in items if DEV_KW.search(t + " " + d)]
            jun_dev = [t for t, _, d in dev if JUNIOR_KW.search(t + " " + d)]
            sen_dev = [t for t, _, d in dev if SENIOR_KW.search(t + " " + d)]
            print(f"=== {name} ===")
            print(
                f"HTTP {code} | total={len(items)} dev={len(dev)} "
                f"junior_dev={len(jun_dev)} senior_dev={len(sen_dev)}"
            )
            for t, _, d in dev[:10]:
                flags = ""
                if JUNIOR_KW.search(t + " " + d):
                    flags += "J"
                if SENIOR_KW.search(t + " " + d):
                    flags += "S"
                print(f"  [{flags or '-'}] {t[:100]}")
            print()
        except Exception as exc:
            print(f"=== {name} === FAIL: {exc}\n")


if __name__ == "__main__":
    main()
