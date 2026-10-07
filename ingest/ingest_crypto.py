import argparse
from datetime import datetime, timezone

import dlt
import sys
from kraken.spot import Market

parser = argparse.ArgumentParser(description="Ingest Kraken ticker data into dlt.")
parser.add_argument(
    "env",
    choices=["dev", "prod"],
    help="Environment to ingest into: 'dev' uses raw_crypto_dev, 'prod' uses raw_crypto."
)
args = parser.parse_args()

dataset_name = "raw_crypto_dev" if args.env == "dev" else "raw_crypto"

# Initialize pipeline pointing to the environment-specific schema
pipeline = dlt.pipeline(
    pipeline_name="crypto_realtime",
    destination="postgres",
    dataset_name=dataset_name
)

try:
    market = Market()
    print(f"[{datetime.now(timezone.utc).isoformat()}] Fetching ticker data...")
    api_response = market.get_ticker(pair=["XXBTZUSD,XETHZUSD,SOLUSD"])
except Exception as e:
    print(f"Failed to fetch from Kraken SDK: {e}")
    sys.exit(1)

pairs_data = api_response
print(pairs_data)
mapping_names = {
    "XXBTZUSD": {"name": "Bitcoin", "symbol": "BTC"},
    "XETHZUSD": {"name": "Ethereum", "symbol": "ETH"},
    "XSOLZUSD": {"name": "Solana", "symbol": "SOL"}
}
# Process data payloads to inject a unified timestamp
current_time = datetime.now(timezone.utc).isoformat()
cleaned_records = []

for kraken_key, info in pairs_data.items():
    if kraken_key in mapping_names:
        coin_meta = mapping_names[kraken_key]
        cleaned_records.append({
            "coin_id": coin_meta["name"].lower(),
            "symbol": coin_meta["symbol"],
            "coin_name": coin_meta["name"],
            # 'c' key represents Last Closed Trade array [price, lot volume]
            "current_price": float(info["c"][0]),
            # 'v' key represents Volume array [today, last 24h]
            "total_volume": float(info["v"][1]),
            "ingested_at": current_time
        })

if not cleaned_records:
    raise Exception("JSON was valid but no matching crypto pairs were recovered.")

# 4. Append rows over time to build out history
load_info = pipeline.run(
    cleaned_records,
    table_name="pricing_history",
    write_disposition="append"
)
print(f"Ingested successful: {load_info}")
