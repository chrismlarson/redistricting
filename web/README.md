# `web/` — redistricting fairness evaluator (FastAPI)

A small FastAPI + Jinja2 service that scores district maps using the same
metric pipeline (`evaluate/` at the repo root) as the CLI. Runs at
`chrislarson.com/redistricting`.

The web app and the CLI share `evaluate/` directly — there is no vendoring,
no submodule, and no JS/TypeScript port of the metrics. Single source of truth.

## What it serves

| Route | Purpose |
|---|---|
| `/redistricting/` | Index. Lists case studies and recent evaluations. |
| `/redistricting/methodology` | Per-metric explanation, legal context, data sources. |
| `/redistricting/evaluate` | Upload form. Accepts a VTD-equivalency CSV. |
| `/redistricting/r/{slug}` | Results page (case studies and uploads share this template). |
| `/redistricting/r/{slug}.json` | Same evaluation, JSON contract documented in the project plan. |

## Local development

The service requires the geopandas/scipy/matplotlib stack the `evaluate/`
module needs, plus the FastAPI extras pinned in `web/requirements.txt`.

```bash
cd <repo root>
python -m venv .venv
. .venv/bin/activate          # (Windows) .venv\Scripts\activate
pip install -r requirements.txt          # geopandas, pandas, scipy, matplotlib, ...
pip install -r web/requirements.txt      # fastapi, uvicorn, jinja2, sqlmodel, ...

# State precincts/counties/VTDs are expected under web-data/ in production.
# Locally the service will fall back to the CLI's data/ directory if web-data
# is empty — so an existing checkout with data/tn/ already populated needs
# no further data setup.

# Seed the TN 2026 case study.
PYTHONPATH=. python -m web.scripts.seed_tn_case_study

# Run the server on the same port the systemd unit uses in production.
PYTHONPATH=. uvicorn web.main:app --host 127.0.0.1 --port 3006 --reload
```

Then open http://127.0.0.1:3006/redistricting/.

The server stores SQLite + generated PNGs under `storage/` (gitignored). To
reseed (e.g. after changing the JSON contract), simply re-run the seed script
— the slug `tn-2026-congressional` is replaced in place.

## Upload format

CSV with two columns:

| Column | Type | Notes |
|---|---|---|
| `GEOID20` | string | 12-character Census VTD identifier (state + county + VTD) |
| `district` | int | district number assigned to that VTD |

One row per VTD in the state's universe. Unmatched GEOID20s are dropped; if
zero rows match, the upload is rejected with a 400 explaining the mismatch.

For plans published as block-equivalency files (RDH, state legislatures), the
canonical workflow is:

1. Aggregate blocks → VTDs externally (e.g. with the `parsers/` and
   `build_tn_plan_geometry.py` tooling at the repo root).
2. Export the resulting VTD assignments as `GEOID20,district`.
3. Upload here.

A reference VTD CSV for the TN 2026 plan is generated at
`web/seeds/tn_2026_congressional.csv` by `seed_tn_case_study.py`.

## Adding a state

1. Drop the state's VEST 2020 precinct shapefile, the matching TIGER VTD
   shapefile, and the TIGER counties shapefile into `web-data/{abbr}/` on the
   server (or in the repo's `data/{abbr}/` for local dev).
2. Add an entry to `_STATES` in `web/services/states.py` with the file paths
   and the column name overrides if the state's VEST file differs.

No metric code changes. The dropdown on `/evaluate` lists every state whose
precinct file exists at startup time.

## Deploy

GitHub Actions workflow at `.github/workflows/deploy-web.yml`:
- triggers on push to `master`/`main` paths under `web/` or `evaluate/`
- rsyncs `web/` and `evaluate/` to `/var/www/redistricting/` on the droplet
- runs `pip install` inside the server's venv
- restarts `systemctl restart redistricting`

The GitHub Actions secrets needed: `DEPLOY_HOST`, `DEPLOY_USER`,
`DEPLOY_SSH_KEY` (matching the existing fleet conventions).

State data files (`web-data/{abbr}/...`) are **not** rsynced. They must be
staged on the server once via scp and live alongside the deployed code.

The Nginx snippet to add (under `/etc/nginx/sites-available/chrislarson.com`)
is at `web/nginx.conf`. The systemd unit is `web/redistricting.service`. Both
require manual installation on the first deploy.

Port: **3006** (the next free port in the chrislarson.com fleet — 3001
vacation-room, 3002 vote, 3003 meshcoreplanner, 3004 ai-gm, 3005 raffle).

## What's intentionally not here

- **Authentication.** Public, anyone can upload. Nginx-level rate limit
  recommended; not in this snippet.
- **Background jobs.** State-level evaluations finish in seconds; `evaluate/`
  is invoked synchronously inside the request handler.
- **Block-level uploads.** V1 is VTD-level only. Block-level (BEF) support
  would mean shipping a per-state block→VTD mapping and aggregating; defer
  until there's demand.
- **Shapefile uploads.** V1 takes a CSV. Adding shapefile support means
  another validation surface (zip handling, CRS sanity); defer.

## File layout

```
web/
├── main.py              FastAPI app, mounts static and routes
├── config.py            paths, port, URL prefix
├── db.py                SQLModel engine + session
├── models.py            Evaluation row
├── templating.py        Jinja2 + filters (fmt_pct, fmt_decimal, fmt_int)
├── routes/              one file per route group
├── services/
│   ├── evaluator.py     wraps evaluate/ — returns the JSON contract dict
│   └── states.py        registry of supported states (V1: TN)
├── templates/           base, index, methodology, evaluate, results
├── static/css/site.css  matches chrislarson.com dark theme
├── seeds/               sample CSVs (auto-generated)
├── scripts/seed_tn_case_study.py
├── redistricting.service systemd unit (production)
├── nginx.conf           location block (production)
└── requirements.txt     web-only deps (geo stack lives at repo root)
```
