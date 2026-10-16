# 2-Week Project Plan

Ten working days, about 3–4 focused hours a day. Each day ends with a commit.

## Week 1: Data foundation and metrics

| Day | Focus | Tasks | Done when |
|---|---|---|---|
| 1 | Setup ✅ | Repo, charter, folder structure, requirements, CI, synthetic data run | `make sample` passes locally and in GitHub Actions |
| 2 | Ingest Part D | Run `ingest/download_partd.py` for 2022–2024 first, then backfill 2019–2021 | `raw.partd_prescriber_drug` and `raw.partd_prescriber` exist with row counts logged |
| 3 | Ingest denominators | Enrollment, chronic conditions, PLACES, ZCTA→county | All 6 raw tables loaded; `docs/data_dictionary.md` filled in |
| 4 | Profile and stage | Row counts by year, nulls, suppressed share; fix staging column names against the real files | dbt staging models build; profiling notes in `analysis/01_profiling.ipynb` |
| 5 | Business rules | Check the drug-class seed against the real generic names (list unmatched names); build the prescriber → county mapping | `int_drug_classified` has 0 unmatched diabetes drugs; county match rate reported |

**Week 1 checkpoint:** brand-trend mart working, so you can already answer "how fast is GLP-1 growing, and which molecule is winning?"

## Week 2: Opportunity, targeting and storytelling

| Day | Focus | Tasks | Done when |
|---|---|---|---|
| 6 | County white space | Tune the penetration benchmark (P75), gap, tiers, Bridge-readiness flag | `mart_county_opportunity` passes tests; top-20 counties look plausible |
| 7 | HCP targeting | 2×2 segmentation and specialty roll-up; sensitivity check on thresholds | `mart_hcp_segments` and a target list CSV exported |
| 8 | Power BI, part 1 | Pages: Executive summary, White-space map, Brand trends | 3 pages built on parquet exports |
| 9 | Power BI, part 2 and validation | Pages: Prescriber targeting, Data quality; reconcile national totals against CMS published figures | `docs/validation_report.md` written |
| 10 | Storytelling | Brand-team memo, README findings and screenshots, resume bullets, LinkedIn post | Repo is portfolio-ready |

## Cut-list (if you fall behind)
1. Use 2022–2024 only instead of 2019–2024.
2. Skip the PLACES/Bridge-readiness flag.
3. Use 3 dashboard pages instead of 5.

## Stretch (after Day 10)
- Run the dbt models on a Snowflake free trial
- K-means prescriber clusters as an alternative to the 2×2
- 5-slide insights deck
