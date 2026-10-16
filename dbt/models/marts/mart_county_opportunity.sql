-- County white-space: how many estimated diabetic Part D patients are "missing" vs the benchmark
with glp1 as (
    select data_year, county_fips,
           sum(glp1_claims) as glp1_claims,
           sum(glp1_benes)  as glp1_benes,
           sum(diabetes_claims) as diabetes_claims,
           count(*) filter (where glp1_claims > 0) as glp1_prescribers
    from {{ ref('int_prescriber_year') }}
    where county_fips <> 'UNMAPPED'
    group by all
),
base as (
    select
        e.data_year,
        e.county_fips,
        e.state,
        e.county_name,
        e.partd_enrollees,
        c.diabetes_prevalence,
        e.partd_enrollees * c.diabetes_prevalence             as est_diabetic_benes,
        coalesce(g.glp1_claims, 0)                            as glp1_claims,
        coalesce(g.glp1_benes, 0)                             as glp1_benes,
        coalesce(g.glp1_prescribers, 0)                       as glp1_prescribers,
        1000.0 * coalesce(g.glp1_claims, 0) / nullif(e.partd_enrollees, 0) as glp1_claims_per_1k,
        least(coalesce(g.glp1_benes, 0) / nullif(e.partd_enrollees * c.diabetes_prevalence, 0), 1) as penetration,
        pl.adult_obesity_prev,
        pl.adult_diabetes_prev
    from {{ ref('stg_medicare_enrollment') }} e
    left join {{ ref('stg_chronic_conditions') }} c using (data_year, county_fips)
    left join glp1 g using (data_year, county_fips)
    left join {{ ref('stg_places_county') }} pl using (county_fips)
),
bench as (
    select
        data_year,
        quantile_cont(penetration, {{ var('benchmark_percentile') }}) as benchmark_penetration,
        quantile_cont(penetration, 0.5)                               as median_penetration,
        quantile_cont(adult_obesity_prev, 0.75)                       as obesity_p75
    from base
    where partd_enrollees >= {{ var('min_county_enrollees') }} and penetration is not null
    group by data_year
),
scored as (
    select
        b.*,
        x.benchmark_penetration,
        greatest(x.benchmark_penetration - b.penetration, 0) * b.est_diabetic_benes as whitespace_gap_patients,
        (b.adult_obesity_prev >= x.obesity_p75 and b.penetration <= x.median_penetration) as is_bridge_ready
    from base b
    join bench x using (data_year)
)
select
    *,
    case ntile(3) over (partition by data_year order by whitespace_gap_patients desc nulls last)
        when 1 then 'High' when 2 then 'Medium' else 'Low' end as opportunity_tier,
    data_year || '-' || county_fips as row_key
from scored
