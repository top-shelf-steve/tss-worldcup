"""Flask app: serves the static frontend and the JSON API off the cache.

Run directly (`python server/app.py`) to serve the tournament to your LAN.
The same payload functions feed scripts/build_static.py for GitHub Pages.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, abort, jsonify, send_from_directory

from . import dataset as D
from .cache import DataCache
from .sources.openfootball import OpenFootballSource

load_dotenv()

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app = Flask(__name__, static_folder=None)
cache = DataCache(
    source=OpenFootballSource(),
    refresh_seconds=int(os.getenv("REFRESH_SECONDS", "600")),
)


def _dataset():
    ds = cache.dataset
    if ds is None:
        abort(503, description="Tournament data not loaded yet — try again shortly.")
    return ds


# --- API -------------------------------------------------------------------

@app.get("/api/status")
def api_status():
    return jsonify(cache.status())


@app.get("/api/overview")
def api_overview():
    return jsonify(D.overview(_dataset()))


@app.get("/api/matches")
def api_matches():
    return jsonify(D.matches(_dataset()))


@app.get("/api/match/<int:match_id>")
def api_match(match_id):
    detail = D.match(_dataset(), match_id)
    return jsonify(detail) if detail else abort(404)


@app.get("/api/groups")
def api_groups():
    return jsonify(D.groups(_dataset()))


@app.get("/api/teams")
def api_teams():
    return jsonify(D.teams(_dataset()))


@app.get("/api/team/<slug>")
def api_team(slug):
    detail = D.team(_dataset(), slug)
    return jsonify(detail) if detail else abort(404)


@app.get("/api/bracket")
def api_bracket():
    return jsonify(D.bracket(_dataset()))


# --- static frontend (SPA) -------------------------------------------------

@app.get("/")
def index():
    return send_from_directory(WEB_DIR, "index.html")


@app.get("/<path:path>")
def assets(path):
    full = WEB_DIR / path
    if full.is_file():
        return send_from_directory(WEB_DIR, path)
    # unknown non-API path -> let the hash-router SPA handle it
    return send_from_directory(WEB_DIR, "index.html")


def main():
    if cache.dataset is None:
        cache.refresh()  # block once so the first request has data
    cache.start_background()
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
