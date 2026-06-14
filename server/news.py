"""World Cup headlines from a free RSS feed (default: Google News search).

The browser can't fetch RSS directly (CORS), so we pull + parse it here — on the
server (cached) and at static-build time. Failures are swallowed and return an
empty list, so the News view just shows an empty state rather than breaking.

Override the feed with the NEWS_FEED_URL env var.
"""

import os
import time
from xml.etree import ElementTree as ET

import requests

DEFAULT_FEED = (
    "https://news.google.com/rss/search"
    "?q=FIFA+World+Cup+2026+soccer&hl=en-US&gl=US&ceid=US:en"
)
FEED_URL = os.getenv("NEWS_FEED_URL", DEFAULT_FEED)
TTL_SECONDS = 1800  # 30 min

_cache = {"items": [], "fetched_at": 0.0}


def _parse(xml_text: str, limit: int) -> list:
    root = ET.fromstring(xml_text)
    items = []
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        pub = (it.findtext("pubDate") or "").strip()
        src_el = it.find("source")
        source = (src_el.text if src_el is not None else "").strip()
        # Google News titles read "Headline - Source"; drop the redundant suffix.
        if source and title.endswith(f" - {source}"):
            title = title[: -(len(source) + 3)].strip()
        if title and link:
            items.append({"title": title, "link": link, "source": source, "published": pub})
        if len(items) >= limit:
            break
    return items


def fetch_news(limit: int = 12, timeout: int = 10) -> list:
    """Fetch + parse the feed. Returns [] on any failure."""
    try:
        resp = requests.get(FEED_URL, timeout=timeout,
                            headers={"User-Agent": "tss-worldcup/1.0"})
        resp.raise_for_status()
        return _parse(resp.text, limit)
    except Exception:  # noqa: BLE001 - news is best-effort
        return []


def get_news(limit: int = 12) -> list:
    """Cached accessor for the server: refetch at most every TTL_SECONDS."""
    now = time.time()
    if not _cache["items"] or now - _cache["fetched_at"] > TTL_SECONDS:
        fresh = fetch_news(limit)
        if fresh:
            _cache["items"] = fresh
            _cache["fetched_at"] = now
    return _cache["items"]
