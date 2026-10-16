-- Annual county rows only (CMS publishes month = 'Year' for the annual average)
select
    cast(year as integer)                         as data_year,
    lpad(bene_fips_cd, 5, '0')                    as county_fips,
    bene_state_abrvtn                             as state,
    bene_county_desc                              as county_name,
    {{ to_num('tot_benes') }}                     as medicare_benes,
    {{ to_num('prscrptn_drug_tot_benes') }}       as partd_enrollees
from {{ source('raw', 'medicare_enrollment') }}
where lower(bene_geo_lvl) = 'county'
  and lower(month) = 'year'
