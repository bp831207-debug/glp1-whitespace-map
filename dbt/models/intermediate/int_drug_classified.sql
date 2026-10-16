-- Attach a drug class to every Part D row. Combination products match several
-- patterns; the lowest priority wins (GLP-1 > SGLT2 > DPP-4 > insulin > ... > metformin).
with matches as (
    select
        d.*,
        m.drug_class,
        m.molecule,
        m.is_glp1,
        row_number() over (partition by d.row_key order by m.priority) as rn
    from {{ ref('stg_partd_prescriber_drug') }} d
    left join {{ ref('drug_class_map') }} m
        on lower(d.generic_name) like '%' || m.pattern || '%'
)
select
    * exclude (rn, drug_class, molecule, is_glp1),
    coalesce(drug_class, 'Unclassified') as drug_class,
    molecule,
    coalesce(is_glp1, false)             as is_glp1
from matches
where rn = 1
