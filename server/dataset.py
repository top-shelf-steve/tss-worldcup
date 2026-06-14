"""Assemble the normalized feed into one dataset, plus per-endpoint payloads.

`build()` runs the source through normalization, standings, and the bracket
resolver once; the payload helpers below slice that result for each API route.
Keeping all shaping here means the Flask layer is a thin pass-through and the
static exporter can reuse the exact same payloads.
"""

from datetime import datetime, timezone

from . import bracket as bracket_mod
from .standings import compute_standings
from .teams import (CONFEDERATIONS, FEATURED_TEAM, HOSTS, SLUG_TO_NAME, TEAMS,
                    confederation, flag, slugify)

TOURNAMENT = {
    "name": "World Cup 2026",
    "dates": "11 June – 19 July 2026",
    "hosts": "United States · Canada · Mexico",
}

# host pins for the Overview map (equirectangular: x=(lon+180)/360, y=(90-lat)/180)
HOST_PINS = [
    {"country": "USA", "x": 23.1, "y": 31.8, "color": "#c0473f"},
    {"country": "Canada", "x": 28.0, "y": 25.8, "color": "#3b6fb0"},
    {"country": "Mexico", "x": 22.5, "y": 39.2, "color": "#2e8b57"},
]


def build(source) -> dict:
    matches = source.matches()
    standings = compute_standings(matches)
    bracket = bracket_mod.annotate_and_build(matches, standings)  # resolves KO slots in-place
    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": source.name,
        "matches": matches,
        "standings": standings,
        "bracket": bracket,
    }


# --- helpers ---------------------------------------------------------------

def _light(m: dict) -> dict:
    """Trimmed match for lists (drops goals to keep payloads small)."""
    keys = ("id", "round", "stage", "group", "date", "time_local", "kickoff_utc",
            "team1", "team2", "flag1", "flag2", "resolved1", "resolved2",
            "score", "status", "winner", "ground")
    return {k: m[k] for k in keys}


def _by_kickoff(m):
    return m.get("kickoff_utc") or ""


def _team_standing(standings: dict, team: str):
    for group, rows in standings.items():
        for row in rows:
            if row["team"] == team:
                return {"group": group, **row}
    return None


# --- payloads --------------------------------------------------------------

def overview(ds: dict) -> dict:
    upcoming = sorted((m for m in ds["matches"] if m["status"] == "upcoming"),
                      key=_by_kickoff)
    next_matches = [_light(m) for m in upcoming[:8]]
    return {
        "tournament": TOURNAMENT,
        "host_pins": HOST_PINS,
        "next_matches": next_matches,
        "featured": team(ds, slugify(FEATURED_TEAM)),
    }


def matches(ds: dict) -> dict:
    return {"matches": [_light(m) for m in ds["matches"]]}


def match(ds: dict, match_id: int):
    for m in ds["matches"]:
        if m["id"] == match_id:
            detail = dict(m)
            if m.get("group"):
                detail["table"] = ds["standings"].get(m["group"], [])
            return detail
    return None


def groups(ds: dict) -> dict:
    out = []
    for group, rows in ds["standings"].items():
        fixtures = [_light(m) for m in ds["matches"] if m.get("group") == group]
        fixtures.sort(key=_by_kickoff)
        out.append({"group": group, "table": rows, "fixtures": fixtures})
    return {"groups": out}


def teams(ds: dict) -> dict:
    # group letter for each team, derived from the standings keys
    group_of = {row["team"]: g for g, rows in ds["standings"].items() for row in rows}
    items = []
    for name in sorted(TEAMS):
        items.append({
            "name": name, "slug": slugify(name), "flag": flag(name),
            "confederation": confederation(name), "group": group_of.get(name),
        })
    return {"teams": items, "confederations": CONFEDERATIONS}


def team(ds: dict, slug: str):
    name = SLUG_TO_NAME.get(slug)
    if not name:
        return None
    played, upcoming = [], []
    for m in ds["matches"]:
        if name in (m["team1"], m["team2"]):
            (played if m["status"] == "finished" else upcoming).append(_light(m))
    played.sort(key=_by_kickoff)
    upcoming.sort(key=_by_kickoff)
    return {
        "name": name, "slug": slug, "flag": flag(name),
        "confederation": confederation(name),
        "standing": _team_standing(ds["standings"], name),
        "results": played, "fixtures": upcoming,
        "is_host": name in HOSTS,
    }


def bracket(ds: dict) -> dict:
    return ds["bracket"]


def stats(ds: dict) -> dict:
    """Tournament stats derived purely from the goal data in the feed.

    Own goals are excluded from the scorer chart (the listed name is an opponent,
    not the team's own player); penalties count as goals and are tallied too.
    """
    scorers, team_goals = {}, {}
    total_goals = played = 0
    biggest = None

    for m in ds["matches"]:
        if not m.get("score"):
            continue
        played += 1
        a, b = m["score"]["ft"]
        total_goals += a + b

        for team, gf, fl in ((m["team1"], a, m["flag1"]), (m["team2"], b, m["flag2"])):
            tg = team_goals.setdefault(team, {"team": team, "flag": fl, "goals": 0})
            tg["goals"] += gf

        margin = abs(a - b)
        if margin and (biggest is None or margin > biggest["margin"]):
            biggest = {
                "match_id": m["id"], "team1": m["team1"], "team2": m["team2"],
                "flag1": m["flag1"], "flag2": m["flag2"],
                "score": m["score"]["ft"], "margin": margin,
            }

        for goals, team, fl in ((m["goals1"], m["team1"], m["flag1"]),
                                (m["goals2"], m["team2"], m["flag2"])):
            for g in goals:
                if g.get("owngoal"):
                    continue
                s = scorers.setdefault(g["name"], {
                    "name": g["name"], "team": team, "flag": fl, "goals": 0, "pens": 0,
                })
                s["goals"] += 1
                if g.get("penalty"):
                    s["pens"] += 1

    scorer_list = sorted(scorers.values(), key=lambda s: (-s["goals"], s["name"]))
    team_list = sorted(team_goals.values(), key=lambda t: (-t["goals"], t["team"]))
    return {
        "scorers": scorer_list[:20],
        "team_goals": [t for t in team_list if t["goals"] > 0][:10],
        "totals": {
            "matches_played": played,
            "goals": total_goals,
            "avg_goals": round(total_goals / played, 2) if played else 0,
            "biggest_win": biggest,
        },
    }
