"""Export a fully static copy of the site into dist/ for GitHub Pages.

Builds the dataset once, writes every API payload as a flat JSON file under
dist/data/ (including one per match and per team, since static hosting has no
path params), copies web/ over, and flips index.html into static mode so the
frontend reads ./data/*.json instead of the Flask API. Identical UI, no server.

Usage:
    python scripts/build_static.py            # fetch live openfootball data
    python scripts/build_static.py --local f  # build from a local feed file
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from server import dataset as D  # noqa: E402
from server import news  # noqa: E402
from server.sources.base import DataSource  # noqa: E402
from server.sources.openfootball import OpenFootballSource  # noqa: E402

WEB = ROOT / "web"
DIST = ROOT / "dist"
STATIC_CONFIG = '<script>window.__WC_API__={base:"data",ext:".json"};</script>'


class LocalFileSource(DataSource):
    name = "openfootball-local"

    def __init__(self, path):
        self.path = path

    def fetch_matches(self):
        return json.loads(Path(self.path).read_text())["matches"]


def write(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", help="path to a local worldcup.json instead of fetching")
    args = ap.parse_args()

    source = LocalFileSource(args.local) if args.local else OpenFootballSource()
    print(f"Building dataset from {source.name}…")
    ds = D.build(source)

    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(WEB, DIST)

    # flip index.html into static mode
    index = DIST / "index.html"
    html = index.read_text(encoding="utf-8").replace("<!--WC_CONFIG-->", STATIC_CONFIG)
    index.write_text(html, encoding="utf-8")

    data = DIST / "data"
    write(data / "overview.json", D.overview(ds))
    write(data / "matches.json", D.matches(ds))
    write(data / "groups.json", D.groups(ds))
    write(data / "teams.json", D.teams(ds))
    write(data / "bracket.json", D.bracket(ds))
    write(data / "stats.json", D.stats(ds))
    write(data / "news.json", {"items": news.fetch_news()})
    write(data / "status.json", {
        "source": ds["source"], "updated_at": ds["generated_at"], "stale": False,
    })
    for m in ds["matches"]:
        write(data / "match" / f"{m['id']}.json", D.match(ds, m["id"]))
    for t in D.teams(ds)["teams"]:
        write(data / "team" / f"{t['slug']}.json", D.team(ds, t["slug"]))

    n_files = sum(1 for _ in DIST.rglob("*") if _.is_file())
    print(f"Wrote dist/ ({n_files} files). Serve it with any static server, e.g.:")
    print("  python -m http.server -d dist 8000")


if __name__ == "__main__":
    main()
