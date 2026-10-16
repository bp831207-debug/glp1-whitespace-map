-- National GLP-1 trend by year × molecule × brand, with share and YoY growth
with base as (
    select
        data_year,
        molecule,
        brand_name,
        sum(total_claims)     as claims,
        sum(total_30day_fills) as fills_30day,
        sum(total_drug_cost)  as drug_cost,
        sum(coalesce(total_benes, 0)) as benes_sum,
        count(distinct npi)   as prescribers
    from {{ ref('int_drug_classified') }}
    where is_glp1
    group by all
)
select
    *,
    claims / sum(claims) over (partition by data_year) as glp1_claim_share,
    claims / nullif(lag(claims) over (partition by molecule, brand_name order by data_year), 0) - 1 as claims_yoy_growth,
    data_year || '-' || molecule || '-' || brand_name   as row_key
from base
