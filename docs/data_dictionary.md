# Data Dictionary

_Fill in on Day 3–4 after loading real files: row counts, years, key columns, null %._

| Raw table | Source | Grain | Rows (by year) | Key columns | Notes |
|---|---|---|---|---|---|
| raw.partd_prescriber_drug | CMS Part D by Provider and Drug | NPI × drug × year | | prscrbr_npi, gnrc_name, brnd_name, tot_clms, tot_benes | Filtered to diabetes drugs at ingest |
| raw.partd_prescriber | CMS Part D by Provider | NPI × year | | prscrbr_npi, prscrbr_zip5, prscrbr_type | |
| raw.medicare_enrollment | CMS Monthly Enrollment | geo × month × year | | bene_fips_cd, prscrptn_drug_tot_benes | Annual rows have month = 'Year' |
| raw.chronic_conditions | CMS Specific Chronic Conditions | geo × condition × year | | bene_geo_cd, bene_cond, prvlnc | |
| raw.places_county | CDC PLACES 2025 | county × measure | | locationid, measureid, data_value | DIABETES, OBESITY only |
| raw.zcta_county | Census 2020 relationship file | ZCTA × county | | geoid_zcta5_20, geoid_county_20, arealand_part | |
