"""Analytics dashboard page with placeholder KPI and charts."""

import numpy as np
import pandas as pd
import streamlit as st

from bandit_utils import metric_row, page_header, placeholder_chart, show_info_banner

page_header(
    "Analytics",
    "Monitor carousel performance and model behavior over time.",
)

st.subheader("Filters")
filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    date_range = st.date_input("Date Range", value=())
with filter_col2:
    selected_carousel = st.selectbox("Carousel", ["All", "Carousel A", "Carousel B", "Carousel C"])

st.info("🔧 [Filter Query Builder] will be connected here.")
# TODO: Connect to backend API for analytics filter execution.

st.divider()
st.subheader("Key Metrics")
metric_row(
    [
        {"label": "Total Impressions", "value": "12,450", "delta": "+4.2%"},
        {"label": "Total Clicks", "value": "1,140", "delta": "+1.1%"},
        {"label": "CTR", "value": "9.16%", "delta": "+0.3%"},
    ]
)

st.divider()
st.subheader("Charts")
placeholder_chart("Variant CTR Trend")

rng = np.random.default_rng(223)
time_index = pd.date_range("2026-01-01", periods=20, freq="D")
chart_data = pd.DataFrame(
    {
        "timestamp": time_index,
        "ctr_variant_a": rng.uniform(0.04, 0.12, size=20),
        "ctr_variant_b": rng.uniform(0.03, 0.11, size=20),
        "ctr_variant_c": rng.uniform(0.05, 0.13, size=20),
    }
).set_index("timestamp")

chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    st.caption("Dummy Line Chart (time series placeholder)")
    st.line_chart(chart_data)
with chart_col2:
    st.caption("Dummy Bar Chart (aggregate placeholder)")
    st.bar_chart(chart_data.mean().rename("mean_ctr"))

st.empty()
st.info(
    f"🔧 [Model Performance Breakdown] will be connected here for '{selected_carousel}' "
    f"and date range {date_range}."
)
# TODO: Connect to backend API for real model performance series and KPI snapshots.
