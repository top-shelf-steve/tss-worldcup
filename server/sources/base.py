"""Data-source contract + the normalized match shape the rest of the app speaks.

Everything downstream (standings, bracket, API, frontend) consumes the
normalized dicts produced here. A new source (e.g. a keyed live API) only has
to implement `DataSource.fetch_matches()` returning this same shape — no UI or
endpoint changes required. That is the whole point of the adapter layer.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

from ..teams import flag, is_real_team

# Maps openfootball `round` strings to a compact stage code used everywhere.
STAGE_BY_ROUND = {
    "Round of 32": "r32",
    "Round of 16": "r16",
    "Quarter-final": "qf",
    "Semi-final": "sf",
    "Match for third place": "third",
    "Final": "final",
}


def stage_for(round_name: str, group) -> str:
    if group:
        return "group"
    return STAGE_BY_ROUND.get(round_name, "ko")


def parse_kickoff(date_str: str, time_str: str):
    """'2026-06-11' + '13:00 UTC-6' -> ISO-8601 UTC instant (or None).

    The feed gives local kickoff with a UTC offset; we normalize to UTC so the
    browser can render each match in the viewer's own timezone.
    """
    try:
        clock, _, offset = (time_str or "").partition(" ")
        hh, mm = (int(p) for p in clock.split(":")[:2])
        sign = 1
        off_hours = 0
        off = offset.replace("UTC", "").strip()
        if off:
            sign = -1 if off[0] == "-" else 1
            off_hours = int(off[1:].split(":")[0])
        y, mo, d = (int(p) for p in date_str.split("-"))
        local = datetime(y, mo, d, hh, mm, tzinfo=timezone(timedelta(hours=sign * off_hours)))
        return local.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except (ValueError, AttributeError):
        return None


def normalize_match(raw: dict, index: int) -> dict:
    """Convert one feed match into the canonical dict (slots left unresolved)."""
    group = raw.get("group")
    ft = (raw.get("score") or {}).get("ft")
    ht = (raw.get("score") or {}).get("ht")
    team1, team2 = raw["team1"], raw["team2"]

    winner = None
    if ft:
        if ft[0] > ft[1]:
            winner = 1
        elif ft[1] > ft[0]:
            winner = 2
        # draws in knockout would be decided on penalties; feed lacks that, so
        # we leave winner=None and let the bracket show it as undecided.

    return {
        "id": index + 1,  # 1..104; equals feed `num` for knockout matches
        "round": raw.get("round"),
        "stage": stage_for(raw.get("round"), group),
        "group": group,
        "date": raw.get("date"),
        "time_local": raw.get("time"),
        "kickoff_utc": parse_kickoff(raw.get("date"), raw.get("time")),
        # *_slot keeps the raw label (real name or placeholder like '2A'/'W73');
        # team1/team2 may be overwritten by the bracket resolver.
        "team1_slot": team1,
        "team2_slot": team2,
        "team1": team1,
        "team2": team2,
        "flag1": flag(team1) if is_real_team(team1) else None,
        "flag2": flag(team2) if is_real_team(team2) else None,
        "resolved1": is_real_team(team1),
        "resolved2": is_real_team(team2),
        "score": {"ft": ft, "ht": ht} if ft else None,
        "status": "finished" if ft else "upcoming",
        "winner": winner,
        "goals1": raw.get("goals1") or [],
        "goals2": raw.get("goals2") or [],
        "ground": raw.get("ground"),
    }


class DataSource(ABC):
    """Implement this to add a new feed. `fetch_matches` returns raw feed dicts
    (openfootball shape); `normalize_match` above turns them canonical."""

    name = "base"

    @abstractmethod
    def fetch_matches(self) -> list:
        """Return a list of raw match dicts in openfootball's schema."""
        raise NotImplementedError

    def matches(self) -> list:
        return [normalize_match(m, i) for i, m in enumerate(self.fetch_matches())]
