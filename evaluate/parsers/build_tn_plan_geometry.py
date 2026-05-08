"""Build a district-level shapefile from the SA7001 block-equivalency CSV.

Inputs:
  - data/tn/sa7001_assignments.csv   (from tn_sa7001 parser)
  - data/tn/tl_2024_us_county.shp     (filter STATEFP=47)
  - data/tn/tl_2020_47_vtd20.shp      (VTD geometries with NAME20)

Strategy:
  1. Build a per-VTD assignment by joining the bill rows.
     - Whole-county rows: assign every VTD in that county to the district.
     - Whole-VTD rows: assign that VTD to the district.
     - Split-VTD rows (block-level): count blocks per district within the
       VTD; assign the VTD to the dominant district. Track which VTDs were
       split (for warnings in the report).
  2. Dissolve the assigned VTDs by district to produce 9 polygons.

Approximation: split VTDs (~640 of ~1965) are assigned wholly to one
district. This loses block-level resolution within those VTDs but keeps the
overall map structurally correct.
"""
import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

import geopandas as gpd
import pandas as pd


def buildVtdAssignment(assignments_csv: Path, county_shp: Path, vtd_shp: Path):
    bef = pd.read_csv(assignments_csv, dtype={"district": int, "county": str, "vtd": str, "block": str}, keep_default_na=False)

    counties = gpd.read_file(county_shp)
    counties = counties[counties["STATEFP"] == "47"][["NAME", "COUNTYFP", "geometry"]].copy()
    counties.rename(columns={"NAME": "county_name", "COUNTYFP": "county_fp"}, inplace=True)

    vtds = gpd.read_file(vtd_shp)[["COUNTYFP20", "NAME20", "GEOID20", "geometry"]].copy()
    vtds.rename(columns={"COUNTYFP20": "county_fp", "NAME20": "vtd_name", "GEOID20": "geoid20"}, inplace=True)

    # Map county name -> fp (case-insensitive match)
    name_to_fp = {n.lower(): fp for n, fp in zip(counties["county_name"], counties["county_fp"])}
    bef["county_fp"] = bef["county"].str.lower().map(name_to_fp)
    missing = bef[bef["county_fp"].isna()]["county"].unique()
    if len(missing):
        print(f"[warn] {len(missing)} county names in bill not found in TIGER: {sorted(missing)}")
    bef = bef.dropna(subset=["county_fp"])

    # Step 1: whole-county rows (vtd == "" and block == "")
    whole_county = bef[(bef["vtd"] == "") & (bef["block"] == "")]
    whole_county_lookup = dict(zip(whole_county["county_fp"], whole_county["district"]))

    # Step 2: whole-VTD rows (vtd != "", block == "")
    whole_vtd = bef[(bef["vtd"] != "") & (bef["block"] == "")]
    # key = (county_fp, vtd_name) -> district
    whole_vtd_lookup = {}
    for _, r in whole_vtd.iterrows():
        whole_vtd_lookup[(r["county_fp"], r["vtd"])] = r["district"]

    # Step 3: split-VTD block-level rows: assign VTD to district with most blocks
    split_blocks = bef[bef["block"] != ""]
    split_vtd_counts = defaultdict(Counter)
    for _, r in split_blocks.iterrows():
        split_vtd_counts[(r["county_fp"], r["vtd"])][r["district"]] += 1
    split_vtd_lookup = {
        key: counter.most_common(1)[0][0] for key, counter in split_vtd_counts.items()
    }

    # Apply: every TIGER VTD gets a district
    def lookupDistrict(row):
        key = (row["county_fp"], row["vtd_name"])
        # priority: split-vtd lookup > whole-vtd lookup > whole-county fallback
        if key in split_vtd_lookup:
            return split_vtd_lookup[key]
        if key in whole_vtd_lookup:
            return whole_vtd_lookup[key]
        return whole_county_lookup.get(row["county_fp"])

    vtds["district"] = vtds.apply(lookupDistrict, axis=1)
    unassigned = vtds["district"].isna().sum()
    print(f"VTD assignment: {len(vtds)} total, {unassigned} unassigned")
    if unassigned:
        sample = vtds[vtds["district"].isna()].head(10)
        print("Unassigned sample:")
        for _, r in sample.iterrows():
            print(f"  cf={r['county_fp']} name={r['vtd_name']!r}")

    vtds = vtds.dropna(subset=["district"]).copy()
    vtds["district"] = vtds["district"].astype(int)
    return vtds, len(split_vtd_lookup)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--assignments", type=Path, default=Path("data/tn/sa7001_assignments.csv"))
    ap.add_argument("--counties", type=Path, default=Path("data/tn/tl_2024_us_county.shp"))
    ap.add_argument("--vtds", type=Path, default=Path("data/tn/tl_2020_47_vtd20.shp"))
    ap.add_argument("--out-vtd", type=Path, default=Path("data/tn/tn_2026_proposed_vtd.shp"),
                    help="Per-VTD shapefile with district assignment")
    ap.add_argument("--out-plan", type=Path, default=Path("data/tn/proposed_2026_congressional.shp"),
                    help="Dissolved plan: 9 district polygons")
    args = ap.parse_args(argv)

    vtds, n_split = buildVtdAssignment(args.assignments, args.counties, args.vtds)
    print(f"Split VTDs (assigned to dominant district): {n_split}")

    vtds.to_file(args.out_vtd)
    print(f"Wrote per-VTD assignments: {args.out_vtd}")

    plan = vtds.dissolve(by="district", as_index=False)[["district", "geometry"]]
    plan["DISTRICT"] = plan["district"].astype(int)
    plan = plan[["DISTRICT", "geometry"]]
    plan.to_file(args.out_plan)
    print(f"Wrote dissolved plan: {args.out_plan} ({len(plan)} districts)")


if __name__ == "__main__":
    sys.exit(main())
