import argparse
import importlib.util
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from evaluate.loadCounties import loadCounties
from evaluate.loadDistrictPlan import loadDistrictPlan
from evaluate.loadPrecinctVotes import (
    aggregateByDistrict,
    assignPrecinctsToDistricts,
    loadPrecinctVotes,
)
from evaluate.metrics.compactness import computeCompactness
from evaluate.metrics.competitiveness import computeCompetitiveness
from evaluate.metrics.partisan import computePartisan
from evaluate.metrics.population import computePopulationDeviation
from evaluate.metrics.splits import computeCountySplits
from evaluate.planSpec import PlanSpec


def loadSpec(spec_path: Path) -> PlanSpec:
    spec_module_spec = importlib.util.spec_from_file_location("plan_spec_module", spec_path)
    if spec_module_spec is None or spec_module_spec.loader is None:
        raise ImportError(f"Could not import spec from {spec_path}")
    module = importlib.util.module_from_spec(spec_module_spec)
    spec_module_spec.loader.exec_module(module)
    if not hasattr(module, "SPEC"):
        raise AttributeError(f"{spec_path} must define a top-level SPEC = PlanSpec(...)")
    return module.SPEC


def runSanityChecks(precincts, district_df: pd.DataFrame, plan):
    issues = []
    if district_df["pop"].notna().any():
        pop_total = district_df["pop"].sum()
        if pop_total <= 0:
            issues.append("Total population from precincts is zero")

    precinct_total = precincts[["dem_votes", "rep_votes"]].sum(axis=1)
    if (precinct_total < 0).any():
        issues.append("Negative D+R precinct totals encountered")

    pp_oob = []
    from evaluate.metrics.compactness import polsbyPopper
    for _, row in plan.iterrows():
        pp = polsbyPopper(row.geometry)
        if not (0 <= pp <= 1):
            pp_oob.append((row["district"], pp))
    if pp_oob:
        issues.append(f"Polsby-Popper out of [0,1]: {pp_oob}")

    return issues


def writeReport(spec: PlanSpec, plan, district_df, compactness_df, results: dict, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append(f"# Fairness evaluation: {spec.name}")
    lines.append("")
    lines.append(f"- State: {spec.state_abbr} (FIPS {spec.state_fips})")
    lines.append(f"- Chamber: {spec.chamber}")
    lines.append(f"- Seats: {spec.seat_count}")
    if spec.notes:
        lines.append(f"- Notes: {spec.notes}")
    lines.append("")

    lines.append("## Population")
    pop = results["population"]
    if pop.get("available"):
        lines.append(f"- Total population: {pop['total_population']:,.0f}")
        lines.append(f"- Ideal per district: {pop['ideal_population']:,.0f}")
        lines.append(f"- Max |deviation|: {pop['max_abs_deviation']*100:.3f}% (threshold {pop['threshold']*100:.1f}%)")
        lines.append(f"- Exceeds threshold: **{pop['exceeds_threshold']}**")
    else:
        lines.append(f"- Not computed: {pop.get('reason', 'unknown')}")
    lines.append("")

    lines.append("## Compactness")
    lines.append("")
    lines.append("| District | Polsby-Popper | Reock | Schwartzberg | Convex Hull |")
    lines.append("|---|---|---|---|---|")
    for _, r in compactness_df.iterrows():
        lines.append(
            f"| {r['district']} | {r['polsby_popper']:.3f} | {r['reock']:.3f} | "
            f"{r['schwartzberg']:.3f} | {r['convex_hull']:.3f} |"
        )
    means = compactness_df[["polsby_popper", "reock", "schwartzberg", "convex_hull"]].mean()
    mins = compactness_df[["polsby_popper", "reock", "schwartzberg", "convex_hull"]].min()
    lines.append(f"| **mean** | {means['polsby_popper']:.3f} | {means['reock']:.3f} | {means['schwartzberg']:.3f} | {means['convex_hull']:.3f} |")
    lines.append(f"| **min**  | {mins['polsby_popper']:.3f} | {mins['reock']:.3f} | {mins['schwartzberg']:.3f} | {mins['convex_hull']:.3f} |")
    lines.append("")
    lines.append("Interpretation: Polsby-Popper >0.30 typical, Reock >0.40 acceptable, Convex Hull >0.60 acceptable. Lower = less compact.")
    lines.append("")

    lines.append("## Partisan symmetry (2020 presidential, two-party)")
    p = results["partisan"]
    lines.append(f"- **Efficiency gap**: {p['efficiency_gap']*100:+.2f}% (positive => pro-R; |EG| > 7% presumptive gerrymander)")
    lines.append(f"- **Mean-median**: {p['mean_median']*100:+.2f}% (positive => pro-D in median seat; |MM| > 2-3% suggestive)")
    lines.append(f"- **Partisan bias**: {p['partisan_bias']*100:+.2f}% (positive => pro-D)")
    lines.append(f"- **Declination**: {p['declination']:+.3f} ( |δ| > 0.3 concerning )")
    lm = p["lopsided_margins"]
    lines.append(f"- **Lopsided margins**: D mean win margin {lm['dem_mean_margin']*100:.2f}%, R mean win margin {lm['rep_mean_margin']*100:.2f}%, t={lm['t_stat']:.2f}, p={lm['p_value']:.3f}")
    lines.append("")

    lines.append("## Competitiveness")
    c = results["competitiveness"]
    lines.append(f"- Districts with D share in [45%, 55%]: **{c['districts_in_45_55_band']} / {c['total_districts']}**")
    lines.append(f"- Districts with D share in [47%, 53%]: {c['districts_in_47_53_band']} / {c['total_districts']}")
    lines.append("")

    lines.append("## County splits")
    s = results["splits"]
    lines.append(f"- Counties split across districts: **{s['split_county_count']} / {s['total_counties']}**")
    lines.append(f"- Max times any single county is split: {s['max_splits_in_one_county']}")
    if s["split_county_detail"]:
        lines.append("")
        lines.append("| County | Districts touched |")
        lines.append("|---|---|")
        for county, n in s["split_county_detail"].items():
            lines.append(f"| {county} | {n} |")
    lines.append("")

    lines.append("## Per-district detail")
    lines.append("")
    lines.append("| District | Population | Pop dev | Dem votes | Rep votes | Dem share |")
    lines.append("|---|---|---|---|---|---|")
    pop_lookup = {row["district"]: row["pop_deviation"] for row in pop.get("per_district", [])}
    for _, r in district_df.iterrows():
        dev = pop_lookup.get(r["district"], float("nan"))
        share = r["dem_share"]
        share_str = f"{share*100:.1f}%" if pd.notna(share) else "n/a"
        pop_str = f"{r['pop']:,.0f}" if pd.notna(r['pop']) else "n/a"
        dev_str = f"{dev*100:+.2f}%" if pd.notna(dev) else "n/a"
        lines.append(
            f"| {r['district']} | {pop_str} | {dev_str} | "
            f"{r['dem_votes']:,.0f} | {r['rep_votes']:,.0f} | {share_str} |"
        )
    lines.append("")

    if results["sanity_issues"]:
        lines.append("## Sanity check warnings")
        for issue in results["sanity_issues"]:
            lines.append(f"- {issue}")
        lines.append("")

    lines.append("## Out of scope for this report")
    lines.append("- MCMC ensemble outlier comparison (scalar metrics only).")
    lines.append("- VRA / minority cracking — VEST 2020 has no race columns; would require CVAP block disaggregation.")
    lines.append("- Election cycles other than 2020 presidential.")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote report: {out_path}")


def writeFigures(plan, district_df, compactness_df, out_dir: Path, name: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    plan_with_pp = plan.merge(compactness_df[["district", "polsby_popper"]], on="district")
    plan_with_share = plan.merge(district_df[["district", "dem_share"]], on="district")

    fig, ax = plt.subplots(figsize=(10, 7))
    plan_with_pp.plot(column="polsby_popper", cmap="viridis", legend=True, edgecolor="black", ax=ax)
    ax.set_title(f"{name} — Polsby-Popper compactness")
    ax.set_axis_off()
    fig.savefig(out_dir / f"{name}_compactness.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 7))
    plan_with_share.plot(column="dem_share", cmap="RdBu", vmin=0.2, vmax=0.8, legend=True, edgecolor="black", ax=ax)
    ax.set_title(f"{name} — 2020 presidential D vote share")
    ax.set_axis_off()
    fig.savefig(out_dir / f"{name}_dem_share.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Evaluate a district map for fairness metrics.")
    ap.add_argument("--spec", required=True, type=Path, help="Path to a Python file defining SPEC = PlanSpec(...)")
    ap.add_argument("--out", type=Path, default=None, help="Output markdown path (default: reports/<spec name>.md)")
    ap.add_argument("--no-figures", action="store_true", help="Skip matplotlib figure generation")
    args = ap.parse_args(argv)

    spec = loadSpec(args.spec)
    out_path = args.out or spec.report_path()

    print(f"Loading plan: {spec.plan_path}")
    plan = loadDistrictPlan(spec)
    print(f"  {len(plan)} districts loaded")

    print(f"Loading precincts: {spec.precinct_path}")
    precincts = loadPrecinctVotes(spec)
    print(f"  {len(precincts)} precincts loaded")

    print("Assigning precincts to districts...")
    precincts_d = assignPrecinctsToDistricts(precincts, plan)
    district_df = aggregateByDistrict(precincts_d)

    print("Computing compactness...")
    compactness_df = computeCompactness(plan)

    print("Loading counties...")
    counties = loadCounties(spec)
    print(f"  {len(counties)} counties loaded")

    print("Computing metrics...")
    results = {
        "population": computePopulationDeviation(district_df, spec),
        "partisan": computePartisan(district_df),
        "competitiveness": computeCompetitiveness(district_df),
        "splits": computeCountySplits(plan, counties),
        "sanity_issues": runSanityChecks(precincts, district_df, plan),
    }

    if not args.no_figures:
        print("Writing figures...")
        writeFigures(plan, district_df, compactness_df, out_path.parent, spec.name)

    writeReport(spec, plan, district_df, compactness_df, results, out_path)


if __name__ == "__main__":
    sys.exit(main())
