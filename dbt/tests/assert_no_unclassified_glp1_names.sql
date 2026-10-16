-- Every row kept at ingest should map to a drug class; review anything listed here
{{ config(severity='warn') }}
select distinct generic_name from {{ ref('int_drug_classified') }}
where drug_class = 'Unclassified'
