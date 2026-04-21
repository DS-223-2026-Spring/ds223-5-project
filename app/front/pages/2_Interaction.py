#Page for simulated carousel interactions

import streamlit as st

from bandit_utils import page_header, show_info_banner

page_header(
    "Interaction",
    "Simulate user selections and clicks for carousel variants.",
)

st.sidebar.subheader("Interaction Controls")
carousel_id = st.sidebar.selectbox("Carousel Selector", ["Carousel A", "Carousel B", "Carousel C"])
st.sidebar.caption("Select a carousel to simulate interaction flow.")

show_info_banner("🔧 Interaction events will be logged to backend services.")
# TODO: Connect to backend API for carousel recommendation and interaction logging.

display_col, controls_col = st.columns([2, 1])

with display_col:
    st.subheader("Carousel Display Area")
    st.info("🔧 [Carousel Variant Renderer] will be connected here.")
    carousel_placeholder = st.empty()
    carousel_placeholder.write(f"Currently previewing: {carousel_id}")

with controls_col:
    st.subheader("Interaction Buttons")
    click_variant_a = st.button("Click Variant A", use_container_width=True)
    click_variant_b = st.button("Click Variant B", use_container_width=True)
    skip = st.button("Skip", use_container_width=True)

st.divider()
st.subheader("Feedback / Result Area")
feedback_container = st.empty()

if click_variant_a:
    feedback_container.success("Placeholder: Logged click on Variant A.")
elif click_variant_b:
    feedback_container.success("Placeholder: Logged click on Variant B.")
elif skip:
    feedback_container.warning("Placeholder: Logged skip interaction.")
else:
    feedback_container.info("🔧 [Interaction Outcome + Recommended Arm] will appear here.")

st.info("🔧 [Model Output Diagnostics] will be connected here.")
# TODO: Connect to backend API for posterior values, confidence intervals, and arm choice.
