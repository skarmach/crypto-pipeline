{% test api_downtime(model, timestamp_column, max_hours_lag=2) %}
with latest_record as (
    select max({{ timestamp_column }}) as last_ingested_at
    from {{ model }}
),
downtime_check as (
    select
        last_ingested_at,
        {{ dbt.datediff("last_ingested_at", dbt.current_timestamp(), "hour") }} as hours_since_last_ingestion
    from latest_record
)
select
    *
from downtime_check
where hours_since_last_ingestion > {{ max_hours_lag }}
{% endtest %}
