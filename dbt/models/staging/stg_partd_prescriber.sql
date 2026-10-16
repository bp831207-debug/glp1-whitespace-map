select
    cast(data_year as integer)                    as data_year,
    prscrbr_npi                                   as npi,
    lpad(left(trim(prscrbr_zip5), 5), 5, '0')     as zip5,
    prscrbr_state_abrvtn                          as prescriber_state,
    prscrbr_type                                  as prescriber_type,
    {{ to_num('tot_clms') }}                      as total_claims_all_drugs,
    data_year || '-' || prscrbr_npi               as row_key
from {{ source('raw', 'partd_prescriber') }}
