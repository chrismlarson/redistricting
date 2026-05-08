from math import pi

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon


def _minimumBoundingCircleArea(geom) -> float:
    try:
        return geom.minimum_bounding_circle().area
    except AttributeError:
        # Shapely <2.0 fallback (project requires 2.0 but be defensive)
        from shapely.ops import unary_union
        hull = geom.convex_hull
        return hull.area * pi / 4


def polsbyPopper(geom) -> float:
    if geom.length == 0:
        return 0.0
    return 4 * pi * geom.area / (geom.length ** 2)


def reock(geom) -> float:
    mbc = _minimumBoundingCircleArea(geom)
    return geom.area / mbc if mbc > 0 else 0.0


def schwartzberg(geom) -> float:
    # Schwartzberg = perimeter / circumference of equal-area circle.
    # Returned as 1 / Schwartzberg so larger = more compact (range (0, 1]).
    if geom.area == 0:
        return 0.0
    equal_area_circle_perim = 2 * pi * (geom.area / pi) ** 0.5
    return equal_area_circle_perim / geom.length if geom.length else 0.0


def convexHullRatio(geom) -> float:
    hull_area = geom.convex_hull.area
    return geom.area / hull_area if hull_area > 0 else 0.0


def computeCompactness(plan: gpd.GeoDataFrame) -> pd.DataFrame:
    rows = []
    for _, r in plan.iterrows():
        g = r.geometry
        rows.append({
            "district": r["district"],
            "polsby_popper": polsbyPopper(g),
            "reock": reock(g),
            "schwartzberg": schwartzberg(g),
            "convex_hull": convexHullRatio(g),
        })
    return pd.DataFrame(rows)
