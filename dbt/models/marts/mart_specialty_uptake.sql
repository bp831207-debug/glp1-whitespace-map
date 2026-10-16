-- Which specialties drive GLP-1 uptake?
select
    data_year,
    prescriber_type,
    count(*)                                   as prescribers,
    sum(diabetes_claims)                       as diabetes_claims,
    sum(glp1_claims)                           as glp1_claims,
    sum(glp1_claims) / nullif(sum(diabetes_claims), 0) as glp1_share,
    sum(glp1_claims) / sum(sum(glp1_claims)) over (partition by data_year) as share_of_all_glp1_claims
from {{ ref('int_prescriber_year') }}
group by data_year, prescriber_type
