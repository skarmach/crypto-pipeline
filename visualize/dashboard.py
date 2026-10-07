import streamlit as pd
import streamlit as st
import psycopg2
import numpy as np
import pandas as pd
import os
import sys
import altair as alt

# Support python < 3.11 fallback for toml parsing if needed
try:
    import tomllib
except ImportError:
    import toml as tomllib

st.set_page_config(page_title="Crypto Pipeline Analytics", layout="wide")
st.title("🚀 Real-Time Crypto Data Platform")

# 1. Dynamically locate and resolve the secrets.toml path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRETS_PATH = os.path.join(BASE_DIR, "../ingest", ".dlt", "secrets.toml")

if not os.path.exists(SECRETS_PATH):
    st.error(f"Configuration Critical Failure: Could not locate secrets file at `{SECRETS_PATH}`")
    sys.exit(1)

# 2. Parse the database connection credentials securely from the TOML file
with open(SECRETS_PATH, "rb") as f:
    try:
        secrets = tomllib.load(f)
        db_creds = secrets["destination"]["postgres"]["credentials"]
    except Exception as e:
        st.error(f"Failed parsing credentials from configuration file: {e}")
        sys.exit(1)

# 3. Establish the secure database connection handshake
try:
    conn = psycopg2.connect(
        dbname=db_creds["database"],
        user=db_creds["username"],
        password=db_creds["password"],
        host=db_creds["host"],
        port=db_creds["port"]
    )
except Exception as e:
    st.error(f"Database Connection Engine Failed: {e}")
    sys.exit(1)

# 4. Fetch your Gold layer dbt table data metrics
try:
    query = """
        SELECT symbol, coin_name, price_usd, price_timestamp, price_change_since_last_tick, rolling_6_period_avg_price
        FROM raw_crypto.fct_crypto_metrics
        ORDER BY price_timestamp DESC
        LIMIT 200
    """
    df = pd.read_sql(query, conn)
finally:
    conn.close() # Ensure database connections clean up immediately

# 5. Display Live UI Component Cards
if df.empty:
    st.warning("Database connected successfully, but the `fct_crypto_metrics` table is currently empty. Waiting for cron execution...")
else:
    st.subheader("Latest Market Snapshot")
    latest = df.groupby('symbol').first().reset_index()
    cols = st.columns(len(latest))
    for i, row in latest.iterrows():
        cols[i].metric(
            label=row['coin_name'],
            value=f"\${row['price_usd']:,.2f}",
            delta=f"{row['price_change_since_last_tick']:+.4f}"
        )
    st.subheader("Bitcoin Price Tracking")
    btc_df = df[df['symbol'] == 'BTC']
    chart = (
        alt.Chart(btc_df)
            .mark_line(point={'size': 120, 'opacity': 0.5})
            .encode(
                x=alt.X('price_timestamp:T', title='Price Timestamp'),
                y=alt.Y('price_usd:Q', title='Price (USD)', scale=alt.Scale(zero=False)),
                color='symbol',
                tooltip=[
                    alt.Tooltip('price_timestamp:T', title='Price Timestamp', format='%Y-%m-%d %H:%M:%S'),
                    alt.Tooltip('price_usd:Q', title='Price (USD)', format='$.2f')
                ]
            )
            .interactive()
    )
    st.altair_chart(chart, use_container_width=True)

    st.subheader("Ethereum Price Tracking")
    eth_df = df[df['symbol'] == 'ETH']
    chart = (
        alt.Chart(eth_df)
            .mark_line()
            .encode(
                x=alt.X('price_timestamp:T', title='Price Timestamp'),
                y=alt.Y('price_usd:Q', title='Price (USD)', scale=alt.Scale(zero=False)),
                color='symbol',
                tooltip=[
                    alt.Tooltip('price_timestamp:T', title='Price Timestamp', format='%Y-%m-%d %H:%M:%S'),
                    alt.Tooltip('price_usd:Q', title='Price (USD)', format='$.2f')
                ]
            )
            .interactive()
    )
    st.altair_chart(chart, use_container_width=True)
