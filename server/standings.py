"""Compute group tables from finished matches.

The feed has no standings, so we derive them. Tiebreakers use the simplified
FIFA order that needs no head-to-head replay: points, goal difference, goals
for. (Official rules add head-to-head and fair-play; good enough for a tracker.)
"""

from collections import OrderedDict

from .teams import flag


def _blank_row(team: str) -> dict:
    return {
        "team": team,
        "flag": flag(team),
        "p": 0, "w": 0, "d": 0, "l": 0,
        "gf": 0, "ga": 0, "gd": 0, "pts": 0,
    }


def compute_standings(matches: list) -> "OrderedDict[str, list]":
    """Return {group_name: [row, ...]} ordered A..L, each list ranked."""
    groups = {}
    for m in matches:
        if not m.get("group"):
            continue
        groups.setdefault(m["group"], {})
        for team in (m["team1"], m["team2"]):
            groups[m["group"]].setdefault(team, _blank_row(team))

    for m in matches:
        g = m.get("group")
        if not g or not m.get("score"):
            continue
        a, b = m["score"]["ft"]
        r1, r2 = groups[g][m["team1"]], groups[g][m["team2"]]
        r1["gf"] += a; r1["ga"] += b
        r2["gf"] += b; r2["ga"] += a
        for r in (r1, r2):
            r["p"] += 1
        if a > b:
            r1["w"] += 1; r2["l"] += 1; r1["pts"] += 3
        elif b > a:
            r2["w"] += 1; r1["l"] += 1; r2["pts"] += 3
        else:
            r1["d"] += 1; r2["d"] += 1; r1["pts"] += 1; r2["pts"] += 1

    out = OrderedDict()
    for g in sorted(groups):
        rows = list(groups[g].values())
        for r in rows:
            r["gd"] = r["gf"] - r["ga"]
        rows.sort(key=lambda r: (r["pts"], r["gd"], r["gf"], r["team"]), reverse=True)
        for i, r in enumerate(rows):
            r["rank"] = i + 1
        out[g] = rows
    return out


def group_is_complete(rows: list) -> bool:
    """A 4-team group is done once every side has played its 3 matches."""
    return bool(rows) and all(r["p"] >= 3 for r in rows)
