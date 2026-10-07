with raw_data as (
    select *
    from {{ source('dlt_crypto', 'pricing_history') }}
)
select
    coin_id,
    symbol,
    coin_name,
    {{ clean_multiple_metrics(['current_price', 'total_volume'], decimal_places=2) }},
    ingested_at::timestamp as price_timestamp
from raw_data
