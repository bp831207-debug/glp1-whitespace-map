select * from {{ ref('mart_county_opportunity') }}
where penetration < 0 or penetration > 1
