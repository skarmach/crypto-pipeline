{{
    config(
        materialized='incremental',
        unique_key='surrogate_key',
        on_schema_change='append_new_columns'
    )
}}

with stg as (
    select *
    from {{ ref('stg_crypto_prices') }}
    {% if is_incremental() %}
        -- lookback 2 hours for rolling window
        where price_timestamp > (select max(price_timestamp) - interval '2 hours' from {{ this }})
    {% endif %}
),
calculated_metrics as (
    select
        md5(coin_id || '-' || price_timestamp::text) as surrogate_key,
        coin_id,
        symbol,
        coin_name,
        price_timestamp,
        current_price_cleaned as price_usd,
        avg(current_price_cleaned) over (
            partition by coin_id
            order by price_timestamp
            rows between 5 preceding and current row
        ) as rolling_6_period_avg_price,
        current_price_cleaned - lag(current_price_cleaned) over (
            partition by coin_id
            order by price_timestamp
        ) as price_change_since_last_tick
    from stg
)
select *
from calculated_metrics

{% if is_incremental() %}
    -- lookback 2 hours for rolling window
    where price_timestamp > (select max(price_timestamp) from {{ this }})
{% endif %}
