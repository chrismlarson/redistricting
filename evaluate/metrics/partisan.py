"""Partisan-fairness metrics.

Re-implemented locally rather than calling gerrychain.metrics so we don't
have to construct a gerrychain Partition. Formulas match
gerrychain/metrics/partisan.py and the standard literature.
"""
from math import atan, pi

import numpy as np
import pandas as pd
from scipy import stats


def _shares(district_df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    d = district_df["dem_votes"].to_numpy(dtype=float)
    r = district_df["rep_votes"].to_numpy(dtype=float)
    total = d + r
    with np.errstate(divide="ignore", invalid="ignore"):
        dem_share = np.where(total > 0, d / total, np.nan)
    return d, r, dem_share


def efficiencyGap(district_df: pd.DataFrame) -> float:
    """(wasted_D - wasted_R) / total_votes. Positive => pro-R (PlanScore convention)."""
    d, r, _ = _shares(district_df)
    total_per_dist = d + r
    threshold = total_per_dist / 2

    dem_won = d > r
    wasted_d = np.where(dem_won, d - threshold, d)
    wasted_r = np.where(dem_won, r, r - threshold)
    total_votes = total_per_dist.sum()
    if total_votes == 0:
        return float("nan")
    return float((wasted_d.sum() - wasted_r.sum()) / total_votes)


def meanMedianDifference(district_df: pd.DataFrame) -> float:
    """median(D share) - mean(D share). Positive => pro-D advantage in median seat."""
    _, _, share = _shares(district_df)
    share = share[~np.isnan(share)]
    if len(share) == 0:
        return float("nan")
    return float(np.median(share) - np.mean(share))


def partisanBias(district_df: pd.DataFrame) -> float:
    """Symmetry around 50%: shift every district's D share so statewide mean = 0.5,
    then compute (D seat share at shifted - 0.5). Positive => pro-D bias.
    """
    _, _, share = _shares(district_df)
    share = share[~np.isnan(share)]
    n = len(share)
    if n == 0:
        return float("nan")
    shift = 0.5 - share.mean()
    shifted = share + shift
    seats_dem = (shifted > 0.5).sum()
    return float(seats_dem / n - 0.5)


def declination(district_df: pd.DataFrame) -> float:
    """Warrington 2018 declination. |delta| > 0.3 is concerning.

    Returns NaN if either party wins zero districts (declination is undefined).
    """
    _, _, share = _shares(district_df)
    share = np.sort(share[~np.isnan(share)])
    n = len(share)
    if n == 0:
        return float("nan")
    dem_wins = share[share > 0.5]
    rep_wins = share[share <= 0.5]
    if len(dem_wins) == 0 or len(rep_wins) == 0:
        return float("nan")

    mean_dem = dem_wins.mean()
    mean_rep = rep_wins.mean()
    frac_rep = len(rep_wins) / n
    frac_dem = len(dem_wins) / n

    theta_rep = atan((0.5 - mean_rep) / frac_rep)
    theta_dem = atan((mean_dem - 0.5) / frac_dem)
    return float(2 * (theta_dem - theta_rep) / pi)


def lopsidedMargins(district_df: pd.DataFrame) -> dict:
    """Welch's t-test on D win-margins vs R win-margins. Significant p =>
    one party wastes votes more than the other (sign of packing)."""
    d, r, share = _shares(district_df)
    valid = ~np.isnan(share)
    share = share[valid]
    dem_margins = share[share > 0.5] - 0.5
    rep_margins = 0.5 - share[share <= 0.5]
    if len(dem_margins) < 2 or len(rep_margins) < 2:
        return {"dem_mean_margin": float(dem_margins.mean()) if len(dem_margins) else float("nan"),
                "rep_mean_margin": float(rep_margins.mean()) if len(rep_margins) else float("nan"),
                "t_stat": float("nan"), "p_value": float("nan")}
    t, p = stats.ttest_ind(dem_margins, rep_margins, equal_var=False)
    return {
        "dem_mean_margin": float(dem_margins.mean()),
        "rep_mean_margin": float(rep_margins.mean()),
        "t_stat": float(t),
        "p_value": float(p),
    }


def computePartisan(district_df: pd.DataFrame) -> dict:
    return {
        "efficiency_gap": efficiencyGap(district_df),
        "mean_median": meanMedianDifference(district_df),
        "partisan_bias": partisanBias(district_df),
        "declination": declination(district_df),
        "lopsided_margins": lopsidedMargins(district_df),
    }
