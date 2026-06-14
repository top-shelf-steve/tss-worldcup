"""One-off: render a dotted map of the three host nations (US/Canada/Mexico).

Samples a grid inside the host-map bounding box, keeps points that fall on
US/Canada/Mexico land, and emits dots using server.hostmap's projection so the
plotted city pins line up. Output is vendored as web/assets/na-dots.svg.

Usage: python scripts/gen_na_dots.py /tmp/world.geojson
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from server import hostmap as H  # noqa: E402

STEP = 0.55           # degrees between samples
DOT_R = 0.22          # circle radius in viewBox units
HOST_ISO = {"USA", "CAN", "MEX"}
OUT = ROOT / "web" / "assets" / "na-dots.svg"


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
            if lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
                inside = not inside
        j = i
    return inside


def main(src):
    data = json.loads(Path(src).read_text())
    polys = []
    for feat in data["features"]:
        if feat["properties"].get("ISO_A3") not in HOST_ISO:
            continue
        for ring in rings(feat["geometry"]):
            xs = [p[0] for p in ring]
            ys = [p[1] for p in ring]
            polys.append((min(xs), min(ys), max(xs), max(ys), ring))

    dots = []
    lat = H.LAT_MAX
    while lat >= H.LAT_MIN:
        lon = H.LON_MIN
        while lon <= H.LON_MAX:
            for minlon, minlat, maxlon, maxlat, ring in polys:
                if minlon <= lon <= maxlon and minlat <= lat <= maxlat and point_in_ring(lon, lat, ring):
                    x = (lon - H.LON_MIN) * H.KX
                    y = H.LAT_MAX - lat
                    dots.append((x, y))
                    break
            lon += STEP
        lat -= STEP

    circles = "".join(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{DOT_R}"/>' for x, y in dots)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {H.WIDTH:.2f} {H.HEIGHT:.2f}" '
        f'fill="currentColor" preserveAspectRatio="xMidYMid meet">{circles}</svg>'
    )
    OUT.write_text(svg)
    print(f"{len(dots)} dots -> {OUT} ({len(svg)} bytes); aspect {H.ASPECT:.3f}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/world.geojson")
