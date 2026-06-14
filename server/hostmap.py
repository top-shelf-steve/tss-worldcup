"""Host-nation map projection + the 16 host cities.

Shared by the dot-map generator (scripts/gen_na_dots.py) and the Overview
payload so the dotted map and the plotted city pins use the exact same
projection. Simple equirectangular with the longitude scaled by cos(mid-lat)
so North America doesn't look horizontally stretched. Accuracy is "good
enough to locate a city," not survey-grade.
"""

from math import cos, radians

# Bounding box: contiguous US + southern Canada + all of Mexico.
LON_MIN, LON_MAX = -140.0, -52.0
LAT_MIN, LAT_MAX = 12.0, 60.0
KX = cos(radians((LAT_MIN + LAT_MAX) / 2))  # longitude compression

WIDTH = (LON_MAX - LON_MIN) * KX
HEIGHT = LAT_MAX - LAT_MIN
ASPECT = WIDTH / HEIGHT

COUNTRY_COLOR = {"USA": "#c0473f", "Canada": "#3b6fb0", "Mexico": "#2e8b57"}

# venue string (matches the feed's `ground`) -> (lat, lon, host nation)
CITY_COORDS = {
    "Atlanta": (33.76, -84.40, "USA"),
    "Boston (Foxborough)": (42.09, -71.26, "USA"),
    "Dallas (Arlington)": (32.75, -97.09, "USA"),
    "Guadalajara (Zapopan)": (20.68, -103.46, "Mexico"),
    "Houston": (29.69, -95.41, "USA"),
    "Kansas City": (39.05, -94.48, "USA"),
    "Los Angeles (Inglewood)": (33.95, -118.34, "USA"),
    "Mexico City": (19.30, -99.15, "Mexico"),
    "Miami (Miami Gardens)": (25.96, -80.24, "USA"),
    "Monterrey (Guadalupe)": (25.67, -100.24, "Mexico"),
    "New York/New Jersey (East Rutherford)": (40.81, -74.07, "USA"),
    "Philadelphia": (39.90, -75.17, "USA"),
    "San Francisco Bay Area (Santa Clara)": (37.40, -121.97, "USA"),
    "Seattle": (47.60, -122.33, "USA"),
    "Toronto": (43.63, -79.42, "Canada"),
    "Vancouver": (49.28, -123.11, "Canada"),
}


def project_pct(lon: float, lat: float):
    """lon/lat -> (x%, y%) within the map's viewBox."""
    x = (lon - LON_MIN) * KX
    y = LAT_MAX - lat
    return round(x / WIDTH * 100, 2), round(y / HEIGHT * 100, 2)


def short_name(city: str) -> str:
    """'Dallas (Arlington)' -> 'Dallas'; trims the parenthetical venue area."""
    return city.split(" (")[0]


def host_cities(highlight: set | None = None) -> list:
    highlight = highlight or set()
    out = []
    for city, (lat, lon, country) in CITY_COORDS.items():
        x, y = project_pct(lon, lat)
        out.append({
            "city": city, "label": short_name(city), "country": country,
            "color": COUNTRY_COLOR[country], "x": x, "y": y,
            "highlight": city in highlight,
        })
    return out
