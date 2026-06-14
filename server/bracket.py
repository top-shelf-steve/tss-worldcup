"""Resolve knockout slot labels and assemble the bracket tree.

Knockout matches reference placeholders rather than teams:
  1A / 2A      -> winner / runner-up of Group A   (from standings)
  W73 / L101   -> winner / loser of match 73 / 101 (from results, recursive)
  3A/B/C/D/F   -> one of eight best third-placed teams (allocation depends on
                  which thirds advance, so we keep it as a readable label)
Anything we can't yet resolve renders as a label so the bracket fills in live.
"""

from .standings import group_is_complete
from .teams import flag, is_real_team

# match numbers per knockout round (R32-based 48-team format)
ROUNDS = [
    ("r32", "Round of 32", range(73, 89)),
    ("r16", "Round of 16", range(89, 97)),
    ("qf", "Quarter-finals", range(97, 101)),
    ("sf", "Semi-finals", range(101, 103)),
    ("final", "Final", [104]),
]
THIRD_PLACE_ID = 103


def _slot(name=None, flag_code=None, label=None):
    return {
        "name": name,
        "flag": flag_code,
        "label": label or name,
        "resolved": name is not None,
    }


def _label_for(raw: str) -> str:
    if raw and raw[0] in "12" and len(raw) <= 2:
        kind = "Winner" if raw[0] == "1" else "Runner-up"
        return f"{kind} Group {raw[1]}"
    if raw and raw[0] == "W" and raw[1:].isdigit():
        return f"Winner of M{raw[1:]}"
    if raw and raw[0] == "L" and raw[1:].isdigit():
        return f"Loser of M{raw[1:]}"
    if raw and raw.startswith("3"):
        return "3rd place: " + raw[1:]
    return raw


def _winner_loser(match, by_id, standings, cache, want_winner):
    """Resolved name of the winner (or loser) of `match`, or None if undecided."""
    if not match or not match.get("score") or not match.get("winner"):
        return None
    win_idx = match["winner"]
    los_idx = 2 if win_idx == 1 else 1
    idx = win_idx if want_winner else los_idx
    return resolve(match[f"team{idx}_slot"], by_id, standings, cache)["name"]


def resolve(raw: str, by_id, standings, cache=None) -> dict:
    """Resolve a slot label to a concrete team slot dict (memoized)."""
    if cache is None:
        cache = {}
    if raw in cache:
        return cache[raw]
    cache[raw] = _slot(label=_label_for(raw))  # guard against cycles

    if is_real_team(raw):
        result = _slot(raw, flag(raw))
    elif raw and raw[0] in "12" and len(raw) <= 2:
        rows = standings.get(f"Group {raw[1]}")
        if rows and group_is_complete(rows):
            team = rows[int(raw[0]) - 1]["team"]
            result = _slot(team, flag(team))
        else:
            result = _slot(label=_label_for(raw))
    elif raw and raw[0] in "WL" and raw[1:].isdigit():
        team = _winner_loser(by_id.get(int(raw[1:])), by_id, standings, cache,
                             want_winner=(raw[0] == "W"))
        result = _slot(team, flag(team)) if team else _slot(label=_label_for(raw))
    else:
        result = _slot(label=_label_for(raw))

    cache[raw] = result
    return result


def annotate_and_build(matches: list, standings: dict) -> list:
    """Resolve knockout team slots in-place and return the bracket columns."""
    by_id = {m["id"]: m for m in matches}
    cache = {}

    for m in matches:
        if m["stage"] == "group":
            continue
        for i in (1, 2):
            slot = resolve(m[f"team{i}_slot"], by_id, standings, cache)
            m[f"team{i}"] = slot["name"] or slot["label"]
            m[f"flag{i}"] = slot["flag"]
            m[f"resolved{i}"] = slot["resolved"]

    def node(m):
        return {
            "id": m["id"], "round": m["round"], "stage": m["stage"],
            "team1": resolve(m["team1_slot"], by_id, standings, cache),
            "team2": resolve(m["team2_slot"], by_id, standings, cache),
            "score": m["score"], "winner": m["winner"],
            "kickoff_utc": m["kickoff_utc"], "ground": m["ground"],
            "date": m["date"], "time_local": m["time_local"],
        }

    columns = []
    for stage, title, ids in ROUNDS:
        nodes = [node(by_id[i]) for i in ids if i in by_id]
        columns.append({"stage": stage, "title": title, "matches": nodes})
    third = by_id.get(THIRD_PLACE_ID)
    return {"columns": columns, "third_place": node(third) if third else None}
