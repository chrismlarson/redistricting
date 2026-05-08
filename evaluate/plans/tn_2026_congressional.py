from pathlib import Path

from evaluate.planSpec import PlanSpec

DATA = Path("data/tn")

SPEC = PlanSpec(
    name="tn_2026_congressional",
    state_fips="47",
    state_abbr="TN",
    chamber="us_house",
    seat_count=9,
    plan_path=DATA / "proposed_2026_congressional.shp",
    precinct_path=DATA / "tn_2020.shp",
    county_path=DATA / "tl_2024_us_county.shp",
    plan_district_col="DISTRICT",
    precinct_dem_col="G20PREDBID",
    precinct_rep_col="G20PRERTRU",
    precinct_pop_col="",  # VEST 2020 TN does not include population — pop deviation skipped
    notes=(
        "TN GOP-led legislature unveiled new US Congressional map on 2026-05-06; "
        "reporting suggests Memphis and Nashville are being cracked. Evaluating "
        "with VEST 2020 presidential precinct data."
    ),
)
