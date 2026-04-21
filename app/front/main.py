"""Streamlit entry point for DS223 frontend."""

import streamlit as st

from bandit_utils import page_header, show_info_banner

st.set_page_config(page_title="DS223 Carousel Bandit", page_icon="🎯", layout="wide")

page_header(
    "DS223 Group Project Frontend",
    "Welcome to the multi-page Streamlit interface for carousel experimentation.",
)

st.sidebar.header("Navigation Guide")
st.sidebar.info(
    "Use Streamlit's page navigation in the sidebar to move between Create Carousels, "
    "Interaction, and Analytics."
)
st.sidebar.divider()
st.sidebar.caption("Milestone 2 UI skeleton")

show_info_banner("🔧 Backend API connectivity will be added in upcoming milestones.")
# TODO: Connect to backend API for app-level health and configuration bootstrap.

st.header("What You Can Do Here")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1) Create Carousels")
    st.write("Define carousel names, configure variants, and prepare experiments.")
    st.info("Open the Create Carousels page to configure new entries.")

with col2:
    st.subheader("2) Interact")
    st.write("Simulate user behavior by selecting variants and logging interactions.")
    st.info("Open the Interaction page to test click/selection flow.")

with col3:
    st.subheader("3) Analytics")
    st.write("Track KPIs and time-series performance from the bandit system.")
    st.info("Open the Analytics page to inspect charts and metrics.")

st.divider()
st.caption("Use the sidebar pages to continue.")
