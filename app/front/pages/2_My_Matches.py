import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ui_core import inject_css, nav_header, init_session, initials, score_badge
from api import get_influencer, get_brand, get_contact_requests, INFLUENCERS, BRANDS

st.set_page_config(page_title="My Matches · PairUp", page_icon="⭐", layout="wide")
inject_css()
init_session()

role = st.session_state.get("role", "brand")
nav_header("matches")

st.markdown("""
<div style='font-size:26px;font-weight:800;color:#0D0E1A;margin-bottom:4px'>My matches</div>
<div style='font-size:14px;color:#9899B0;margin-bottom:28px'>Your saved creators and sent collaboration requests</div>
""", unsafe_allow_html=True)

saved     = st.session_state.get("saved", set())
contacted = st.session_state.get("contacted", set())

all_items = (
    {inf["id"]: inf for inf in INFLUENCERS} if role == "brand"
    else {b["id"]: b for b in BRANDS}
)

# ── SAVED ──────────────────────────────────────────────────────────────────────
saved_count = len(saved)
st.markdown(f"<div class='sec-title'>SAVED &nbsp; {saved_count}</div>", unsafe_allow_html=True)

if not saved:
    st.markdown("""
    <div style='background:#fff;border:1px solid #E4E5F0;border-radius:14px;
                padding:48px;text-align:center;margin-bottom:24px'>
        <div style='font-size:28px;margin-bottom:10px'>☆</div>
        <div style='font-size:14px;color:#9899B0'>No saved creators yet. Browse the marketplace and save your favourites.</div>
    </div>""", unsafe_allow_html=True)
else:
    for pid in saved:
        p = all_items.get(pid, {})
        if not p: continue
        name  = p.get("name", f"Profile #{pid}")
        niche = p.get("niche") or p.get("industry", "—")
        score = p.get("total_score", 0)
        score_cls = "score-high" if score>=75 else ("score-mid" if score>=50 else "score-low")

        col1, col2, col3 = st.columns([6, 1, 1])
        with col1:
            st.markdown(f"""
            <div class='creator-card' style='margin-bottom:8px'>
                <div style='display:flex;align-items:center;justify-content:space-between'>
                    <div>
                        <span style='font-size:14px;font-weight:700;color:#0D0E1A'>{name}</span>
                        <span class='niche-chip' style='margin-left:8px'>{niche}</span>
                    </div>
                    <span class='score-badge {score_cls}'>{score}%</span>
                </div>
            </div>""", unsafe_allow_html=True)
        with col2:
            if st.button("View →", key=f"saved_view_{pid}", use_container_width=True):
                st.session_state.selected_id = pid
                st.session_state.selected_type = "influencer" if role == "brand" else "brand"
                st.switch_page("pages/3_My_Profile.py")
        with col3:
            if st.button("✕", key=f"saved_rm_{pid}", use_container_width=True):
                st.session_state.saved.discard(pid)
                st.rerun()

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# ── REQUESTS SENT ──────────────────────────────────────────────────────────────
contacted_count = len(contacted)
st.markdown(f"<div class='sec-title'>REQUESTS SENT &nbsp; {contacted_count}</div>", unsafe_allow_html=True)

# try real API first, fall back to session state
api_requests = get_contact_requests(st.session_state.get("user_id", 1))

if not contacted and not api_requests:
    st.markdown("""
    <div style='background:#fff;border:1px solid #E4E5F0;border-radius:14px;padding:48px;text-align:center'>
        <div style='font-size:28px;margin-bottom:10px'>✉</div>
        <div style='font-size:14px;color:#9899B0'>No requests sent yet. Open a profile and reach out directly.</div>
    </div>""", unsafe_allow_html=True)
else:
    # show from session state (placeholder until backend ready)
    for pid in contacted:
        p = all_items.get(pid, {"name": f"Profile #{pid}", "total_score": 0})
        name  = p.get("name", f"Profile #{pid}")
        niche = p.get("niche") or p.get("industry","—")
        score = p.get("total_score", 0)
        score_cls = "score-high" if score>=75 else ("score-mid" if score>=50 else "score-low")

        col1, col2 = st.columns([7, 1])
        with col1:
            st.markdown(f"""
            <div class='creator-card' style='border-left:3px solid #6C63FF;margin-bottom:8px'>
                <div style='display:flex;align-items:center;justify-content:space-between'>
                    <div>
                        <span style='font-size:14px;font-weight:700;color:#0D0E1A'>{name}</span>
                        <span class='niche-chip' style='margin-left:8px'>{niche}</span>
                        <span style='background:#E0FBF4;color:#007A5A;font-size:11px;font-weight:600;
                                     padding:2px 8px;border-radius:10px;margin-left:6px'>Sent</span>
                    </div>
                    <span class='score-badge {score_cls}'>{score}%</span>
                </div>
                <div style='font-size:12px;color:#9899B0;margin-top:6px'>Awaiting response</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            if st.button("View →", key=f"cont_view_{pid}", use_container_width=True):
                st.session_state.selected_id = pid
                st.session_state.selected_type = "influencer" if role == "brand" else "brand"
                st.switch_page("pages/3_My_Profile.py")

    # show any real API requests
    for req in api_requests:
        st.markdown(f"""
        <div class='creator-card' style='border-left:3px solid #6C63FF;margin-bottom:8px'>
            <div style='font-size:14px;font-weight:700;color:#0D0E1A'>Request #{req.get('id','—')}</div>
            <div style='font-size:12px;color:#9899B0;margin-top:4px'>
                Status: {req.get('status','pending')} · {req.get('direction','')}
            </div>
        </div>""", unsafe_allow_html=True)