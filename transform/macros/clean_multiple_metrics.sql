{% macro clean_multiple_metrics(column_list, decimal_places=2) %}
    {% for col in column_list %}
        {{ clean_currency(col, decimal_places) }} as {{ col }}_cleaned{% if not loop.last %},{% endif %}
    {% endfor %}
{% endmacro %}
