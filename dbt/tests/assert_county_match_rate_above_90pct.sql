-- Success criterion from the charter: at least 90% of GLP-1 claims map to a county
{{ config(severity='warn') }}
select data_year,
       sum(glp1_claims) filter (where county_fips <> 'UNMAPPED') / nullif(sum(glp1_claims), 0) as match_rate
from {{ ref('int_prescriber_year') }}
group by data_year
having match_rate < 0.90
