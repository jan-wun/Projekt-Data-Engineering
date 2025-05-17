#!/bin/bash

# Arguments: host, port, db, user, password, table
HOST=$1
PORT=$2
DB=$3
USER=$4
PASSWORD=$5
TABLE=$6

echo "[WAIT] Waiting for table '$TABLE' in database '$DB' to contain data (for Streamlit)..."

# Set the PostgreSQL password for psql
export PGPASSWORD=$PASSWORD

# Loop until the table exists and contains at least one row
until psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DB" -tAc "SELECT 1 FROM $TABLE LIMIT 1;" | grep -q 1; do
  echo "[WAIT] Table '$TABLE' is not ready or empty. Retrying in 5 seconds..."
  sleep 5
done

echo "[WAIT] Table '$TABLE' contains data. Streamlit can start."
