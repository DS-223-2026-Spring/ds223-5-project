"""
ui_core.py — shared CSS, nav header, placeholder data, and helpers.
"""
import streamlit as st

# ── colors ─────────────────────────────────────────────────────────────────────
PURPLE = "#6C63FF"
TEAL   = "#00C896"
AMBER  = "#F5A623"
CORAL  = "#FF5C5C"

# ── constants ──────────────────────────────────────────────────────────────────
NICHES     = ["Fitness","Wellness","Fashion","Food","Tech","Travel","Beauty","Gaming","Running","Lifestyle"]
FORMATS    = ["Reels","Stories","Long-form","Posts"]
AGE_GROUPS = ["13–17","18–24","25–34","35+"]
INDUSTRIES = ["Fitness","Beauty","Tech","Food","Travel","Fashion","Gaming","Wellness"]
SIZES      = ["Startup","SMB","Enterprise"]

# ── global CSS ─────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    .stApp { background: #F7F8FC; }
    #MainMenu, footer { visibility: hidden; }
    [data-testid="stHeader"] { display: none; }
    [data-testid="stSidebar"] { display: none; }

    /* tighten default top padding so our nav sits near the top */
    .block-container { padding-top: 1.2rem !important; }

    /* filter sidebar labels (Discover page) */
    .filter-label {
        font-size: 10px; font-weight: 700; color: #9899B0;
        text-transform: uppercase; letter-spacing: .9px;
        margin: 14px 0 6px;
    }

    /* ── cards ── */
    .creator-card {
        background: #fff; border: 1px solid #E4E5F0;
        border-radius: 14px; padding: 20px; margin-bottom: 14px;
        box-shadow: 0 1px 4px rgba(108,99,255,.06);
        transition: box-shadow .15s;
    }
    .creator-card:hover { box-shadow: 0 4px 16px rgba(108,99,255,.12); }
    .avatar {
        width: 44px; height: 44px; border-radius: 50%;
        background: #F0EFFE; color: #6C63FF; font-size: 14px; font-weight: 700;
        display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0;
    }
    .score-badge {
        font-size: 13px; font-weight: 700;
        padding: 4px 12px; border-radius: 20px; border: 1.5px solid;
    }
    .score-high { background:#E0FBF4; color:#00A87D; border-color:#A0EDD8; }
    .score-mid  { background:#FFF8EC; color:#D48A00; border-color:#FFDFA0; }
    .score-low  { background:#FFF0F0; color:#CC3333; border-color:#FFCCCC; }
    .niche-chip {
        display:inline-block; background:#F0EFFE; color:#4A42D6;
        font-size:11px; font-weight:600; padding:2px 10px;
        border-radius:20px; margin-right:4px;
    }
    .fmt-chip {
        display:inline-block; background:#F7F8FC; color:#5A5B72;
        font-size:11px; padding:3px 10px; border-radius:6px;
        border:1px solid #E4E5F0; margin-right:4px; margin-top:4px;
    }
    .stat-lbl { font-size:12px; color:#9899B0; margin-bottom:2px; }
    .stat-val { font-size:14px; font-weight:700; color:#0D0E1A; }
    .sec-title {
        font-size:11px; font-weight:700; color:#9899B0;
        text-transform:uppercase; letter-spacing:.6px; margin:20px 0 10px;
    }
    .bar-track {
        background:#E4E5F0; border-radius:4px;
        height:7px; overflow:hidden; margin-top:4px;
    }

    /* buttons */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    /* 🔥 LOGO BUTTON (remove rectangle) */
    div[data-testid="stButton"] > button[kind="secondary"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        color: #0D0E1A !important;
    }

    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        color: #6C63FF !important;
    }
    /* avatar button styling */
    button[data-testid="baseButton-logo_btn"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center;
        gap: 6px;
    
        font-size: 16px !important;
        font-weight: 800 !important;
        color: #0D0E1A !important;
    }
    
    /* make "Up" purple */
    button[data-testid="baseButton-logo_btn"]::after {
        content: "Up";
        color: #6C63FF;
        margin-left: 2px;
    }
    
    /* remove duplicate "Up" from original text */
    button[data-testid="baseButton-logo_btn"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* hover effect */
    button[data-testid="baseButton-logo_btn"]:hover {
        color: #6C63FF !important;
    }
    
    
    button[data-testid="baseButton-avatar_btn"] {
        width: 36px !important;
        height: 36px !important;
        border-radius: 50% !important;
    
        background: #F0EFFE !important;
        border: 2px solid #C5C2FF !important;
    
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    
        padding: 0 !important;
        font-size: 18px !important;
    
        transition: all 0.2s ease-in-out;
    }
    
    button[data-testid="baseButton-avatar_btn"]:hover {
        background: #E8E6FF !important;
        transform: scale(1.05);
}
    
    
    </style>
    """, unsafe_allow_html=True)


# ── nav header ─────────────────────────────────────────────────────────────────
def nav_header(active_page: str):
    """Pure Streamlit nav bar — no HTML-wrapping hacks, fully functional."""
    role = st.session_state.get("role", "brand")

    # nav row: logo | Discover | My matches | My profile | gap | Brand | Creator | avatar
    logo_col, disc_col, match_col, prof_col, gap_col, brand_col, creator_col, av_col = \
        st.columns([2, 1, 1, 1, 4, 1, 1, 0.5])

    with logo_col:
        if st.button("🔗 PairUp", key="logo_btn"):
            st.switch_page("main.py")




    with disc_col:
        t = "primary" if active_page == "discover" else "secondary"
        if st.button("Discover", type=t, use_container_width=True,
                     key=f"nav_disc_{active_page}"):
            st.switch_page("pages/1_Discover.py")

    with match_col:
        t = "primary" if active_page == "matches" else "secondary"
        if st.button("My matches", type=t, use_container_width=True,
                     key=f"nav_match_{active_page}"):
            st.switch_page("pages/2_My_Matches.py")

    with prof_col:
        t = "primary" if active_page == "profile" else "secondary"
        if st.button("My profile", type=t, use_container_width=True,
                     key=f"nav_prof_{active_page}"):
            st.switch_page("pages/3_My_Profile.py")

    with brand_col:
        t = "primary" if role == "brand" else "secondary"
        if st.button("Brand", type=t, use_container_width=True,
                     key=f"nav_brand_{active_page}"):
            st.session_state.role = "brand"
            st.rerun()

    with creator_col:
        t = "primary" if role == "creator" else "secondary"
        if st.button("Creator", type=t, use_container_width=True,
                     key=f"nav_creator_{active_page}"):
            st.session_state.role = "creator"
            st.rerun()

    with av_col:
        if st.button("👤", key="avatar_btn"):
            st.switch_page("pages/3_My_Profile.py")

    st.markdown(
        "<hr style='margin:4px 0 16px;border:none;border-top:1px solid #E4E5F0'>",
        unsafe_allow_html=True,
    )


# ── session init ───────────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "role": "brand",
        "user_id": 1,
        "selected_id": None,
        "saved": set(),
        "contacted": set(),
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── helpers ────────────────────────────────────────────────────────────────────
def score_badge(score: int) -> str:
    cls = "score-high" if score >= 75 else ("score-mid" if score >= 50 else "score-low")
    return f'<span class="score-badge {cls}">{score}%</span>'


def initials(name: str) -> str:
    parts = name.replace("@", "").split(".")
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return name.replace("@", "")[:2].upper()


def score_bars(niche, audience, engagement, history):
    labels = ["Niche 35%", "Audience 30%", "Engagement 25%", "History 10%"]
    values = [niche, audience, engagement, history]
    colors = [PURPLE, TEAL, AMBER, CORAL]
    cols = st.columns(4)
    for col, lbl, val, clr in zip(cols, labels, values, colors):
        with col:
            st.markdown(f"""
            <div style='font-size:11px;color:#5A5B72;margin-bottom:4px'>{lbl}</div>
            <div class='bar-track'>
                <div style='width:{val}%;background:{clr};height:100%;border-radius:4px'></div>
            </div>
            <div style='font-size:12px;font-weight:700;color:{clr};margin-top:4px'>{val}</div>
            """, unsafe_allow_html=True)


# ── placeholder data ───────────────────────────────────────────────────────────
INFLUENCERS = [
    {"id":1,"name":"@sara.fit",       "niche":"Fitness", "location":"New York, US",      "followers":42400,"engagement":3.8,"age":"18–34","formats":["Reels","Stories"],     "rate":"$800–$1,500/post", "total_score":93,"niche_score":95,"audience_score":92,"engagement_score":96,"history_score":80,"bio":"Fitness & wellness creator. NYC-based. Brand partner for 3+ years."},
    {"id":2,"name":"@move.with.mia",  "niche":"Wellness","location":"Brooklyn, US",      "followers":27200,"engagement":4.1,"age":"18–34","formats":["Reels","Stories"],     "rate":"$500–$900/post",  "total_score":81,"niche_score":82,"audience_score":85,"engagement_score":88,"history_score":60,"bio":"Mindful movement and wellness. Brooklyn vibes."},
    {"id":3,"name":"@danielruns",     "niche":"Running", "location":"Jersey City, US",   "followers":61000,"engagement":1.9,"age":"25–34","formats":["Posts","Stories"],     "rate":"$1,200–$2,000/post","total_score":62,"niche_score":68,"audience_score":60,"engagement_score":55,"history_score":72,"bio":"Marathon runner & coach. Jersey City represent."},
    {"id":4,"name":"@nourish.nina",   "niche":"Food",    "location":"Los Angeles, US",   "followers":38900,"engagement":3.3,"age":"25–34","formats":["Reels","Long-form"],   "rate":"$700–$1,200/post","total_score":55,"niche_score":50,"audience_score":58,"engagement_score":62,"history_score":45,"bio":"Clean eating and nutrition recipes. LA food scene."},
    {"id":5,"name":"@glowwithgrace",  "niche":"Beauty",  "location":"Chicago, US",       "followers":54000,"engagement":2.9,"age":"18–24","formats":["Reels","Stories","Long-form"],"rate":"$900–$1,500/post","total_score":49,"niche_score":45,"audience_score":52,"engagement_score":50,"history_score":44,"bio":"Beauty & skincare tutorials. Chicago-based creator."},
    {"id":6,"name":"@levelup.leo",    "niche":"Gaming",  "location":"Austin, US",        "followers":95000,"engagement":3.5,"age":"13–24","formats":["Long-form","Reels"],   "rate":"$2,500–$5,000/post","total_score":46,"niche_score":40,"audience_score":48,"engagement_score":58,"history_score":30,"bio":"Gaming content and esports coverage."},
    {"id":7,"name":"@passport.alex",  "niche":"Travel",  "location":"Miami, US",         "followers":73000,"engagement":2.2,"age":"25–34","formats":["Reels","Stories"],     "rate":"$1,500–$3,000/post","total_score":44,"niche_score":42,"audience_score":46,"engagement_score":40,"history_score":50,"bio":"Full-time traveler. 60+ countries. Miami home base."},
    {"id":8,"name":"@techbytomas",    "niche":"Tech",    "location":"San Francisco, US", "followers":88000,"engagement":1.4,"age":"18–34","formats":["Long-form","Posts"],   "rate":"$2,000–$4,000/post","total_score":33,"niche_score":30,"audience_score":35,"engagement_score":32,"history_score":28,"bio":"Tech reviews and startup culture. SF-based."},
]

BRANDS = [
    {"id":1,"name":"FitFuel Nutrition","industry":"Fitness","size":"SMB",      "budget_min":3000, "budget_max":8000, "target":"Active adults 20–35, fitness-focused","total_score":92,"niche_score":95,"audience_score":90,"engagement_score":88,"history_score":80,"location":"Austin, US",      "preferences":["Fitness","Wellness","Running","Reels","Stories"]},
    {"id":2,"name":"GlowBox",          "industry":"Beauty", "size":"Startup",  "budget_min":1000, "budget_max":5000, "target":"Women 18–28, skincare & beauty",     "total_score":87,"niche_score":90,"audience_score":85,"engagement_score":82,"history_score":78,"location":"New York, US",    "preferences":["Beauty","Fashion","Reels"]},
    {"id":3,"name":"TechNest",         "industry":"Tech",   "size":"Enterprise","budget_min":15000,"budget_max":50000,"target":"Men 25–40, tech enthusiasts",        "total_score":75,"niche_score":72,"audience_score":78,"engagement_score":70,"history_score":68,"location":"San Francisco, US","preferences":["Tech","Gaming","Long-form"]},
    {"id":4,"name":"Wanderly",         "industry":"Travel", "size":"SMB",      "budget_min":3000, "budget_max":10000,"target":"Adults 25–40, frequent travelers",    "total_score":80,"niche_score":78,"audience_score":82,"engagement_score":79,"history_score":72,"location":"Miami, US",       "preferences":["Travel","Lifestyle","Reels","Stories"]},
]