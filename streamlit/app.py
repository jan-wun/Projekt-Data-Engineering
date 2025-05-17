import streamlit as st
import pandas as pd
import psycopg2
import os

# DB-Verbindung herstellen
conn = psycopg2.connect(
    host="postgres",
    database=os.environ.get("POSTGRES_DB"),
    user=os.environ.get("POSTGRES_USER"),
    password=os.environ.get("POSTGRES_PASSWORD"),
    port=5432
)

# Daten laden
df = pd.read_sql("SELECT * FROM aggregated_bitcoin_data", conn)

# App UI
st.title("Bitcoin Quarterly Analysis")
st.dataframe(df)
