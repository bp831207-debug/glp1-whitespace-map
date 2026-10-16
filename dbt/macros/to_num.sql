{# Cast a CMS text value to a number; suppressed markers ('', '*', '<11') become NULL. #}
{% macro to_num(col, type='double') -%}
    try_cast(nullif(regexp_replace(trim({{ col }}), '[,$%]', '', 'g'), '') as {{ type }})
{%- endmacro %}
