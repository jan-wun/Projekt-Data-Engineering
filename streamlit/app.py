import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

# Utility: Format large numbers nicely
def format_large_number(n, decimals=2):
    """Formats large numbers with SI suffix and rounding."""
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.{decimals}f}B"
    elif n >= 1_000_000:
        return f"{n / 1_000_000:.{decimals}f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.{decimals}f}K"
    else:
        return f"{n:.{decimals}f}"

# DB engine
engine = create_engine(
    f"postgresql+psycopg2://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@postgres:5432/{os.environ['POSTGRES_DB']}"
)

# Load data
df = pd.read_sql("SELECT * FROM aggregated_bitcoin_data ORDER BY year, quarter", engine)
df["quarter_label"] = df["year"].astype(str) + " Q" + df["quarter"].astype(str)

# Filter for complete quarters
full_quarters = df[df["is_partial"] == False]
latest_full = full_quarters.iloc[-1]

# UI Setup
st.set_page_config(page_title="Bitcoin Dashboard", layout="wide")
st.title("📊 Bitcoin Quarterly Aggregated Data")

# KPIs Section
st.markdown("📌 Latest Complete Quarter")
with st.container():
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Quarter", latest_full["quarter_label"])
    col2.metric("Avg Open", format_large_number(latest_full["avg_open"]))
    col3.metric("Avg Close", format_large_number(latest_full["avg_close"]))
    col4.metric("Volume", format_large_number(latest_full["total_volume"]))

    col5, col6, col7 = st.columns(3)
    col5.metric("Min Low", format_large_number(latest_full["min_low"]))
    col6.metric("Max High", format_large_number(latest_full["max_high"]))
    col7.metric("Counted Days", int(latest_full["count_days"]))

st.markdown("---")

# Chart: Avg Close
st.subheader("💵 Average Close Price per Quarter")
fig_close = px.line(
    full_quarters, x="quarter_label", y="avg_close", markers=True,
    labels={"quarter_label": "Quarter", "avg_close": "Avg Close"}
)
fig_close.update_layout(yaxis_tickformat=".2~s")
st.plotly_chart(fig_close, use_container_width=True)

# Chart: Avg Open
st.subheader("💵 Average Open Price per Quarter")
fig_open = px.line(
    full_quarters, x="quarter_label", y="avg_open", markers=True,
    labels={"quarter_label": "Quarter", "avg_open": "Avg Open"}
)
fig_open.update_layout(yaxis_tickformat=".2~s")
st.plotly_chart(fig_open, use_container_width=True)

# Chart: Volume
st.subheader("📊 Total Trading Volume per Quarter")
fig_volume = px.bar(
    full_quarters, x="quarter_label", y="total_volume",
    labels={"quarter_label": "Quarter", "total_volume": "Volume"}
)
fig_volume.update_layout(yaxis_tickformat=".2~s")
st.plotly_chart(fig_volume, use_container_width=True)

# Chart: Min/Max
st.subheader("📉 Min Low and Max High per Quarter")
fig_range = go.Figure()
fig_range.add_trace(go.Bar(name="Min Low", x=full_quarters["quarter_label"], y=full_quarters["min_low"]))
fig_range.add_trace(go.Bar(name="Max High", x=full_quarters["quarter_label"], y=full_quarters["max_high"]))
fig_range.update_layout(
    barmode="group",
    xaxis_title="Quarter",
    yaxis_title="Price",
    legend_title="Metric",
    yaxis_tickformat=".2~s"
)
st.plotly_chart(fig_range, use_container_width=True)


st.markdown("---")

# Full table
with st.expander("🔍 Show full aggregated data table"):
    st.dataframe(df)
