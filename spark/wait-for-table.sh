#!/bin/bash

HOST=$1
PORT=$2
DB=$3
USER=$4
PASSWORD=$5
TABLE=$6

echo "[WAIT] Warte, bis Tabelle '$TABLE' in $DB Daten enthält..."

export PGPASSWORD=$PASSWORD

until psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DB" -tAc "SELECT 1 FROM $TABLE LIMIT 1;" | grep -q 1; do
  echo "[WAIT] Noch keine Daten in '$TABLE' – versuche erneut..."
  sleep 2
done

echo "[WAIT] Tabelle '$TABLE' enthält Daten."
