import geopandas as gpd
import pandas as pd

from evaluate.planSpec import PlanSpec


def loadPrecinctVotes(spec: PlanSpec) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(spec.precinct_path)
    if gdf.crs is None:
        raise ValueError(f"Precincts at {spec.precinct_path} have no CRS")
    gdf = gdf.to_crs(spec.target_crs)

    for col in (spec.precinct_dem_col, spec.precinct_rep_col):
        if col not in gdf.columns:
            raise KeyError(
                f"Expected column '{col}' missing from precincts. Have: {list(gdf.columns)}"
            )

    gdf["dem_votes"] = pd.to_numeric(gdf[spec.precinct_dem_col], errors="coerce").fillna(0)
    gdf["rep_votes"] = pd.to_numeric(gdf[spec.precinct_rep_col], errors="coerce").fillna(0)

    if spec.precinct_pop_col and spec.precinct_pop_col in gdf.columns:
        gdf["pop"] = pd.to_numeric(gdf[spec.precinct_pop_col], errors="coerce").fillna(0)
    else:
        gdf["pop"] = float("nan")  # population not available — pop-deviation skipped

    return gdf[["dem_votes", "rep_votes", "pop", "geometry"]]


def assignPrecinctsToDistricts(
    precincts: gpd.GeoDataFrame, plan: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """Assign each precinct to a district by representative_point spatial join.

    Using representative_point (vs centroid) handles precincts with holes
    or non-convex shapes — same fix pattern used in the block-with-holes case
    elsewhere in this project.
    """
    rep_pts = precincts.copy()
    rep_pts["geometry"] = rep_pts.geometry.representative_point()
    joined = gpd.sjoin(rep_pts, plan[["district", "geometry"]], how="left", predicate="within")

    unmatched = joined["district"].isna().sum()
    if unmatched:
        print(f"[warn] {unmatched}/{len(joined)} precincts did not land in any district")

    precincts = precincts.copy()
    precincts["district"] = joined["district"].values
    return precincts


def aggregateByDistrict(precincts_with_district: gpd.GeoDataFrame) -> pd.DataFrame:
    df = precincts_with_district.dropna(subset=["district"]).copy()
    grouped = (
        df.groupby("district")
        .agg(dem_votes=("dem_votes", "sum"), rep_votes=("rep_votes", "sum"), pop=("pop", "sum"))
        .reset_index()
    )
    grouped["total_votes"] = grouped["dem_votes"] + grouped["rep_votes"]
    grouped["dem_share"] = grouped["dem_votes"] / grouped["total_votes"].replace(0, pd.NA)
    return grouped
