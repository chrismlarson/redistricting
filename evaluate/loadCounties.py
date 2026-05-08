import geopandas as gpd

from evaluate.planSpec import PlanSpec


def loadCounties(spec: PlanSpec) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(spec.county_path)
    if gdf.crs is None:
        raise ValueError(f"Counties at {spec.county_path} have no CRS")
    gdf = gdf.to_crs(spec.target_crs)

    name_col = next(
        (c for c in ("NAME", "NAMELSAD", "COUNTY", "name") if c in gdf.columns), None
    )
    if name_col is None:
        gdf["county_name"] = gdf.index.astype(str)
    else:
        gdf = gdf.rename(columns={name_col: "county_name"})

    if "STATEFP" in gdf.columns:
        gdf = gdf[gdf["STATEFP"] == spec.state_fips]

    return gdf[["county_name", "geometry"]].reset_index(drop=True)
