-- 2×2 prescriber segmentation for the latest year: diabetes volume (potential) × GLP-1 share (adoption)
with eligible as (
    select *
    from {{ ref('int_prescriber_year') }}
    where data_year = {{ var('latest_year') }}
      and diabetes_claims >= {{ var('hcp_min_diabetes_claims') }}
),
cuts as (
    select
        quantile_cont(diabetes_claims, {{ var('hcp_volume_percentile') }}) as volume_cut,
        quantile_cont(glp1_share, {{ var('hcp_share_percentile') }})       as share_cut
    from eligible
)
select
    e.*,
    c.volume_cut,
    c.share_cut,
    case
        when e.diabetes_claims >= c.volume_cut and e.glp1_share <  c.share_cut then 'Untapped'
        when e.diabetes_claims >= c.volume_cut and e.glp1_share >= c.share_cut then 'Champions'
        when e.diabetes_claims <  c.volume_cut and e.glp1_share >= c.share_cut then 'Emerging'
        else 'Deprioritize'
    end as segment,
    -- simple priority for the call list: untapped volume = diabetes claims not on GLP-1
    e.diabetes_claims * (c.share_cut - e.glp1_share) as untapped_claims_score
from eligible e
cross join cuts c
