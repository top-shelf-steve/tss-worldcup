# World Cup 2026 Tracker

A clean, self-hosted tracker for the 2026 FIFA World Cup — schedule, results,
group standings, the knockout bracket, every team, and a **Team USA** spotlight.

Deliberately *not* a generic dashboard: ink-on-paper, hairline rules, real type
hierarchy. Flat — no gradients, glass, or drop shadows.

![sections: Overview · Matches · Groups · Bracket · Teams](web/assets/na-dots.svg)

## How it works

- **Data**: the free, public-domain [`openfootball/worldcup.json`](https://github.com/openfootball/worldcup.json)
  feed (schedule, final scores, goal scorers). Standings and the bracket are
  computed from results.
- **Server**: a small Flask app pulls + caches the feed on a schedule and serves
  the site to your LAN. It keeps serving the last good data (and a disk copy
  across restarts) if a refresh fails.
- **Frontend**: vanilla HTML/CSS/JS, no build step. A normalized data layer sits
  between the source and the UI, so a richer **keyed** source can be added later
  to light up the live clock / Lineups / Stats — without touching the frontend.

## Run it (local network)

```bash
cd world-cup
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # optional: change PORT / REFRESH_SECONDS
python -m server.app
```

Open `http://localhost:8080`, or from another device on your network use the
machine's LAN IP, e.g. `http://192.168.1.50:8080` (find it with `ipconfig getifaddr en0`).

> Run as a module (`python -m server.app`) so the package imports resolve.

## Publish to GitHub Pages

GitHub Pages is static — there's no Flask server — so you publish the `dist/`
snapshot. The included Action (`.github/workflows/pages.yml`) builds and deploys
it automatically: on every push to `main`, **and on a 30-minute schedule** so
results/standings/bracket stay current during the tournament without any manual
work. You can also trigger a rebuild from the repo's **Actions** tab.

**One-time setup:** in the repo, go to **Settings → Pages → Build and deployment**
and set **Source = GitHub Actions**. Push to `main` (or run the workflow) and the
site goes live at `https://<you>.github.io/tss-worldcup/`. All asset paths are
relative and routing is hash-based, so it works under that subpath as-is.

Preview the static build locally first if you like:

```bash
python scripts/build_static.py        # fetches data, writes dist/
python -m http.server -d dist 8000    # http://localhost:8000
```

### Phase 2: authoritative data on Pages (optional)

The default build uses the free openfootball feed (hand-updated, can lag). To bake
in authoritative scores — and eventually lineups/stats — at build time:

1. Get a free [API-Football](https://dashboard.api-football.com) key (100 req/day
   is plenty for a 30-min rebuild; World Cup is `league=1&season=2026`).
2. Add it as a repo secret: **Settings → Secrets and variables → Actions →**
   `API_FOOTBALL_KEY`.
3. Uncomment the `env:` block in `pages.yml` and implement
   `server/sources/apifootball.py` (same `DataSource` interface — no frontend
   changes). The Action runs server-side, so the key stays secret.

This stays a periodically-rebuilt snapshot, not a second-by-second live clock —
for that, run the Flask server locally (Phase 3).

## Project layout

```
server/            Flask app + data layer
  app.py             routes: serves web/ and /api/*
  cache.py           TTL cache, background refresh, disk fallback
  dataset.py         assembles the feed into per-endpoint payloads
  standings.py       group tables from results
  bracket.py         resolves 1A/2A/W73… slots, builds the bracket
  teams.py           48-team metadata (flag code, confederation)
  sources/
    base.py          DataSource contract + normalized match shape
    openfootball.py  the free, no-key source
web/               static frontend (vanilla, hash-routed SPA)
  index.html  css/  js/{api,app,util,components,views/*}  assets/{flags,na-dots.svg}
scripts/
  build_static.py    export dist/ for GitHub Pages
  gen_na_dots.py     (one-off) regenerate the dotted US/Canada/Mexico map
```

## What's stubbed (and why)

The Overview mockup includes a live match clock, Lineups, detailed Stats, and
News. The free feed can't provide those, so they render as honest empty states.
They're **keyed-ready**: add `server/sources/apifootball.py` implementing the
same `DataSource` interface, set `API_FOOTBALL_KEY` in `.env`, and those views
fill in automatically — no frontend changes.

Standings tiebreakers use the simplified order (points, goal difference, goals
for); official rules add head-to-head and fair-play. Knockout draws decided on
penalties show as undecided since the feed lacks shoot-out data.

Data: openfootball (public domain). Flags: [flag-icons](https://github.com/lipis/flag-icons) (MIT).
Dotted map generated from [Natural Earth](https://www.naturalearthdata.com/) (public domain).
