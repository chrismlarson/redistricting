"""Run the evaluate/ pipeline for the web app.

Inputs:
  * a registered state (with precincts/counties/VTDs on disk via web-data/)
  * a plan source — either a prebuilt district shapefile (case study seed) or
    a VTD-equivalency CSV with columns GEOID20,district uploaded by the user

Outputs:
  * a dict matching the JSON contract documented in the redistricting plan
  * two PNG choropleths written to STORAGE/images/{slug}/
"""
from __future__ import annotations

import math
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # headless; must precede pyplot import

import geopandas as gpd  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from evaluate.loadCounties import loadCounties
from evaluate.loadDistrictPlan import loadDistrictPlan
from evaluate.loadPrecinctVotes import (
    aggregateByDistrict,
    assignPrecinctsToDistricts,
    loadPrecinctVotes,
)
from evaluate.metrics.compactness import computeCompactness
from evaluate.metrics.competitiveness import computeCompetitiveness
from evaluate.metrics.partisan import computePartisan
from evaluate.metrics.population import computePopulationDeviation
from evaluate.metrics.splits import computeCountySplits
from evaluate.planSpec import PlanSpec

from web.config import IMAGES_DIR, REPO_ROOT, URL_PREFIX
from web.services.states import StateData


SCHEMA_VERSION = "1.0"


def _f(x) -> Optional[float]:
    """Float for JSON, with NaN/Inf -> None."""
    if x is None:
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    if math.isnan(v) or math.isinf(v):
        return None
    return v


def _i(x) -> Optional[int]:
    if x is None:
        return None
    try:
        if pd.isna(x):
            return None
    except (TypeError, ValueError):
        pass
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def _repo_commit() -> Optional[str]:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, stderr=subprocess.DEVNULL
        )
        return out.decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None


def vtd_csv_to_plan_shapefile(csv_path: Path, vtd_shp_path: Path, out_shp: Path) -> None:
    """Join a `GEOID20,district` CSV against the state's VTD shapefile and
    dissolve to per-district polygons. Writes a shapefile to out_shp."""
    df = pd.read_csv(csv_path, dtype=str)
    df.columns = [c.strip() for c in df.columns]
    cmap = {c.lower(): c for c in df.columns}
    geoid_col = cmap.get("geoid20") or cmap.get("geoid")
    district_col = cmap.get("district")
    if geoid_col is None or district_col is None:
        raise ValueError(
            f"CSV must have GEOID20 and district columns; got {list(df.columns)}"
        )
    df = df[[geoid_col, district_col]].rename(columns={geoid_col: "GEOID20", district_col: "district"})
    df["district"] = pd.to_numeric(df["district"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["district", "GEOID20"]).copy()
    df["GEOID20"] = df["GEOID20"].astype(str).str.strip()

    vtds_full = gpd.read_file(vtd_shp_path)
    geoid_col_v = next((c for c in vtds_full.columns if c.lower() == "geoid20"), None)
    if geoid_col_v is None:
        raise ValueError(
            f"State VTD shapefile {vtd_shp_path.name} has no GEOID20 column"
        )
    vtds = vtds_full[[geoid_col_v, "geometry"]].rename(columns={geoid_col_v: "GEOID20"})
    vtds["GEOID20"] = vtds["GEOID20"].astype(str)

    joined = vtds.merge(df, on="GEOID20", how="inner")
    if joined.empty:
        raise ValueError(
            "No GEOID20 values from the CSV matched the state's VTD shapefile."
        )

    plan = joined.dissolve(by="district", as_index=False)[["district", "geometry"]]
    plan["DISTRICT"] = plan["district"].astype(int)
    plan = plan[["DISTRICT", "geometry"]]
    out_shp.parent.mkdir(parents=True, exist_ok=True)
    plan.to_file(out_shp)


def write_figures(plan, district_df, compactness_df, out_dir: Path, slug: str) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)

    plan_pp = plan.merge(compactness_df[["district", "polsby_popper"]], on="district")
    plan_share = plan.merge(district_df[["district", "dem_share"]], on="district")

    fig, ax = plt.subplots(figsize=(10, 7))
    plan_pp.plot(column="polsby_popper", cmap="viridis", legend=True, edgecolor="black", ax=ax)
    ax.set_title("Polsby-Popper compactness")
    ax.set_axis_off()
    pp_path = out_dir / "compactness.png"
    fig.savefig(pp_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 7))
    plan_share.plot(column="dem_share", cmap="RdBu", vmin=0.2, vmax=0.8, legend=True, edgecolor="black", ax=ax)
    ax.set_title("2020 presidential D vote share")
    ax.set_axis_off()
    share_path = out_dir / "dem_share.png"
    fig.savefig(share_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return {
        "compactness_choropleth": f"{URL_PREFIX}/static/images/{slug}/compactness.png",
        "dem_share_choropleth": f"{URL_PREFIX}/static/images/{slug}/dem_share.png",
    }


def _serialize_compactness(compactness_df: pd.DataFrame) -> dict:
    metrics = ["polsby_popper", "reock", "schwartzberg", "convex_hull"]
    summary = {}
    for m in metrics:
        col = compactness_df[m]
        summary[m] = {
            "mean": _f(col.mean()),
            "min": _f(col.min()),
        }
    per_district = []
    for _, r in compactness_df.iterrows():
        per_district.append({
            "district": _i(r["district"]),
            "polsby_popper": _f(r["polsby_popper"]),
            "reock": _f(r["reock"]),
            "schwartzberg": _f(r["schwartzberg"]),
            "convex_hull": _f(r["convex_hull"]),
        })
    return {"summary": summary, "per_district": per_district}


def _serialize_partisan(partisan: dict) -> dict:
    decl = _f(partisan.get("declination"))
    decl_reason = None
    if decl is None:
        decl_reason = "Either every district was won by the same party, or no votes were recorded."
    lm_in = partisan.get("lopsided_margins", {})
    return {
        "efficiency_gap": _f(partisan.get("efficiency_gap")),
        "mean_median": _f(partisan.get("mean_median")),
        "partisan_bias": _f(partisan.get("partisan_bias")),
        "declination": decl,
        "declination_undefined_reason": decl_reason,
        "lopsided_margins": {
            "dem_mean_margin": _f(lm_in.get("dem_mean_margin")),
            "rep_mean_margin": _f(lm_in.get("rep_mean_margin")),
            "t_stat": _f(lm_in.get("t_stat")),
            "p_value": _f(lm_in.get("p_value")),
        },
    }


def _serialize_splits(splits: dict) -> dict:
    detail = []
    for county, n in splits.get("split_county_detail", {}).items():
        detail.append({"county": str(county), "districts_touched_count": int(n)})
    return {
        "total_counties": _i(splits.get("total_counties")) or 0,
        "split_county_count": _i(splits.get("split_county_count")) or 0,
        "max_splits_in_one_county": _i(splits.get("max_splits_in_one_county")) or 0,
        "total_fragments_in_split_counties": _i(splits.get("total_fragments_in_split_counties")) or 0,
        "detail": detail,
    }


def _serialize_population(pop: dict) -> dict:
    if not pop.get("available"):
        return {"available": False, "reason": pop.get("reason", "unknown")}
    return {
        "available": True,
        "total_population": _f(pop.get("total_population")),
        "ideal_population": _f(pop.get("ideal_population")),
        "max_abs_deviation": _f(pop.get("max_abs_deviation")),
        "threshold": _f(pop.get("threshold")),
        "exceeds_threshold": bool(pop.get("exceeds_threshold")),
        "per_district": [
            {
                "district": _i(d.get("district")),
                "pop": _f(d.get("pop")),
                "pop_deviation": _f(d.get("pop_deviation")),
            }
            for d in pop.get("per_district", [])
        ],
    }


def _serialize_district_detail(district_df: pd.DataFrame, pop_per_district: list) -> list:
    pop_lookup = {_i(d.get("district")): _f(d.get("pop_deviation")) for d in pop_per_district or []}
    out = []
    for _, r in district_df.sort_values("district").iterrows():
        district = _i(r["district"])
        out.append({
            "district": district,
            "dem_votes": _f(r["dem_votes"]),
            "rep_votes": _f(r["rep_votes"]),
            "total_votes": _f(r.get("total_votes")),
            "dem_share": _f(r.get("dem_share")),
            "pop": _f(r.get("pop")),
            "pop_deviation": pop_lookup.get(district),
        })
    return out


def evaluate_plan(
    *,
    state: StateData,
    chamber: str,
    seat_count: int,
    name: str,
    notes: str,
    slug: str,
    plan_shp_path: Optional[Path] = None,
    vtd_csv_path: Optional[Path] = None,
    plan_source_label: str = "",
    plan_source_url: Optional[str] = None,
) -> dict:
    if not plan_shp_path and not vtd_csv_path:
        raise ValueError("Must provide either plan_shp_path or vtd_csv_path")

    work_dir: Optional[tempfile.TemporaryDirectory] = None
    if vtd_csv_path is not None:
        work_dir = tempfile.TemporaryDirectory(prefix=f"plan_{slug}_")
        plan_shp_path = Path(work_dir.name) / "plan.shp"
        vtd_csv_to_plan_shapefile(vtd_csv_path, state.vtd_path, plan_shp_path)

    try:
        spec = PlanSpec(
            name=slug,
            state_fips=state.fips,
            state_abbr=state.abbr,
            chamber=chamber,
            seat_count=seat_count,
            plan_path=plan_shp_path,
            precinct_path=state.precinct_path,
            county_path=state.county_path,
            precinct_dem_col=state.precinct_dem_col,
            precinct_rep_col=state.precinct_rep_col,
            precinct_pop_col=state.precinct_pop_col,
            notes=notes,
        )

        plan = loadDistrictPlan(spec)
        precincts = loadPrecinctVotes(spec)
        precincts_d = assignPrecinctsToDistricts(precincts, plan)
        district_df = aggregateByDistrict(precincts_d)

        compactness_df = computeCompactness(plan)
        counties = loadCounties(spec)
        partisan = computePartisan(district_df)
        competitiveness = computeCompetitiveness(district_df)
        splits = computeCountySplits(plan, counties)
        population = computePopulationDeviation(district_df, spec)

        slug_dir = IMAGES_DIR / slug
        images = write_figures(plan, district_df, compactness_df, slug_dir, slug)
    finally:
        if work_dir is not None:
            work_dir.cleanup()

    pop_serialized = _serialize_population(population)
    pop_per_dist = pop_serialized.get("per_district", []) if pop_serialized.get("available") else []

    contract = {
        "schema_version": SCHEMA_VERSION,
        "id": slug,
        "slug": slug,
        "name": name,
        "state": {"fips": state.fips, "abbr": state.abbr, "name": state.name},
        "chamber": chamber,
        "seat_count": seat_count,
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "data_vintage": {
            "precincts": {"source": "VEST 2020", "doi": "10.7910/DVN/K7760H"},
            "counties": {"source": "Census TIGER/Line"},
            "plan_source": {"label": plan_source_label, "url": plan_source_url},
        },
        "code_version": {"repo_commit": _repo_commit()},
        "metrics": {
            "compactness": _serialize_compactness(compactness_df),
            "partisan": _serialize_partisan(partisan),
            "competitiveness": {
                "districts_in_45_55_band": _i(competitiveness.get("districts_in_45_55_band")) or 0,
                "districts_in_47_53_band": _i(competitiveness.get("districts_in_47_53_band")) or 0,
                "total_districts": _i(competitiveness.get("total_districts")) or 0,
            },
            "splits": _serialize_splits(splits),
            "population": pop_serialized,
        },
        "per_district": _serialize_district_detail(district_df, pop_per_dist),
        "images": images,
        "warnings": [],
        "links": {
            "plan_source": {"label": plan_source_label, "url": plan_source_url},
            "precinct_data": {
                "label": "VEST 2020 on Harvard Dataverse",
                "url": "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/K7760H",
            },
            "shapefiles": {
                "label": "Census TIGER/Line",
                "url": "https://www.census.gov/cgi-bin/geo/shapefiles/index.php",
            },
        },
    }

    if not pop_serialized.get("available"):
        contract["warnings"].append(
            f"Population deviation not computed: {pop_serialized.get('reason')}"
        )

    return contract
