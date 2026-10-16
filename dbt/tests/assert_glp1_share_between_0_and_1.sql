select * from {{ ref('int_prescriber_year') }}
where glp1_share < 0 or glp1_share > 1
