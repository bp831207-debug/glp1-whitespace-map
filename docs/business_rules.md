# Business Rules (draft: confirm against real data on Day 5)

## Drug classification
The source of truth is `dbt/seeds/drug_class_map.csv`. Generic names (`Gnrc_Name`) are matched by case-insensitive substring. When a name matches several patterns (combination products), the **lowest `priority`** wins.

| Class | Molecules | Notes |
|---|---|---|
| GLP-1 RA | semaglutide, tirzepatide*, dulaglutide, liraglutide, exenatide, lixisenatide | *tirzepatide is a dual GIP/GLP-1 agonist and is grouped with GLP-1s. Combos with insulin (Xultophy, Soliqua) count as GLP-1. |
| SGLT2 | empagliflozin, dapagliflozin, canagliflozin, ertugliflozin, bexagliflozin | SGLT2/metformin combos → SGLT2 |
| DPP-4 | sitagliptin, saxagliptin, linagliptin, alogliptin | |
| Metformin | metformin | |
| Sulfonylurea | glipizide, glimepiride, glyburide | |
| TZD | pioglitazone | |
| Insulin | insulin* | |

Brands are taken directly from `Brnd_Name` (Ozempic, Rybelsus and Wegovy are all semaglutide).

## Geography
- Prescriber ZIP (`Prscrbr_zip5`, by-Provider file) → ZCTA → county. Each ZCTA goes to the county holding the largest share of its land area.
- Prescribers with no county match are kept and reported as "Unmapped".

## Metrics
| Metric | Definition | Grain |
|---|---|---|
| GLP-1 claims per 1,000 | GLP-1 `Tot_Clms` ÷ Part D enrollees × 1,000 | county-year |
| Est. diabetic beneficiaries | Part D enrollees × CMS diabetes prevalence | county-year |
| GLP-1 beneficiaries | Σ GLP-1 `Tot_Benes` across prescribers (may double-count patients seen by 2+ prescribers; suppressed values = 0) | county-year |
| Penetration | min(GLP-1 beneficiaries ÷ est. diabetic beneficiaries, 1) | county-year |
| Benchmark | 75th percentile of county penetration (counties with ≥ 500 enrollees) | year |
| White-space gap | max(benchmark − penetration, 0) × est. diabetic beneficiaries | county-year |
| Opportunity tier | High = top third of gap, Medium = middle third, Low = bottom third | county-year |
| Bridge-readiness | PLACES obesity ≥ national P75 **and** penetration ≤ national median | county |
| HCP diabetes volume | Σ `Tot_Clms` across all diabetes classes | NPI-year |
| HCP GLP-1 share | GLP-1 claims ÷ diabetes claims | NPI-year |

## HCP segmentation (latest year; prescribers with ≥ 50 diabetes claims)
| Segment | Diabetes volume | GLP-1 share |
|---|---|---|
| Untapped (target) | ≥ P75 | < median |
| Champions (maintain) | ≥ P75 | ≥ median |
| Emerging (nurture) | < P75 | ≥ median |
| Deprioritize | < P75 | < median |

Thresholds are dbt vars in `dbt/dbt_project.yml`, so they can be tuned in sensitivity checks.

## Suppression
CMS blanks values when fewer than 11 beneficiaries or claims are involved. `Tot_Benes` nulls are treated as 0 in sums and flagged with `is_bene_suppressed`.
