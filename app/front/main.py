"""
main.py — PairUp landing (home) page.
This is the FIRST page users see when they open the app.
Clicking "I'm a brand" / "I'm a creator" / "Browse marketplace" takes them
to the Discover page (pages/1_Discover.py).
The nav logo returns here; the avatar goes to the profile.
"""
import streamlit as st
from ui_core import inject_css, init_session, nav_header

st.set_page_config(
    page_title="PairUp — Where Brands Meet the Right Creators",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
init_session()

# ── top nav bar (shared) ──────────────────────────────────────────────────────
nav_header("home")

# ── landing-page-specific CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
.hero-wrap { max-width:680px; margin:56px auto 0; text-align:center; padding:0 24px; }
.hero-badge {
    display:inline-flex; align-items:center; gap:6px;
    background:#F0EFFE; color:#6C63FF; font-size:13px; font-weight:600;
    padding:6px 18px; border-radius:20px; border:1px solid #C5C2FF;
    margin-bottom:24px;
}
.hero-badge-dot { width:7px; height:7px; background:#6C63FF; border-radius:50%;
                  display:inline-block; }
.hero-title {
    font-size:44px; font-weight:800; color:#0D0E1A;
    line-height:1.15; letter-spacing:-1px; margin-bottom:16px;
}
.hero-title em { color:#6C63FF; font-style:normal; }
.hero-sub {
    font-size:16px; color:#5A5B72; line-height:1.6;
    margin:0 auto 32px; max-width:520px;
}

/* stats row */
.stat-hero {
    background:#fff; border:1px solid #E4E5F0;
    border-radius:12px; padding:22px 16px; text-align:center;
}
.stat-hero-v { font-size:28px; font-weight:800; color:#6C63FF; margin-bottom:4px; }
.stat-hero-k { font-size:12px; color:#5A5B72; }

/* how-it-works */
.how-section {
    background:#fff; border-top:1px solid #E4E5F0; border-bottom:1px solid #E4E5F0;
    padding:56px 24px; margin-top:56px;
}
.how-title { font-size:26px; font-weight:700; color:#0D0E1A; text-align:center;
             margin-bottom:8px; }
.how-sub   { font-size:14px; color:#5A5B72; text-align:center; margin-bottom:36px; }
.how-card {
    background:#F7F8FC; border:1px solid #E4E5F0;
    border-radius:12px; padding:20px; height:100%;
}
.how-num {
    width:30px; height:30px; border-radius:8px;
    background:#F0EFFE; color:#6C63FF; font-size:13px; font-weight:700;
    display:flex; align-items:center; justify-content:center; margin-bottom:12px;
}
.how-card h3 { font-size:14px; font-weight:700; color:#0D0E1A; margin-bottom:6px; }
.how-card p  { font-size:13px; color:#5A5B72; line-height:1.55; margin:0; }

/* split cards */
.split-section { max-width:900px; margin:0 auto; padding:56px 24px; }
.split-title { font-size:26px; font-weight:700; color:#0D0E1A; margin-bottom:8px; }
.split-sub   { font-size:14px; color:#5A5B72; margin-bottom:28px; }
.split-card {
    border-radius:14px; padding:26px; border:1px solid #E4E5F0;
    min-height: 280px;
}
.split-card.brand-card { background:linear-gradient(135deg,#F0EFFE 0%,#E8E6FF 100%); }
.split-card.creator-card { background:linear-gradient(135deg,#E0FBF4 0%,#D0F5EB 100%); }
.split-icon {
    width:44px; height:44px; border-radius:12px;
    display:flex; align-items:center; justify-content:center;
    margin-bottom:14px; font-size:20px; background:#fff;
}
.split-card h3 { font-size:16px; font-weight:700; color:#0D0E1A; margin-bottom:10px; }
.split-card ul { list-style:none; padding:0; margin:0 0 14px; }
.split-card ul li {
    font-size:13px; color:#5A5B72; padding:4px 0;
    display:flex; align-items:center; gap:8px;
}
.split-card ul li::before { content:''; width:5px; height:5px; border-radius:50%; flex-shrink:0; }
.split-card.brand-card ul li::before   { background:#6C63FF; }
.split-card.creator-card ul li::before { background:#00C896; }
</style>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
_, hero_col, _ = st.columns([1, 3, 1])
with hero_col:
    st.markdown("""
    <div class='hero-wrap'>
        <div class='hero-badge'>
            <span class='hero-badge-dot'></span>
            Smart matching · No agencies needed
        </div>
        <div class='hero-title'>
            Where brands meet<br>
            <em>the right creators</em>
        </div>
        <div class='hero-sub'>
            PairUp connects small businesses with micro-influencers using
            data-driven match scores — not guesswork. Find your perfect
            creative partner in minutes.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # CTA buttons
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("I'm a brand", type="primary", use_container_width=True,
                     key="cta_brand"):
            st.session_state.role = "brand"
            st.switch_page("pages/1_Discover.py")
    with b2:
        if st.button("I'm a creator", use_container_width=True,
                     key="cta_creator"):
            st.session_state.role = "creator"
            st.switch_page("pages/1_Discover.py")
    with b3:
        if st.button("Browse marketplace", use_container_width=True,
                     key="cta_browse"):
            st.switch_page("pages/1_Discover.py")

    # stats row
    st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown("""
        <div class='stat-hero'>
            <div class='stat-hero-v'>8</div>
            <div class='stat-hero-k'>Creators listed</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown("""
        <div class='stat-hero'>
            <div class='stat-hero-v'>5</div>
            <div class='stat-hero-k'>Brands seeking</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown("""
        <div class='stat-hero'>
            <div class='stat-hero-v'>$5.78</div>
            <div class='stat-hero-k'>Avg ROI per $1 spent</div>
        </div>
        """, unsafe_allow_html=True)

# ── HOW PAIRUP WORKS ──────────────────────────────────────────────────────────
st.markdown("""
<div class='how-section'>
    <div class='how-title'>How PairUp works</div>
    <div class='how-sub'>A transparent, scored marketplace — no black boxes</div>
</div>
""", unsafe_allow_html=True)

_, how_col, _ = st.columns([1, 6, 1])
with how_col:
    cards = st.columns(4)
    steps = [
        ("1", "Create your profile",
         "Brands describe their campaign. Creators share their audience, engagement, and past collabs."),
        ("2", "Get matched by score",
         "Our algorithm scores compatibility across niche, audience, engagement, and history — 0 to 100."),
        ("3", "Browse and filter",
         "Search with smart filters. Every result shows a transparent score breakdown so you know why."),
        ("4", "Connect directly",
         "Send a collab request or pitch directly. No intermediary, no agency fee."),
    ]
    for col, (n, title, desc) in zip(cards, steps):
        with col:
            st.markdown(f"""
            <div class='how-card'>
                <div class='how-num'>{n}</div>
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

# ── FOR BRANDS / FOR CREATORS ────────────────────────────────────────────────
_, split_col, _ = st.columns([1, 6, 1])
with split_col:
    st.markdown("<div style='height:56px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='split-title'>For brands &amp; creators</div>
    <div class='split-sub'>Purpose-built tools for each side of the marketplace.</div>
    """, unsafe_allow_html=True)

    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown("""
        <div class='split-card brand-card'>
            <div class='split-icon'>🏢</div>
            <h3>For brands</h3>
            <ul>
                <li>Filter by niche, location, engagement</li>
                <li>See a full match score breakdown</li>
                <li>Send collab requests directly</li>
                <li>Save favourite creators</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start as a brand", type="primary",
                     use_container_width=True, key="split_brand"):
            st.session_state.role = "brand"
            st.switch_page("pages/1_Discover.py")

    with sc2:
        st.markdown("""
        <div class='split-card creator-card'>
            <div class='split-icon' style='background:#C5F5E5'>✨</div>
            <h3>For creators</h3>
            <ul>
                <li>Get discovered by matching brands</li>
                <li>Receive inbound pitch requests</li>
                <li>Showcase your rate card and audience</li>
                <li>Track your deal pipeline</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start as a creator", use_container_width=True,
                     key="split_creator"):
            st.session_state.role = "creator"
            st.switch_page("pages/1_Discover.py")

    st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)