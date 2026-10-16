-- CDC PLACES crude prevalence among all adults (model-based estimates)
select
    lpad(locationid, 5, '0')                      as county_fips,
    stateabbr                                     as state,
    locationname                                  as county_name,
    cast(year as integer)                         as brfss_year,
    max(case when measureid = 'DIABETES' then {{ to_num('data_value') }} / 100 end) as adult_diabetes_prev,
    max(case when measureid = 'OBESITY'  then {{ to_num('data_value') }} / 100 end) as adult_obesity_prev,
    max({{ to_num('totalpop18plus') }})           as adult_population
from {{ source('raw', 'places_county') }}
where datavaluetypeid = 'CrdPrv'
group by all
