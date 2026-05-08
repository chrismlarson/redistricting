import pandas as pd


def computeCompetitiveness(district_df: pd.DataFrame) -> dict:
    share = district_df["dem_share"].dropna()
    band_45_55 = ((share >= 0.45) & (share <= 0.55)).sum()
    band_47_53 = ((share >= 0.47) & (share <= 0.53)).sum()
    return {
        "districts_in_45_55_band": int(band_45_55),
        "districts_in_47_53_band": int(band_47_53),
        "total_districts": int(len(share)),
    }
