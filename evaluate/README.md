# `evaluate/` — district plan fairness evaluation

State- and chamber-agnostic evaluation of an externally-provided district plan.
Computes scalar fairness metrics: compactness, population equality, partisan
symmetry (efficiency gap, mean-median, partisan bias, declination,
lopsided margins), competitiveness, and county splits.

This module is independent of the rest of the repo (which generates plans from
geometry+population). It only requires geopandas, pandas, scipy, matplotlib.

## Run

```bash
pip install -r requirements.txt
PYTHONPATH="$(pwd)" python evaluate/report.py \
    --spec evaluate/plans/tn_2026_congressional.py \
    --out reports/tn_2026_congressional.md
```

## Adding a new plan

Create a new file under `evaluate/plans/` defining a top-level
`SPEC = PlanSpec(...)`. Drop the four required files into `data/<state>/`:

- District plan shapefile/GeoJSON (must have a per-feature district id column)
- Precinct shapefile with `TOTPOP`, `G20PREDBID`, `G20PRERTRU` (or supply
  alternate column names in the spec)
- Counties shapefile (TIGER works)

Set chamber to one of `us_house | state_senate | state_house` and `seat_count`
accordingly. The population-deviation threshold and seat-count math adjust
automatically.

## Data sources

### Proposed / enacted plans

- **Redistricting Data Hub** — https://redistrictingdatahub.org/ posts
  shapefiles within days of enactment for any state.
- **Census TIGER/Line** — https://www.census.gov/cgi-bin/geo/shapefiles/index.php
  for current congressional & state legislative boundaries.
- State sources vary; for Tennessee:
  https://comptroller.tn.gov/maps/u-s--congress-districts.html (email
  `Redistricting@cot.tn.gov` if a new map isn't posted yet).

### Precinct election results

- **VEST 2020** (free, CC) —
  https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/K7760H
  — file `<state>_2020.zip`. Columns include `G20PREDBID`, `G20PRERTRU`,
  `TOTPOP`.

### Counties

- Census TIGER, filtered by state FIPS.

## Metrics implemented

| Metric | Source |
|---|---|
| Polsby-Popper, Reock, Schwartzberg, Convex Hull | `metrics/compactness.py` |
| Population deviation (chamber-aware threshold) | `metrics/population.py` |
| Efficiency gap, mean-median, partisan bias, declination, lopsided margins | `metrics/partisan.py` |
| Competitiveness (45-55 / 47-53 vote bands) | `metrics/competitiveness.py` |
| County splits & fragments | `metrics/splits.py` |

## Out of scope

- MCMC ensemble outlier analysis (planned follow-up via `gerrychain`).
- VRA / minority cracking metrics — needs CVAP block disaggregation since
  VEST 2020 does not include race columns.
- Election cycles other than 2020 presidential (until VEST 2022 is added).
