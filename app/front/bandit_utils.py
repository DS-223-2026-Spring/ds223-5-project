from __future__ import annotations
from typing import Any
import streamlit as st


def page_header(title: str, description: str = "") -> None:
    #Render a consistent page header across all pages
    st.title(title)
    if description:
        st.caption(description)
    st.divider()


def placeholder_chart(chart_title: str) -> None:
    #Render a placeholder chart area with a chart-specific message
    container = st.container(border=True)
    with container:
        st.subheader(chart_title)
        st.info(f"Chart: {chart_title} will appear here.")
        st.empty()


def placeholder_form(form_title: str) -> None:
    #Render a placeholder form container
    container = st.container(border=True)
    with container:
        st.subheader(form_title)
        st.info("🔧 Form inputs and submission wiring will be connected here.")


def metric_row(metrics: list[dict[str, Any]]) -> None:
    #Render a row of metric cards using label, value, and optional delta
    if not metrics:
        st.info("No metrics configured yet.")
        return

    columns = st.columns(len(metrics))
    for col, item in zip(columns, metrics):
        col.metric(
            label=str(item.get("label", "Metric")),
            value=str(item.get("value", "-")),
            delta=item.get("delta"),
        )


def show_info_banner(message: str) -> None:
    #Display a highlighted information banner
    st.info(message)
