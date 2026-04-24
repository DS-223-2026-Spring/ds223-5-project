import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ui_core import (
    inject_css, nav_header, init_session,
    initials,
    INFLUENCERS, BRANDS,
    NICHES, FORMATS, INDUSTRIES, SIZES,
)

st.set_page_config(page_title="Discover · PairUp", page_icon="🔍", layout="wide")
inject_css()
init_session()

role = st.session_state.get("role", "brand")

# ── top nav bar (shared component) ────────────────────────────────────────────
nav_header("discover")

# ── layout: sidebar + main ────────────────────────────────────────────────────
sidebar, main = st.columns([1, 4])

# defaults (so both roles always have the variables defined)
niche_filter = []
loc_input    = ""
min_eng      = 0.0
max_fol      = 100000
min_score    = 0
fmt_filter   = []
ind_filter   = []
size_filter  = []

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with sidebar:
    st.markdown(f"""
    <div style='font-size:15px;font-weight:700;color:#0D0E1A;margin-bottom:4px'>
        {'Filter creators' if role == 'brand' else 'Filter brands'}
    </div>
    <div style='font-size:12px;color:#9899B0;margin-bottom:8px'>
        {'Narrow your perfect match' if role == 'brand' else 'Find the right brand for you'}
    </div>
    """, unsafe_allow_html=True)

    if role == "brand":
        st.markdown("<div class='filter-label'>YOUR CAMPAIGN NICHE</div>",
                    unsafe_allow_html=True)
        st.text_input("Campaign niche", placeholder="e.g. Fitness, Food, Tech",
                      label_visibility="collapsed", key="niche_txt")

        st.markdown("<div class='filter-label'>CREATOR LOCATION</div>",
                    unsafe_allow_html=True)
        loc_input = st.text_input("Creator location",
                                  placeholder="e.g. New York, London",
                                  label_visibility="collapsed", key="loc_txt")

        st.markdown("<div class='filter-label'>CREATOR NICHE</div>",
                    unsafe_allow_html=True)
        niche_filter = st.multiselect("Creator niche", NICHES,
                                      label_visibility="collapsed", key="niche_ms")

        st.markdown("<div class='filter-label'>MIN ENGAGEMENT RATE</div>",
                    unsafe_allow_html=True)
        min_eng = st.slider("Min engagement", 0.0, 10.0, 0.0, 0.1,
                            format="%.1f%%", label_visibility="collapsed",
                            key="eng_sl")

        st.markdown("<div class='filter-label'>MAX FOLLOWERS</div>",
                    unsafe_allow_html=True)
        max_fol = st.slider("Max followers", 5000, 100000, 100000, 1000,
                            format="%d", label_visibility="collapsed", key="fol_sl")

        st.markdown("<div class='filter-label'>MIN MATCH SCORE</div>",
                    unsafe_allow_html=True)
        min_score = st.slider("Min score", 0, 100, 0, format="%d%%",
                              label_visibility="collapsed", key="score_sl")

        st.markdown("<div class='filter-label'>CONTENT FORMAT</div>",
                    unsafe_allow_html=True)
        fmt_filter = st.multiselect("Formats", FORMATS,
                                    label_visibility="collapsed", key="fmt_ms")

    else:
        st.markdown("<div class='filter-label'>INDUSTRY</div>",
                    unsafe_allow_html=True)
        ind_filter = st.multiselect("Industry", INDUSTRIES,
                                    label_visibility="collapsed", key="ind_ms")

        st.markdown("<div class='filter-label'>COMPANY SIZE</div>",
                    unsafe_allow_html=True)
        size_filter = st.multiselect("Size", SIZES,
                                     label_visibility="collapsed", key="size_ms")

        st.markdown("<div class='filter-label'>MIN MATCH SCORE</div>",
                    unsafe_allow_html=True)
        min_score = st.slider("Min score", 0, 100, 0, format="%d%%",
                              label_visibility="collapsed", key="score_sl2")

# ── MAIN AREA ──────────────────────────────────────────────────────────────────
with main:
    if role == "brand":
        # apply filters
        results = list(INFLUENCERS)
        if niche_filter:
            results = [r for r in results if r["niche"] in niche_filter]
        if loc_input:
            results = [r for r in results if loc_input.lower() in r["location"].lower()]
        if min_eng > 0:
            results = [r for r in results if r["engagement"] >= min_eng]
        if max_fol < 100000:
            results = [r for r in results if r["followers"] <= max_fol]
        if min_score > 0:
            results = [r for r in results if r["total_score"] >= min_score]
        if fmt_filter:
            results = [r for r in results if any(f in r["formats"] for f in fmt_filter)]
        results.sort(key=lambda x: x["total_score"], reverse=True)

        head1, head2 = st.columns([3, 1])
        with head1:
            st.markdown(f"""
            <div style='font-size:20px;font-weight:700;color:#0D0E1A'>Matched creators</div>
            <div style='font-size:13px;color:#9899B0;margin-bottom:16px'>
                {len(results)} creators found
            </div>
            """, unsafe_allow_html=True)
        with head2:
            sort_by = st.selectbox("Sort:",
                                   ["Match score", "Engagement", "Followers"],
                                   label_visibility="collapsed")

        if sort_by == "Engagement":
            results.sort(key=lambda x: x["engagement"], reverse=True)
        elif sort_by == "Followers":
            results.sort(key=lambda x: x["followers"], reverse=True)

        # render cards in 2 columns
        cols_per_row = 2
        for i in range(0, len(results), cols_per_row):
            row = results[i:i+cols_per_row]
            card_cols = st.columns(cols_per_row)
            for col, inf in zip(card_cols, row):
                with col:
                    score = inf["total_score"]
                    score_cls = ("score-high" if score >= 75
                                 else ("score-mid" if score >= 50 else "score-low"))
                    av = initials(inf["name"])
                    fmts = "".join(f"<span class='fmt-chip'>{f}</span>"
                                   for f in inf["formats"])
                    rate_chip = f"<span class='fmt-chip'>{inf['rate']}</span>"

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
                        <div style='margin-bottom:8px'>
                            <div style='font-size:11px;color:#9899B0;margin-bottom:4px'>Niche · Audience · Engagement · History</div>
                            <div style='display:flex;gap:3px'>
                                <div style='flex:35;height:4px;background:#6C63FF;border-radius:2px;opacity:{inf['niche_score']/100}'></div>
                                <div style='flex:30;height:4px;background:#00C896;border-radius:2px;opacity:{inf['audience_score']/100}'></div>
                                <div style='flex:25;height:4px;background:#F5A623;border-radius:2px;opacity:{inf['engagement_score']/100}'></div>
                                <div style='flex:10;height:4px;background:#FF5C5C;border-radius:2px;opacity:{inf['history_score']/100}'></div>
                            </div>
                        </div>
                        <div>{fmts}{rate_chip}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("View profile →", key=f"view_{inf['id']}",
                                 use_container_width=True):
                        st.session_state.selected_id = inf["id"]
                        st.switch_page("pages/3_My_Profile.py")

    else:
        # creator view — show brands
        results = list(BRANDS)
        if min_score > 0:
            results = [r for r in results if r["total_score"] >= min_score]
        if ind_filter:
            results = [r for r in results if r["industry"] in ind_filter]
        if size_filter:
            results = [r for r in results if r["size"] in size_filter]
        results.sort(key=lambda x: x["total_score"], reverse=True)

        st.markdown(f"""
        <div style='font-size:20px;font-weight:700;color:#0D0E1A'>Matched brands</div>
        <div style='font-size:13px;color:#9899B0;margin-bottom:16px'>
            {len(results)} brands found
        </div>
        """, unsafe_allow_html=True)

        cols_per_row = 2
        for i in range(0, len(results), cols_per_row):
            row = results[i:i+cols_per_row]
            card_cols = st.columns(cols_per_row)
            for col, brand in zip(card_cols, row):
                with col:
                    score = brand["total_score"]
                    score_cls = ("score-high" if score >= 75
                                 else ("score-mid" if score >= 50 else "score-low"))
                    prefs = "".join(f"<span class='fmt-chip'>{p}</span>"
                                    for p in brand["preferences"])
                    st.markdown(f"""
                    <div class='creator-card'>
                        <div style='display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:12px'>
                            <div>
                                <div style='font-size:14px;font-weight:700;color:#0D0E1A'>{brand['name']}</div>
                                <div style='font-size:12px;color:#9899B0'>{brand['industry']} · {brand['size']} · {brand['location']}</div>
                            </div>
                            <span class='score-badge {score_cls}'>{score}%</span>
                        </div>
                        <div style='display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-bottom:12px'>
                            <div><div class='stat-lbl'>budget</div><div class='stat-val'>${brand['budget_min']:,}–${brand['budget_max']:,}</div></div>
                            <div><div class='stat-lbl'>target audience</div><div class='stat-val' style='font-size:12px'>{brand['target'][:28]}…</div></div>
                        </div>
                        <div>{prefs}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("View brand →", key=f"view_brand_{brand['id']}",
                                 use_container_width=True):
                        st.session_state.selected_id = brand["id"]
                        st.switch_page("pages/3_My_Profile.py")