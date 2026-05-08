# Prompt for chrislarson.com Claude Code workspace

Paste the section below into a fresh Claude Code session running in the
chrislarson.com repo. It briefs the agent cold, points it at this repo as
a read-only source of truth, and asks for a plan before any code.

---

I want to publish redistricting-fairness analysis on my personal site, **chrislarson.com**. The analysis already exists as a Python tool elsewhere on this machine — I want you to plan how to bring either the code or just the rendered results onto the site. **Don't start coding yet — produce a plan first.**

## Source of truth (read-only for this work)

`C:\Users\ChrisLocal\source\clauderedistricting\redistricting\evaluate\`

A self-contained Python package that scores any US state's district map on standard fairness metrics. State- and chamber-agnostic. Skim before planning:

- `evaluate/metrics/` — pure functions, one file per metric family (compactness, partisan, splits, competitiveness, population)
- `evaluate/report.py` — CLI orchestrator: takes a `PlanSpec`, emits a markdown report + 2 PNG choropleths (Polsby-Popper + D-share)
- `evaluate/planSpec.py` — the dataclass that defines a single map evaluation
- `evaluate/parsers/tn_sa7001.py` — example state-specific ingestion (parses Tennessee's 101-page bill PDF into a block-equivalency CSV)
- `reports/tn_2026_congressional.md` and the two PNGs alongside it — already-generated artifacts for the first case study

## Case study driving this

Tennessee's mid-decade redistricting (proposed 2026-05-06, GOP-led). Headline numbers from the run:

- Efficiency gap **+26%** (~4× the 7% Stephanopoulos & McGhee 2015 academic threshold; no federal *legal* threshold post-*Rucho v. Common Cause* 2019)
- **0 of 9** districts competitive (D share in 45–55%)
- District 5 Polsby-Popper **0.083** — visibly a tendril reaching across the state
- Davidson (Nashville) and Shelby (Memphis) each split three ways
- Declination undefined because every district was Trump-carried in 2020

The site should host (a) this case study and (b) the methodology — what each metric means, how it's computed, what its known limitations are. The methodology page is probably more durable value than any single case study.

## Decisions to surface, not decide unilaterally

1. **Stack fit.** Audit chrislarson.com first — framework, content model, deploy target. Match existing patterns.
2. **Static vs. dynamic.** I lean static: pre-render in Python, commit a JSON+PNG bundle per evaluated map, render via the site's normal templating. Avoids a Python backend. Push back if you see a reason to do otherwise.
3. **Code vs. output.** Three options on a spectrum:
   - (a) Run the Python eval out-of-band; ship only JSON+PNGs to chrislarson.com; methodology page links to the source repo.
   - (b) Vendor just the metric formulas into chrislarson.com so the analysis is reproducible from the site repo.
   - (c) Treat the source repo as a peer dependency.

   I lean (a). Tell me if you'd choose differently.
4. **Data contract.** Design the JSON shape for one evaluated map: top-level metrics, per-district detail, image paths, prose interpretation, source links. Optimize for "adding a second state later is content-only".
5. **Interactivity for V1?** Only if the site already has a culture of it. Static images are honest about underlying VTD-level approximations in the analysis.

## Constraints

- Don't change site nav structure or break existing pages.
- Read a few existing pages and match the writing voice.
- Don't ship copyrighted source material; link to canonical sources (TN bill PDF, VEST data on Harvard Dataverse, TIGER shapefiles).
- Wide map images need mobile-responsive treatment.
- Adding a second state later should be content-only, not a code change.
- Be precise about *Rucho* and *Gill v. Whitford* if you discuss legal context — there's no federal legal threshold for partisan gerrymandering, only academic thresholds and varying state-court doctrines.

## What I want back, before any code

1. Audit of chrislarson.com (stack, content model, deploy).
2. Proposed architecture for the redistricting section.
3. JSON data contract for an evaluated map.
4. Page outline for the TN case study.
5. Page outline for the methodology page.
6. Open questions for me — use AskUserQuestion when you have decisions to surface.
