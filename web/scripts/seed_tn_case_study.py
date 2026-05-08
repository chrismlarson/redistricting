"""Seed the TN 2026 congressional case study into the local DB.

Idempotent. If the slug already exists, it is replaced (so re-running picks
up code changes to the JSON contract or figure styling).

Usage:
    python -m web.scripts.seed_tn_case_study
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from sqlmodel import Session, select

from web.config import REPO_ROOT
from web.db import engine, init_db
from web.models import Evaluation
from web.services.evaluator import evaluate_plan
from web.services.states import get_state

SLUG = "tn-2026-congressional"
NAME = "Tennessee 2026 congressional"
NOTES = (
    "TN GOP-led legislature unveiled new US Congressional map on 2026-05-06. "
    "Reporting suggests Memphis and Nashville are being cracked. Evaluated against "
    "VEST 2020 presidential precinct data."
)
PLAN_SOURCE_LABEL = "Tennessee SB7004 / SA7001"


def _resolve_plan_shp() -> Path:
    candidates = [
        REPO_ROOT / "web-data" / "tn" / "proposed_2026_congressional.shp",
        REPO_ROOT / "data" / "tn" / "proposed_2026_congressional.shp",
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError(
        "Could not find proposed_2026_congressional.shp under web-data/tn or data/tn"
    )


def _resolve_vtd_assignments() -> Path | None:
    """The per-VTD shapefile build_tn_plan_geometry.py writes — used only to
    emit a downloadable VTD-equivalency CSV under web/seeds/."""
    candidates = [
        REPO_ROOT / "web-data" / "tn" / "tn_2026_proposed_vtd.shp",
        REPO_ROOT / "data" / "tn" / "tn_2026_proposed_vtd.shp",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _emit_seed_csv() -> None:
    src = _resolve_vtd_assignments()
    if src is None:
        print("[skip] no per-VTD shapefile found; not emitting seed CSV")
        return
    seeds_dir = Path(__file__).resolve().parent.parent / "seeds"
    seeds_dir.mkdir(parents=True, exist_ok=True)
    out_csv = seeds_dir / "tn_2026_congressional.csv"
    gdf = gpd.read_file(src)
    geoid_col = next((c for c in ("GEOID20", "geoid20") if c in gdf.columns), None)
    if geoid_col is None:
        print(f"[skip] no GEOID20/geoid20 column in {src}; columns: {list(gdf.columns)}")
        return
    df = pd.DataFrame({
        "GEOID20": gdf[geoid_col].astype(str),
        "district": pd.to_numeric(gdf["district"], errors="coerce").astype("Int64"),
    }).dropna(subset=["district"])
    df.to_csv(out_csv, index=False)
    print(f"Wrote sample VTD-equivalency CSV: {out_csv} ({len(df)} rows)")


def main() -> int:
    init_db()

    state = get_state("TN")
    plan_shp = _resolve_plan_shp()
    print(f"Evaluating {NAME} from {plan_shp}")

    report = evaluate_plan(
        state=state,
        chamber="us_house",
        seat_count=9,
        name=NAME,
        notes=NOTES,
        slug=SLUG,
        plan_shp_path=plan_shp,
        plan_source_label=PLAN_SOURCE_LABEL,
        plan_source_url=None,
    )

    eg = report["metrics"]["partisan"]["efficiency_gap"]
    pp_min = report["metrics"]["compactness"]["summary"]["polsby_popper"]["min"]
    print(f"  efficiency_gap = {eg!r}")
    print(f"  polsby_popper min = {pp_min!r}")

    with Session(engine) as session:
        existing = session.exec(select(Evaluation).where(Evaluation.slug == SLUG)).first()
        if existing:
            existing.name = NAME
            existing.state_abbr = state.abbr
            existing.chamber = "us_house"
            existing.seat_count = 9
            existing.notes = NOTES
            existing.report_json = json.dumps(report)
            existing.is_seed = True
            session.add(existing)
        else:
            session.add(Evaluation(
                slug=SLUG,
                name=NAME,
                state_abbr=state.abbr,
                chamber="us_house",
                seat_count=9,
                notes=NOTES,
                report_json=json.dumps(report),
                is_seed=True,
            ))
        session.commit()

    _emit_seed_csv()
    print(f"Seeded {SLUG}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
