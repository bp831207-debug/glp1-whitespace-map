-- One row per prescriber-year: diabetes volume and GLP-1 adoption
select
    d.data_year,
    d.npi,
    any_value(d.prescriber_type)                                   as prescriber_type,
    any_value(d.prescriber_state)                                  as prescriber_state,
    coalesce(any_value(g.county_fips), 'UNMAPPED')                 as county_fips,
    sum(d.total_claims)                                            as diabetes_claims,
    sum(case when d.is_glp1 then d.total_claims else 0 end)        as glp1_claims,
    sum(case when d.is_glp1 then coalesce(d.total_benes, 0) else 0 end) as glp1_benes,
    sum(case when d.is_glp1 then d.total_drug_cost else 0 end)     as glp1_cost,
    sum(case when d.is_glp1 then d.total_claims else 0 end)
        / nullif(sum(d.total_claims), 0)                           as glp1_share
from {{ ref('int_drug_classified') }} d
left join {{ ref('int_prescriber_geo') }} g using (data_year, npi)
where d.drug_class <> 'Unclassified'
group by d.data_year, d.npi
