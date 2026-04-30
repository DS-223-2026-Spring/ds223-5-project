import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ui_core import inject_css, nav_header, init_session, score_badge, score_bars, initials, NICHES, FORMATS, AGE_GROUPS, INDUSTRIES, SIZES
from api import get_influencers, get_brands

st.set_page_config(page_title="Discover · PairUp", page_icon="🔍", layout="wide")
inject_css()
init_session()

role = st.session_state.get("role", "brand")
nav_header("discover")

sidebar, main = st.columns([1, 4])

# defaults
niche_filter = []; loc_input = ""; min_eng = 0.0; max_fol = 100000
min_score = 0; fmt_filter = []; ind_filter = []; size_filter = []

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with sidebar:
    if role == "brand":
        st.markdown(f"""<div style='font-size:15px;font-weight:700;color:#0D0E1A;margin-bottom:4px'>Filter creators</div>
        <div style='font-size:12px;color:#9899B0;margin-bottom:16px'>Narrow down your perfect match</div>""",
        unsafe_allow_html=True)

        st.markdown("<div style='font-size:11px;font-weight:700;color:#9899B0;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px'>YOUR CAMPAIGN NICHE</div>", unsafe_allow_html=True)
        niche_txt = st.text_input("", placeholder="e.g. Fitness, Food, Tech", label_visibility="collapsed", key="niche_txt")

        st.markdown("<div style='font-size:11px;font-weight:700;color:#9899B0;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px'>CREATOR LOCATION</div>", unsafe_allow_html=True)
        loc_input = st.text_input("", placeholder="e.g. New York, Los Angeles", label_visibility="collapsed", key="loc_txt")

        st.markdown("<div style='font-size:11px;font-weight:700;color:#9899B0;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px'>CREATOR NICHE</div>", unsafe_allow_html=True)
        niche_filter = st.multiselect("", NICHES, label_visibility="collapsed", key="niche_ms")

        st.markdown("<div style='font-size:11px;font-weight:700;color:#9899B0;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px'>MIN ENGAGEMENT RATE</div>", unsafe_allow_html=True)
        min_eng = st.slider("", 0.0, 10.0, 0.0, 0.1, format="%.1f%%", label_visibility="collapsed", key="eng_sl")

        st.markdown("<div style='font-size:11px;font-weight:700;color:#9899B0;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px'>MAX FOLLOWERS</div>", unsafe_allow_html=True)
        max_fol = st.slider("", 5000, 100000, 100000, 1000, format="%,d", label_visibility="collapsed", key="fol_sl")

        st.markdown("<div style='font-size:11px;font-weight:700;color:#9899B0;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px'>MIN MATCH SCORE</div>", unsafe_allow_html=True)
        min_score = st.slider("", 0, 100, 0, format="%d%%", label_visibility="collapsed", key="score_sl")

        st.markdown("<div style='font-size:11px;font-weight:700;color:#9899B0;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px'>CONTENT FORMAT</div>", unsafe_allow_html=True)
        fmt_filter = st.multiselect("", FORMATS, label_visibility="collapsed", key="fmt_ms")

    else:
        st.markdown(f"""<div style='font-size:15px;font-weight:700;color:#0D0E1A;margin-bottom:4px'>Filter brands</div>
        <div style='font-size:12px;color:#9899B0;margin-bottom:16px'>Find brands looking for you</div>""",
        unsafe_allow_html=True)

        st.markdown("<div style='font-size:11px;font-weight:700;color:#9899B0;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px'>YOUR CREATOR NICHE</div>", unsafe_allow_html=True)
        st.text_input("", placeholder="e.g. Fitness, Beauty", label_visibility="collapsed", key="c_niche")

        st.markdown("<div style='font-size:11px;font-weight:700;color:#9899B0;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px'>YOUR LOCATION</div>", unsafe_allow_html=True)
        st.text_input("", placeholder="e.g. New York, Los Angeles", label_visibility="collapsed", key="c_loc")

        st.markdown("<div style='font-size:11px;font-weight:700;color:#9899B0;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px'>BRAND INDUSTRY</div>", unsafe_allow_html=True)
        ind_filter = st.multiselect("", INDUSTRIES, label_visibility="collapsed", key="ind_ms")

        st.markdown("<div style='font-size:11px;font-weight:700;color:#9899B0;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px'>MIN MATCH SCORE</div>", unsafe_allow_html=True)
        min_score = st.slider("", 0, 100, 0, format="%d%%", label_visibility="collapsed", key="score_sl2")

        st.markdown("<div style='font-size:11px;font-weight:700;color:#9899B0;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px'>BUDGET RANGE</div>", unsafe_allow_html=True)
        for label in ["Under $2K","$2K–$5K","$5K–$10K","$10K+"]:
            st.checkbox(label, key=f"budget_{label}")

        st.markdown("<div style='font-size:11px;font-weight:700;color:#9899B0;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px'>COMPANY SIZE</div>", unsafe_allow_html=True)
        size_filter = st.multiselect("", SIZES, label_visibility="collapsed", key="size_ms")

        if st.button("Find brands", type="primary", use_container_width=True):
            st.rerun()
        if st.button("Reset", use_container_width=True):
            st.rerun()

# ── MAIN AREA ──────────────────────────────────────────────────────────────────
with main:
    if role == "brand":
        results = get_influencers(
            niche=niche_filter[0] if len(niche_filter)==1 else None,
            location=loc_input or None,
            min_engagement=min_eng if min_eng > 0 else None,
            max_followers=max_fol if max_fol < 100000 else None,
            min_match_score=min_score if min_score > 0 else None,
        )
        # client-side multi-filter
        if niche_filter: results = [r for r in results if r["niche"] in niche_filter]
        if fmt_filter:   results = [r for r in results if any(f in r["formats"] for f in fmt_filter)]
        if min_score:    results = [r for r in results if r["total_score"] >= min_score]

        head1, head2 = st.columns([3,1])
        with head1:
            st.markdown(f"""<div style='font-size:20px;font-weight:700;color:#0D0E1A'>Matched creators</div>
            <div style='font-size:13px;color:#9899B0;margin-bottom:16px'>{len(results)} creators found</div>""", unsafe_allow_html=True)
        with head2:
            sort_by = st.selectbox("Sort:", ["Match score","Engagement","Followers"], label_visibility="collapsed", key="sort_sel")

        if sort_by == "Engagement": results.sort(key=lambda x: x["engagement"], reverse=True)
        elif sort_by == "Followers": results.sort(key=lambda x: x["followers"], reverse=True)

        for i in range(0, len(results), 2):
            row = results[i:i+2]
            cols = st.columns(2)
            for col, inf in zip(cols, row):
                with col:
                    score = inf["total_score"]
                    score_cls = "score-high" if score>=75 else ("score-mid" if score>=50 else "score-low")
                    av = initials(inf["name"])
                    fmts = "".join(f"<span class='fmt-chip'>{f}</span>" for f in inf["formats"])

                    st.markdown(f"""
                    <div class='creator-card'>
                        <div style='display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:12px'>
                            <div style='display:flex;align-items:center;gap:10px'>
                                <div class='avatar'>{av}</div>
                                <div>
                                    <div style='font-size:14px;font-weight:700;color:#0D0E1A'>{inf['name']}</div>
                                    <div style='font-size:12px;color:#9899B0'>{inf['niche']} · {inf['location']}</div>
                                </div>
                            </div>
                            <span class='score-badge {score_cls}'>{score}%</span>
                        </div>
                        <div style='display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:12px'>
                            <div><div class='stat-lbl'>followers</div><div class='stat-val'>{inf['followers']/1000:.1f}K</div></div>
                            <div><div class='stat-lbl'>engagement</div><div class='stat-val'>{inf['engagement']}%</div></div>
                            <div><div class='stat-lbl'>audience</div><div class='stat-val'>{inf['age']}</div></div>
                        </div>
                        <div style='margin-bottom:10px'>
                            <div style='font-size:11px;color:#9899B0;margin-bottom:3px'>● Niche &nbsp; ● Audience &nbsp; ● Engagement &nbsp; ● History</div>
                            <div style='display:flex;gap:3px;height:5px'>
                                <div style='flex:35;background:#6C63FF;border-radius:2px;opacity:{inf["niche_score"]/100}'></div>
                                <div style='flex:30;background:#00C896;border-radius:2px;opacity:{inf["audience_score"]/100}'></div>
                                <div style='flex:25;background:#F5A623;border-radius:2px;opacity:{inf["engagement_score"]/100}'></div>
                                <div style='flex:10;background:#FF5C5C;border-radius:2px;opacity:{inf["history_score"]/100}'></div>
                            </div>
                        </div>
                        <div>{fmts}<span class='fmt-chip'>{inf['rate']}</span></div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("View profile →", key=f"view_inf_{inf['id']}", use_container_width=True):
                        st.session_state.selected_id = inf["id"]
                        st.session_state.selected_type = "influencer"
                        st.switch_page("pages/3_My_Profile.py")

    else:
        # creator searching brands
        results = get_brands(
            industry=ind_filter[0] if len(ind_filter)==1 else None,
            size=size_filter[0] if len(size_filter)==1 else None,
            min_match_score=min_score if min_score > 0 else None,
        )
        if ind_filter: results = [r for r in results if any(ind.lower() in r["industry"].lower() for ind in ind_filter)]
        if min_score:  results = [r for r in results if r["total_score"] >= min_score]

        st.markdown(f"""<div style='font-size:20px;font-weight:700;color:#0D0E1A'>Brands seeking creators</div>
        <div style='font-size:13px;color:#9899B0;margin-bottom:16px'>{len(results)} brands found</div>""", unsafe_allow_html=True)

        for i in range(0, len(results), 2):
            row = results[i:i+2]
            cols = st.columns(2)
            for col, brand in zip(cols, row):
                with col:
                    score = brand["total_score"]
                    score_cls = "score-high" if score>=75 else ("score-mid" if score>=50 else "score-low")
                    av = brand["name"][:2].upper()
                    prefs = "".join(f"<span class='fmt-chip'>{p}</span>" for p in brand["preferences"][:4])

                    st.markdown(f"""
                    <div class='creator-card'>
                        <div style='display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:12px'>
                            <div style='display:flex;align-items:center;gap:10px'>
                                <div class='avatar' style='background:#E0FBF4;color:#00A87D'>{av}</div>
                                <div>
                                    <div style='font-size:14px;font-weight:700;color:#0D0E1A'>{brand['name']}</div>
                                    <div style='font-size:12px;color:#9899B0'>{brand['industry']} · {brand['location']}</div>
                                </div>
                            </div>
                            <span class='score-badge {score_cls}'>{score}%</span>
                        </div>
                        <div style='display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:12px'>
                            <div><div class='stat-lbl'>company</div><div class='stat-val' style='font-size:13px'>{brand['size']}</div></div>
                            <div><div class='stat-lbl'>niches</div><div class='stat-val' style='font-size:13px'>{len([p for p in brand['preferences'] if p not in ["Reels","Stories","Long-form","Posts"]])}</div></div>
                            <div><div class='stat-lbl'>formats</div><div class='stat-val' style='font-size:13px'>{len([p for p in brand['preferences'] if p in ["Reels","Stories","Long-form","Posts"]])}</div></div>
                        </div>
                        <div style='margin-bottom:8px'>
                            <span style='background:#E0FBF4;color:#007A5A;font-size:11px;font-weight:700;padding:3px 10px;border-radius:6px'>${brand['budget_min']:,}–${brand['budget_max']:,}</span>
                        </div>
                        <div style='font-size:12px;color:#5A5B72;margin-bottom:8px;line-height:1.4'>{brand['target']}</div>
                        <div>{prefs}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("View brand →", key=f"view_brand_{brand['id']}", use_container_width=True):
                        st.session_state.selected_id = brand["id"]
                        st.session_state.selected_type = "brand"
                        st.switch_page("pages/3_My_Profile.py")