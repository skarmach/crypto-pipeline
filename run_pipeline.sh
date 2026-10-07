#!/bin/bash
set -e

# Project ROOT
PROJECT_ROOT="/home/skarmach/dbt-local-project/crypto_pipeline"

# Define log and lock files
LOCKFILE="/tmp/crypto_pipeline.lock"
LOGFILE="/home/skarmach/dbt-local-project/crypto_pipeline/pipeline.log"
exec 200>"$LOCKFILE"

# Acquire lock
if ! flock -n 200; then
    echo "[$(date)] Warning: Pipeline is already running. Skipping this run." >> "$LOGFILE"
    exit 0
fi

# Log start of pipeline
echo "[$(date)] Starting pipeline run" >> "$LOGFILE"

# Activate the dbt environment
source /home/skarmach/dbt-local-project/dbt-env/bin/activate

# Starting ingestion
echo "[$(date)] Starting data ingestion" >> "$LOGFILE"

# Ingest Data
cd $PROJECT_ROOT/ingest
python ingest_crypto.py prod >> "$LOGFILE" 2>&1

# Starting transformation
echo "[$(date)] Starting data transformation" >> "$LOGFILE"

# Run and test dbt
cd $PROJECT_ROOT/transform
dbt build --target prod >> "$LOGFILE" 2>&1

echo "[$(date)] Pipeline completed successfully." >> "$LOGFILE"
