import geopandas as gpd
import pandas as pd

SLIVER_AREA_FRACTION = 0.001  # ignore county fragments smaller than 0.1% of county area


def computeCountySplits(plan: gpd.GeoDataFrame, counties: gpd.GeoDataFrame) -> dict:
    overlay = gpd.overlay(counties, plan, how="intersection", keep_geom_type=True)
    overlay["frag_area"] = overlay.geometry.area

    county_areas = counties.set_index("county_name").geometry.area
    overlay["county_area"] = overlay["county_name"].map(county_areas)
    overlay["frag_fraction"] = overlay["frag_area"] / overlay["county_area"]

    significant = overlay[overlay["frag_fraction"] > SLIVER_AREA_FRACTION]

    splits_per_county = (
        significant.groupby("county_name")["district"].nunique().rename("districts_touched")
    )
    split_counties = splits_per_county[splits_per_county > 1]

    return {
        "total_counties": int(len(counties)),
        "split_county_count": int(len(split_counties)),
        "max_splits_in_one_county": int(split_counties.max()) if len(split_counties) else 0,
        "total_fragments_in_split_counties": int(
            splits_per_county[splits_per_county > 1].sum()
        ),
        "split_county_detail": split_counties.sort_values(ascending=False).to_dict(),
    }
