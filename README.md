# GLP-1 White-Space Map

**Where is the gap between diabetes burden and GLP-1 use in Medicare, and which prescribers should a brand team call on first?**

An end-to-end commercial-analytics project on free public data (CMS Medicare Part D, CDC PLACES, CMS enrollment and chronic-condition files). It's built with Python, DuckDB, dbt and Power BI.

> Status: 🚧 in progress. This is a 2-week build; see [`docs/project_plan_2weeks.md`](docs/project_plan_2weeks.md).

## Business problem
A GLP-1 brand team has a limited field-force and marketing budget. It needs to know:

1. Which states and counties have the biggest gap between diabetes/obesity burden and GLP-1 use?
2. How is GLP-1 use growing by year, molecule and brand (Ozempic vs Mounjaro vs Trulicity)?
3. Which specialties drive uptake: endocrinology, primary care, or NPs/PAs?
4. Which prescribers have high potential but low adoption? That's the target list.
5. Where should the brand prepare for new obesity demand from the Medicare GLP-1 Bridge (started July 1, 2026)?

## Approach
```
CMS / CDC / Census files ──► ingest/ (Python + DuckDB, filtered to diabetes drugs)
                         ──► dbt staging   (rename, type, suppression flags)
                         ──► dbt intermediate (drug classes, prescriber → ZIP → county)
                         ──► dbt marts     (brand_trends, county_opportunity, hcp_segments)
                         ──► Power BI dashboard + brand-team memo
```

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Option A: run the whole pipeline on synthetic sample data (about 10 seconds, no downloads)
make sample

# Option B: real data (several GB streamed from CMS, filtered on the fly)
make ingest        # downloads to data/glp1.duckdb (raw schema)
make build         # dbt seed + run + test
```

## Data sources
| Source | Use |
|---|---|
| CMS Part D Prescribers by Provider and Drug (2019–2024) | Claims, fills, cost and beneficiaries per prescriber × drug |
| CMS Part D Prescribers by Provider | Prescriber ZIP code |
| CMS Medicare Monthly Enrollment | Part D enrollees per county (denominator) |
| CMS Specific Chronic Conditions | Diabetes prevalence among Medicare FFS beneficiaries, by county |
| CDC PLACES County Data (2025 release) | Diagnosed diabetes and obesity among all adults |
| Census 2020 ZCTA-to-county relationship file | ZIP → county |

## Key metrics
See [`docs/business_rules.md`](docs/business_rules.md).
- **Uptake:** GLP-1 claims per 1,000 Part D enrollees
- **Penetration:** GLP-1 beneficiaries ÷ estimated diabetic Part D beneficiaries
- **White-space gap:** (top-quartile benchmark − county penetration) × diabetic beneficiaries, i.e. patients who could be on a GLP-1 but aren't
- **HCP segments:** Untapped / Champions / Emerging / Deprioritize, based on diabetes volume × GLP-1 share

## Findings
_To be added in Week 2._

## Limitations
- Medicare Part D only, so mostly people aged 65+. This isn't an all-payer view like IQVIA data.
- Prescriber location is used as a stand-in for patient location.
- PLACES numbers are model-based estimates for all adults, not just Medicare members.
- CMS suppresses counts under 11, so rural counties and low-volume prescribers are undercounted.
- GLP-1 Bridge prescriptions are paid outside Part D, so they won't appear in this data.
- Part D can't separate diabetes use from obesity use; brand is only a rough proxy.
- ZIP is treated as ZCTA. Each ZIP is assigned to the county with the most land area.

## Repo structure
```
├── ingest/            download + load scripts (no raw data committed)
├── scripts/           synthetic sample data generator
├── dbt/               staging → intermediate → marts, seeds, tests
├── analysis/          notebooks: scoring and sensitivity checks
├── dashboard/         .pbix + PNG exports
└── docs/              charter, plan, business rules, data dictionary, memo
```
