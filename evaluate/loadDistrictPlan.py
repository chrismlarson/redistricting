import geopandas as gpd
import pandas as pd

from evaluate.planSpec import PlanSpec


def loadDistrictPlan(spec: PlanSpec) -> gpd.GeoDataFrame:
    """Load a district plan shapefile/GeoJSON, reproject, and return one row per district."""
    gdf = gpd.read_file(spec.plan_path)
    if gdf.crs is None:
        raise ValueError(f"Plan at {spec.plan_path} has no CRS — cannot reproject")
    gdf = gdf.to_crs(spec.target_crs)

    if spec.plan_district_col not in gdf.columns:
        raise KeyError(
            f"District column '{spec.plan_district_col}' not in plan columns: {list(gdf.columns)}"
        )

    gdf = gdf.rename(columns={spec.plan_district_col: "district"})
    gdf["district"] = pd.to_numeric(gdf["district"], errors="coerce").astype("Int64")
    gdf = gdf.dissolve(by="district", as_index=False)

    if len(gdf) != spec.seat_count:
        print(
            f"[warn] plan has {len(gdf)} districts, spec.seat_count={spec.seat_count}"
        )

    return gdf[["district", "geometry"]]
