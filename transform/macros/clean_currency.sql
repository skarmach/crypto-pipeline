{% macro clean_currency(column_name, decimal_places=2) %}
    case
        when {{ column_name }} <= 0 then null
        else round(cast({{ column_name }} as numeric), {{ decimal_places }})
    end
{% endmacro %}
