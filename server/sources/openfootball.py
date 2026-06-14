"""Free, no-key source: openfootball/worldcup.json (public domain).

Hand-curated wiki data: full schedule, final scores, and goal scorers — but no
lineups, live clock, or advanced stats. Those gaps are why a keyed source can
later be slotted in beside this one.
"""

import requests

from .base import DataSource

RAW_URL = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"


class OpenFootballSource(DataSource):
    name = "openfootball"

    def __init__(self, url: str = RAW_URL, timeout: int = 15):
        self.url = url
        self.timeout = timeout

    def fetch_matches(self) -> list:
        resp = requests.get(self.url, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        return data.get("matches", [])
