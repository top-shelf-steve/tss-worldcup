"""One-off: render a dotted equirectangular world map SVG from Natural Earth.

Samples a lon/lat grid, keeps the points that fall on land, and emits small
circles. Output is vendored as web/assets/world-dots.svg so neither the server
nor the static build needs any geo dependency at runtime.

Usage: python scripts/gen_world_dots.py /tmp/world.geojson
"""

import json
import sys
from pathlib import Path

STEP = 1.5            # degrees between dots
LAT_MIN, LAT_MAX = -56, 78   # skip Antarctica / empty poles
DOT_R = 0.45          # circle radius in viewBox units (viewBox is 360x180)
OUT = Path(__file__).resolve().parent.parent / "web" / "assets" / "world-dots.svg"


def rings(geom):
    if geom["type"] == "Polygon":
        yield geom["coordinates"][0]
    elif geom["type"] == "MultiPolygon":
        for poly in geom["coordinates"]:
            yield poly[0]


def point_in_ring(lon, lat, ring):
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > lat) != (yj > lat):
            x_cross = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < x_cross:
                inside = not inside
        j = i
    return inside


def main(src):
    data = json.loads(Path(src).read_text())
    polys = []  # (minlon, minlat, maxlon, maxlat, ring)
    for feat in data["features"]:
        for ring in rings(feat["geometry"]):
            xs = [p[0] for p in ring]
            ys = [p[1] for p in ring]
            polys.append((min(xs), min(ys), max(xs), max(ys), ring))

    dots = []
    lat = LAT_MAX
    while lat >= LAT_MIN:
        lon = -180.0
        while lon < 180.0:
            for minlon, minlat, maxlon, maxlat, ring in polys:
                if minlon <= lon <= maxlon and minlat <= lat <= maxlat and point_in_ring(lon, lat, ring):
                    dots.append((lon + 180.0, 90.0 - lat))
                    break
            lon += STEP
        lat -= STEP

    circles = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{DOT_R}"/>' for x, y in dots
    )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 180" '
        f'fill="currentColor" preserveAspectRatio="xMidYMid meet">{circles}</svg>'
    )
    OUT.write_text(svg)
    print(f"{len(dots)} dots -> {OUT} ({len(svg)} bytes)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/world.geojson")
