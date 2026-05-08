import pandas as pd

from evaluate.planSpec import PlanSpec


def computePopulationDeviation(district_df: pd.DataFrame, spec: PlanSpec) -> dict:
    """Returns max deviation as a fraction of ideal population, plus per-district details."""
    pops = district_df["pop"].astype(float)
    if pops.isna().all() or pops.sum() == 0:
        return {
            "available": False,
            "reason": "Population column not present in precinct data",
            "per_district": [],
        }
    total_pop = pops.sum()
    ideal = total_pop / spec.seat_count if spec.seat_count else float("nan")

    deviations = (pops - ideal) / ideal if ideal else pops * 0
    max_abs_dev = deviations.abs().max()

    return {
        "available": True,
        "total_population": float(total_pop),
        "ideal_population": float(ideal),
        "max_abs_deviation": float(max_abs_dev),
        "threshold": spec.population_deviation_threshold,
        "exceeds_threshold": bool(max_abs_dev > spec.population_deviation_threshold),
        "per_district": district_df.assign(
            pop_deviation=deviations.values
        )[["district", "pop", "pop_deviation"]].to_dict(orient="records"),
    }
