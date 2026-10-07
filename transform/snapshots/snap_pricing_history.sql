{% snapshot snap_pricing_history %}

{{
    config(
        target_database='dbt_practice',
        unique_key='coin_id',
        strategy='timestamp',
        updated_at='ingested_at',
        invalidate_hard_deletes=True
    )
}}
select
    coin_id,
    symbol,
    coin_name,
    current_price,
    total_volume,
    ingested_at::timestamp as ingested_at
from {{ source('dlt_crypto', 'pricing_history') }}
where ingested_at = (select max(ingested_at) from {{ source('dlt_crypto', 'pricing_history') }})
{% endsnapshot %}
