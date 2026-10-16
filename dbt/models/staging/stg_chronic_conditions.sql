-- Diabetes prevalence among Medicare FFS beneficiaries, all ages / all demographics
with src as (
    select
        cast(data_year as integer)                as data_year,
        lpad(bene_geo_cd, 5, '0')                 as county_fips,
        {{ to_num('prvlnc') }}                    as prevalence_raw
    from {{ source('raw', 'chronic_conditions') }}
    where lower(bene_geo_lvl) = 'county'
      and lower(bene_cond) = 'diabetes'
      and lower(bene_age_lvl) = 'all'
      and lower(bene_demo_lvl) = 'all'
)
select
    data_year,
    county_fips,
    case when prevalence_raw > 1 then prevalence_raw / 100 else prevalence_raw end as diabetes_prevalence
from src
