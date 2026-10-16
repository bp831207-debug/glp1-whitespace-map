select
    cast(data_year as integer)                    as data_year,
    prscrbr_npi                                   as npi,
    prscrbr_type                                  as prescriber_type,
    prscrbr_state_abrvtn                          as prescriber_state,
    trim(gnrc_name)                               as generic_name,
    trim(brnd_name)                               as brand_name,
    {{ to_num('tot_clms') }}                      as total_claims,
    {{ to_num('tot_30day_fills') }}               as total_30day_fills,
    {{ to_num('tot_drug_cst') }}                  as total_drug_cost,
    {{ to_num('tot_benes') }}                     as total_benes,
    {{ to_num('tot_benes') }} is null             as is_bene_suppressed,
    data_year || '-' || prscrbr_npi || '-' || gnrc_name || '-' || brnd_name as row_key
from {{ source('raw', 'partd_prescriber_drug') }}
