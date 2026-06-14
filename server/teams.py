"""Static metadata for the 48 finalists: flag (ISO code) + confederation.

The openfootball feed gives only team names, so this map supplies the flag
codes (flag-icons / ISO 3166-1 alpha-2, plus gb-eng / gb-sct for home nations)
and confederation used by the Teams filter. Keys must match the feed's names
exactly.
"""

import re
import unicodedata

# name -> (flag code, confederation)
TEAMS = {
    "Algeria": ("dz", "CAF"),
    "Argentina": ("ar", "CONMEBOL"),
    "Australia": ("au", "AFC"),
    "Austria": ("at", "UEFA"),
    "Belgium": ("be", "UEFA"),
    "Bosnia & Herzegovina": ("ba", "UEFA"),
    "Brazil": ("br", "CONMEBOL"),
    "Canada": ("ca", "CONCACAF"),
    "Cape Verde": ("cv", "CAF"),
    "Colombia": ("co", "CONMEBOL"),
    "Croatia": ("hr", "UEFA"),
    "Curaçao": ("cw", "CONCACAF"),
    "Czech Republic": ("cz", "UEFA"),
    "DR Congo": ("cd", "CAF"),
    "Ecuador": ("ec", "CONMEBOL"),
    "Egypt": ("eg", "CAF"),
    "England": ("gb-eng", "UEFA"),
    "France": ("fr", "UEFA"),
    "Germany": ("de", "UEFA"),
    "Ghana": ("gh", "CAF"),
    "Haiti": ("ht", "CONCACAF"),
    "Iran": ("ir", "AFC"),
    "Iraq": ("iq", "AFC"),
    "Ivory Coast": ("ci", "CAF"),
    "Japan": ("jp", "AFC"),
    "Jordan": ("jo", "AFC"),
    "Mexico": ("mx", "CONCACAF"),
    "Morocco": ("ma", "CAF"),
    "Netherlands": ("nl", "UEFA"),
    "New Zealand": ("nz", "OFC"),
    "Norway": ("no", "UEFA"),
    "Panama": ("pa", "CONCACAF"),
    "Paraguay": ("py", "CONMEBOL"),
    "Portugal": ("pt", "UEFA"),
    "Qatar": ("qa", "AFC"),
    "Saudi Arabia": ("sa", "AFC"),
    "Scotland": ("gb-sct", "UEFA"),
    "Senegal": ("sn", "CAF"),
    "South Africa": ("za", "CAF"),
    "South Korea": ("kr", "AFC"),
    "Spain": ("es", "UEFA"),
    "Sweden": ("se", "UEFA"),
    "Switzerland": ("ch", "UEFA"),
    "Tunisia": ("tn", "CAF"),
    "Turkey": ("tr", "UEFA"),
    "USA": ("us", "CONCACAF"),
    "Uruguay": ("uy", "CONMEBOL"),
    "Uzbekistan": ("uz", "AFC"),
}

CONFEDERATIONS = ["AFC", "CAF", "CONCACAF", "CONMEBOL", "UEFA", "OFC"]

# Host nations get the accent pins on the Overview map.
HOSTS = {"USA": "us", "Canada": "ca", "Mexico": "mx"}

# The team the whole "spotlight" is built around.
FEATURED_TEAM = "USA"


def slugify(name: str) -> str:
    """'Bosnia & Herzegovina' -> 'bosnia-herzegovina', 'Curaçao' -> 'curacao'."""
    norm = unicodedata.normalize("NFKD", name)
    ascii_name = norm.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")


# slug -> canonical name
SLUG_TO_NAME = {slugify(name): name for name in TEAMS}


def flag(name: str):
    info = TEAMS.get(name)
    return info[0] if info else None


def confederation(name: str):
    info = TEAMS.get(name)
    return info[1] if info else None


def is_real_team(name: str) -> bool:
    """True for an actual nation, False for a knockout slot label like '1A'/'W73'."""
    return name in TEAMS
