-- Prescriber-year → ZIP → county
select
    p.data_year,
    p.npi,
    p.zip5,
    p.prescriber_state,
    p.prescriber_type,
    coalesce(z.county_fips, 'UNMAPPED') as county_fips,
    z.county_fips is not null           as is_county_mapped
from {{ ref('stg_partd_prescriber') }} p
left join {{ ref('stg_zcta_county') }} z using (zip5)
