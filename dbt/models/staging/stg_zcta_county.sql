-- One county per ZCTA: the county holding the largest share of the ZCTA's land area
select
    geoid_zcta5_20                                as zip5,
    geoid_county_20                               as county_fips
from {{ source('raw', 'zcta_county') }}
where geoid_zcta5_20 is not null and geoid_zcta5_20 <> ''
qualify row_number() over (
    partition by geoid_zcta5_20
    order by {{ to_num('arealand_part', 'bigint') }} desc nulls last
) = 1
