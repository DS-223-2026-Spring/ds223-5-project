"""
ui_core.py — Shared CSS, nav header, and reusable UI components.
"""

import streamlit as st

# ── constants ──────────────────────────────────────────────────────────────────
NICHES     = ["Fitness","Wellness","Fashion","Food","Tech","Travel","Beauty","Gaming","Running","Lifestyle","Parenting"]
FORMATS    = ["Reels","Stories","Long-form","Posts"]
AGE_GROUPS = ["13–17","18–24","25–34","35+"]
INDUSTRIES = ["Fitness / Nutrition","Beauty / Skincare","Food / Organic","Tech / SaaS",
              "Travel / Lifestyle","Fashion","Gaming","Wellness","Productivity / SaaS"]
SIZES      = ["Startup","SMB","Enterprise"]
BUDGETS    = ["Under $1,000","$1,000–$5,000","$5,000–$15,000","$15,000+"]
COLLAB_CATS = ["Sportswear","Nutrition","Wellness","Skincare","Food","Tech",
               "Travel","Fashion","Beauty","Gaming","Finance","Productivity"]


def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    .stApp { background: #F7F8FC; }
    #MainMenu, footer { visibility: hidden; }
    [data-testid="stHeader"] { display: none; }
    [data-testid="stSidebar"] { display: none; }
    .block-container { padding-top: 0.5rem !important; }

    /* cards */
    .creator-card {
        background: #fff; border: 1px solid #E4E5F0; border-radius: 14px;
        padding: 20px; margin-bottom: 14px;
        box-shadow: 0 1px 4px rgba(108,99,255,.06); transition: box-shadow .15s;
    }
    .creator-card:hover { box-shadow: 0 4px 16px rgba(108,99,255,.12); }

    /* avatar */
    .avatar {
        width: 44px; height: 44px; border-radius: 50%;
        background: #F0EFFE; color: #6C63FF; font-size: 14px; font-weight: 700;
        display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0;
    }

    /* score badges */
    .score-badge { font-size: 13px; font-weight: 700; padding: 4px 12px; border-radius: 20px; border: 1.5px solid; }
    .score-high { background:#E0FBF4; color:#00A87D; border-color:#A0EDD8; }
    .score-mid  { background:#FFF8EC; color:#D48A00; border-color:#FFDFA0; }
    .score-low  { background:#FFF0F0; color:#CC3333; border-color:#FFCCCC; }

    /* chips */
    .niche-chip { display:inline-block; background:#F0EFFE; color:#4A42D6; font-size:11px; font-weight:600; padding:3px 12px; border-radius:20px; margin-right:4px; margin-bottom:4px; border:1px solid #C5C2FF; }
    .fmt-chip   { display:inline-block; background:#F7F8FC; color:#5A5B72; font-size:11px; padding:3px 10px; border-radius:6px; border:1px solid #E4E5F0; margin-right:4px; margin-top:4px; }

    /* stat labels */
    .stat-lbl { font-size:11px; color:#9899B0; text-transform:uppercase; letter-spacing:.5px; margin-bottom:4px; font-weight:600; }
    .stat-val  { font-size:16px; font-weight:700; color:#0D0E1A; }

    /* section title */
    .sec-title { font-size:11px; font-weight:700; color:#9899B0; text-transform:uppercase; letter-spacing:.6px; margin:20px 0 10px; }

    /* info box */
    .info-box {
        background:#fff; border:1px solid #E4E5F0; border-radius:10px;
        padding:14px 18px; margin-bottom:10px;
    }

    /* contact row */
    .contact-row {
        display:flex; justify-content:space-between; align-items:center;
        padding:10px 0; border-bottom:1px solid #F0F1F8; font-size:13px;
    }
    .contact-row:last-child { border-bottom: none; }
    .contact-lbl { font-size:11px; font-weight:700; color:#9899B0; text-transform:uppercase; letter-spacing:.5px; }
    .contact-val { color:#6C63FF; font-weight:600; }

    /* bar track */
    .bar-track { background:#E4E5F0; border-radius:4px; height:7px; overflow:hidden; margin-top:4px; }

    /* modal overlay simulation */
    .modal-box {
        background:#fff; border:1px solid #E4E5F0; border-radius:16px;
        padding:28px 32px; max-width:480px; margin:0 auto;
        box-shadow: 0 8px 32px rgba(0,0,0,.12);
    }
    .modal-title { font-size:18px; font-weight:800; color:#0D0E1A; margin-bottom:6px; }
    .modal-sub   { font-size:13px; color:#9899B0; margin-bottom:20px; }
    .form-lbl    { font-size:11px; font-weight:700; color:#9899B0; text-transform:uppercase; letter-spacing:.5px; margin-bottom:6px; }

    /* buttons */
    .stButton > button { border-radius:8px !important; font-weight:600 !important; font-size:13px !important; }
    /* logo button special style */
    [data-testid="stButton"] button[kind="secondary"]:has-text("PairUp"),
    div:first-child .stButton > button {
        background: transparent !important;
        border: none !important;
        color: #0D0E1A !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        padding: 4px 8px !important;
        box-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)


def init_session():
    defaults = {
        "role": "brand", "user_id": 1,
        "selected_id": None, "selected_type": None,
        "saved": set(), "contacted": set(),
        "show_onboarding": False,
        "ob_step": 0, "ob_role": None,
        "show_collab_modal": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def nav_header(active_page: str):
    role = st.session_state.get("role", "brand")

    logo, disc, match, prof, gap, brand_btn, creator_btn, av = st.columns([2,1.2,1.3,1.2,3,1,1,0.5])

    with logo:
        if st.button("🔗 PairUp", key=f"logo_btn_{active_page}",
                     help="Go to home page"):
            st.session_state.selected_id = None
            st.session_state.show_onboarding = False
            st.switch_page("main.py")

    with disc:
        if st.button("Discover", type="primary" if active_page == "discover" else "secondary",
                     use_container_width=True, key=f"nav_d_{active_page}"):
            st.session_state.selected_id = None
            st.switch_page("pages/1_Discover.py")

    with match:
        if st.button("My matches", type="primary" if active_page == "matches" else "secondary",
                     use_container_width=True, key=f"nav_m_{active_page}"):
            st.session_state.selected_id = None
            st.switch_page("pages/2_My_Matches.py")

    with prof:
        if st.button("My profile", type="primary" if active_page == "profile" else "secondary",
                     use_container_width=True, key=f"nav_p_{active_page}"):
            st.session_state.selected_id = None
            st.switch_page("pages/3_My_Profile.py")

    with brand_btn:
        if st.button("Brand", type="primary" if role == "brand" else "secondary",
                     use_container_width=True, key=f"nav_brand_{active_page}"):
            st.session_state.role = "brand"
            st.session_state.selected_id = None
            st.rerun()

    with creator_btn:
        if st.button("Creator", type="primary" if role == "creator" else "secondary",
                     use_container_width=True, key=f"nav_creator_{active_page}"):
            st.session_state.role = "creator"
            st.session_state.selected_id = None
            st.rerun()

    with av:
        st.markdown("""
        <div style='width:30px;height:30px;border-radius:50%;background:#F0EFFE;
                    border:2px solid #C5C2FF;display:flex;align-items:center;
                    justify-content:center;font-size:14px;margin-top:6px'>👤</div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin:4px 0 16px;border:none;border-top:1px solid #E4E5F0'>", unsafe_allow_html=True)


def score_badge(score: int) -> str:
    cls = "score-high" if score >= 75 else ("score-mid" if score >= 50 else "score-low")
    return f'<span class="score-badge {cls}">{score}%</span>'


def score_bars(niche, audience, engagement, history):
    labels = ["Niche 35%","Audience 30%","Engagement 25%","History 10%"]
    values = [niche, audience, engagement, history]
    colors = ["#6C63FF","#00C896","#F5A623","#FF5C5C"]
    cols = st.columns(4)
    for col, lbl, val, clr in zip(cols, labels, values, colors):
        with col:
            st.markdown(f"""
            <div style='font-size:11px;color:#5A5B72;margin-bottom:4px'>{lbl}</div>
            <div class='bar-track'>
                <div style='width:{val}%;background:{clr};height:100%;border-radius:4px'></div>
            </div>
            <div style='font-size:13px;font-weight:700;color:{clr};margin-top:4px'>{val}</div>
            """, unsafe_allow_html=True)


def initials(name: str) -> str:
    parts = name.replace("@","").split(".")
    return (parts[0][0]+parts[1][0]).upper() if len(parts) >= 2 else name.replace("@","")[:2].upper()