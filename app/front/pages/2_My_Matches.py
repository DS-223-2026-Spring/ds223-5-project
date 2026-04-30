import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ui_core import inject_css, nav_header, init_session, score_badge, initials, INFLUENCERS, BRANDS

st.set_page_config(page_title="My Matches · PairUp", page_icon="⭐", layout="wide")
inject_css()
init_session()

role = st.session_state.get("role", "brand")

nav_header('matches')

# ── page header ────────────────────────────────────────────────────────────────
st.markdown("""
<div style='font-size:26px;font-weight:800;color:#0D0E1A;margin-bottom:4px'>My matches</div>
<div style='font-size:14px;color:#9899B0;margin-bottom:28px'>Your saved creators and sent collaboration requests</div>
""", unsafe_allow_html=True)

saved     = st.session_state.get("saved", set())
contacted = st.session_state.get("contacted", set())

all_items = {inf["id"]: inf for inf in INFLUENCERS} if role == "brand" else {b["id"]: b for b in BRANDS}

# ── saved section ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='font-size:11px;font-weight:700;color:#9899B0;text-transform:uppercase;
            letter-spacing:.6px;margin-bottom:12px'>
    SAVED &nbsp; {len(saved)}
</div>
""", unsafe_allow_html=True)

if not saved:
    st.markdown("""
    <div style='background:#fff;border:1px solid #E4E5F0;border-radius:14px;
                padding:48px;text-align:center;margin-bottom:24px'>
        <div style='font-size:28px;margin-bottom:10px'>☆</div>
        <div style='font-size:14px;color:#9899B0'>
            No saved creators yet. Browse the marketplace and save your favourites.
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for pid in saved:
        p = all_items.get(pid, {})
        if not p:
            continue
        name  = p.get("name", f"Profile #{pid}")
        niche = p.get("niche") or p.get("industry", "—")
        score = p.get("total_score", 0)
        score_cls = "score-high" if score >= 75 else ("score-mid" if score >= 50 else "score-low")

        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown(f"""
            <div class='creator-card' style='margin-bottom:8px'>
                <div style='display:flex;align-items:center;justify-content:space-between'>
                    <div style='font-size:14px;font-weight:700;color:#0D0E1A'>{name}
                        <span class='niche-chip' style='margin-left:8px'>{niche}</span>
                    </div>
                    <span class='score-badge {score_cls}'>{score}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("View →", key=f"saved_view_{pid}"):
                st.session_state.selected_id = pid
                st.switch_page("pages/3_My_Profile.py")

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# ── requests sent section ──────────────────────────────────────────────────────
st.markdown(f"""
<div style='font-size:11px;font-weight:700;color:#9899B0;text-transform:uppercase;
            letter-spacing:.6px;margin-bottom:12px'>
    REQUESTS SENT &nbsp; {len(contacted)}
</div>
""", unsafe_allow_html=True)

if not contacted:
    st.markdown("""
    <div style='background:#fff;border:1px solid #E4E5F0;border-radius:14px;
                padding:48px;text-align:center'>
        <div style='font-size:28px;margin-bottom:10px'>✉</div>
        <div style='font-size:14px;color:#9899B0'>
            No requests sent yet. Open a profile and reach out directly.
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    for pid in contacted:
        p = all_items.get(pid, {"name": f"Profile #{pid}", "total_score": 0})
        name  = p.get("name", f"Profile #{pid}")
        score = p.get("total_score", 0)
        score_cls = "score-high" if score >= 75 else ("score-mid" if score >= 50 else "score-low")
        st.markdown(f"""
        <div class='creator-card' style='border-left:3px solid #6C63FF;margin-bottom:8px'>
            <div style='display:flex;align-items:center;justify-content:space-between'>
                <div>
                    <div style='font-size:14px;font-weight:700;color:#0D0E1A'>{name}</div>
                    <div style='font-size:12px;color:#9899B0;margin-top:2px'>
                        <span style='background:#E0FBF4;color:#007A5A;font-size:11px;font-weight:600;
                                     padding:2px 8px;border-radius:10px'>Request sent</span>
                        &nbsp; Awaiting response
                    </div>
                </div>
                <span class='score-badge {score_cls}'>{score}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
