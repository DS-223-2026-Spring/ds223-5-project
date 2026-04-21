#Page for creating carousel configurations

import streamlit as st

from bandit_utils import page_header, placeholder_form, show_info_banner

page_header(
    "Create Carousels",
    "Configure carousel variants and experiment settings before running interactions.",
)

st.sidebar.subheader("Create Workflow")
st.sidebar.write("1. Enter base carousel metadata")
st.sidebar.write("2. Define variant labels")
st.sidebar.write("3. Submit to create")

show_info_banner("🔧 Carousel creation will be connected to backend persistence.")
# TODO: Connect to backend API for carousel creation submit action.

placeholder_form("Carousel Configuration Form")

with st.form("create_carousel_form"):
    carousel_name = st.text_input("Carousel Name", placeholder="Homepage Hero Test")
    variant_count = st.number_input("Number of Variants", min_value=1, max_value=10, value=3)
    variant_labels = st.text_area(
        "Variant Labels (comma-separated)",
        placeholder="Variant A, Variant B, Variant C",
    )
    submitted = st.form_submit_button("Create Carousel")

st.subheader("Submission Result")
result_container = st.empty()
if submitted:
    parsed_labels = [label.strip() for label in variant_labels.split(",") if label.strip()]
    result_container.success(
        f"Placeholder submit: '{carousel_name or 'Untitled Carousel'}' with "
        f"{variant_count} variants and labels {parsed_labels or ['N/A']}."
    )
else:
    result_container.info("🔧 Created carousel confirmation will appear here after submit.")

st.divider()
st.info("🔧 [Model Configuration Defaults] will be connected here.")
# TODO: Connect to backend API for default model/config retrieval.
