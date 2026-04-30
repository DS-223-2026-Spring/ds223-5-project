import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ui_core import inject_css, nav_header, init_session, score_bars, initials, INFLUENCERS, BRANDS, NICHES, FORMATS, INDUSTRIES, SIZES

st.set_page_config(page_title="My Profile · PairUp", page_icon="👤", layout="wide")
inject_css()
init_session()

role        = st.session_state.get("role", "brand")
user_id     = st.session_state.get("user_id", 1)
selected_id = st.session_state.get("selected_id")

nav_header('profile')

# ── decide what to show ────────────────────────────────────────────────────────
# if selected_id is set → viewing someone else's profile
# otherwise → viewing own profile
viewing_other = selected_id is not None

if viewing_other and role == "brand":
    profile = next((inf for inf in INFLUENCERS if inf["id"] == selected_id), None)
    if not profile:
        st.warning("Profile not found.")
        st.stop()

    # ── influencer profile view ────────────────────────────────────────────────
    av = initials(profile["name"])
    score = profile["total_score"]
    score_cls = "score-high" if score >= 75 else ("score-mid" if score >= 50 else "score-low")
    fmts = "".join(f"<span class='fmt-chip'>{f}</span>" for f in profile["formats"])

    if st.button("← Back to Discover"):
        st.session_state.selected_id = None
        st.switch_page("pages/1_Discover.py")

    st.markdown(f"""
    <div style='background:#fff;border:1px solid #E4E5F0;border-radius:14px;padding:28px;margin-bottom:20px'>
        <div style='display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px'>
            <div style='display:flex;align-items:center;gap:14px'>
                <div class='avatar' style='width:56px;height:56px;font-size:18px'>{av}</div>
                <div>
                    <div style='font-size:22px;font-weight:800;color:#0D0E1A'>{profile['name']}</div>
                    <div style='font-size:13px;color:#9899B0'>{profile['niche']} · {profile['location']}</div>
                </div>
            </div>
            <span class='score-badge {score_cls}' style='font-size:16px;padding:8px 18px'>{score}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # stats row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Followers", f"{profile['followers']/1000:.1f}K")
    c2.metric("Engagement", f"{profile['engagement']}%")
    c3.metric("Audience age", profile["age"])
    c4.metric("Rate", profile["rate"])

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # match score breakdown
    st.markdown("<div class='sec-title'>Match score breakdown</div>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div style='background:#fff;border:1px solid #E4E5F0;border-radius:12px;padding:18px'>", unsafe_allow_html=True)
        score_bars(profile["niche_score"], profile["audience_score"], profile["engagement_score"], profile["history_score"])
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # bio + formats
    st.markdown("<div class='sec-title'>About</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background:#F7F8FC;border:1px solid #E4E5F0;border-radius:10px;
                padding:16px;font-size:14px;color:#5A5B72;margin-bottom:16px'>
        {profile['bio']}
    </div>
    <div style='margin-bottom:20px'>{fmts}</div>
    """, unsafe_allow_html=True)

    # past collabs placeholder
    st.markdown("<div class='sec-title'>Past collaborations</div>", unsafe_allow_html=True)
    st.info("📌 Placeholder — will load from GET /past-collaborations once backend is connected.")

    # contact form
    st.markdown("<div class='sec-title'>Send a collaboration request</div>", unsafe_allow_html=True)
    already = profile["id"] in st.session_state.get("contacted", set())
    with st.form("contact_form"):
        msg = st.text_area("Message (optional)", placeholder="Introduce yourself and explain why this would be a great collab...", height=100)
        send = st.form_submit_button(
            "✅ Request already sent" if already else "📨 Send collaboration request",
            disabled=already, type="primary", use_container_width=True
        )
        if send and not already:
            st.session_state.contacted.add(profile["id"])
            st.success("Request sent!")
            st.rerun()

else:
    # ── OWN PROFILE ────────────────────────────────────────────────────────────
    st.session_state.selected_id = None

    if role == "brand":
        own = BRANDS[0]
        st.markdown(f"""
        <div style='font-size:26px;font-weight:800;color:#0D0E1A;margin-bottom:4px'>My profile</div>
        <div style='font-size:14px;color:#9899B0;margin-bottom:24px'>Your brand profile visible to creators on PairUp</div>
        """, unsafe_allow_html=True)

        # stats row
        s1, s2, s3 = st.columns(3)
        s1.metric("Creators matched", 8)
        s2.metric("Requests sent", len(st.session_state.get("contacted", set())))
        s3.metric("Saved", len(st.session_state.get("saved", set())))

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background:#fff;border:1px solid #E4E5F0;border-radius:14px;padding:28px'>
            <div style='font-size:11px;font-weight:700;color:#9899B0;text-transform:uppercase;
                        letter-spacing:.6px;margin-bottom:20px'>PROFILE DETAILS</div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div style='font-size:11px;color:#9899B0;margin-bottom:4px'>BRAND NAME</div>", unsafe_allow_html=True)
            brand_name = st.text_input("", value=own["name"], label_visibility="collapsed", key="bname")
            st.markdown("<div style='font-size:11px;color:#9899B0;margin-bottom:4px;margin-top:12px'>CAMPAIGN BUDGET</div>", unsafe_allow_html=True)
            budget = st.text_input("", value=f"${own['budget_min']:,}–${own['budget_max']:,}", label_visibility="collapsed", key="bbudget")
        with col2:
            st.markdown("<div style='font-size:11px;color:#9899B0;margin-bottom:4px'>INDUSTRY</div>", unsafe_allow_html=True)
            industry = st.selectbox("", INDUSTRIES, index=INDUSTRIES.index(own["industry"]) if own["industry"] in INDUSTRIES else 0, label_visibility="collapsed", key="bind")
            st.markdown("<div style='font-size:11px;color:#9899B0;margin-bottom:4px;margin-top:12px'>LOCATION</div>", unsafe_allow_html=True)
            location = st.text_input("", value=own["location"], label_visibility="collapsed", key="bloc")

        st.markdown("<div style='font-size:11px;color:#9899B0;margin-bottom:4px;margin-top:12px'>TARGET AUDIENCE</div>", unsafe_allow_html=True)
        target = st.text_input("", value=own["target"], label_visibility="collapsed", key="btarget")

        st.markdown("<div style='font-size:11px;color:#9899B0;margin-bottom:8px;margin-top:12px'>CREATOR PREFERENCES</div>", unsafe_allow_html=True)
        prefs = st.multiselect("", ["Fitness","Wellness","Running","Beauty","Tech","Food","Travel","Gaming","Reels","Stories","Long-form","Posts"], default=own["preferences"], label_visibility="collapsed", key="bprefs")

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button("Edit profile", type="primary"):
            st.info("Profile update will connect to PUT /brands/{id} once backend is ready.")

    else:
        own = INFLUENCERS[0]
        st.markdown(f"""
        <div style='font-size:26px;font-weight:800;color:#0D0E1A;margin-bottom:4px'>My profile</div>
        <div style='font-size:14px;color:#9899B0;margin-bottom:24px'>Your creator profile visible to brands on PairUp</div>
        """, unsafe_allow_html=True)

        s1, s2, s3 = st.columns(3)
        s1.metric("Brands matched", 4)
        s2.metric("Requests received", 0)
        s3.metric("Saved by brands", 0)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Handle", value=own["name"], key="iname")
            st.number_input("Follower count", value=own["followers"], key="ifol")
            st.text_input("Location", value=own["location"], key="iloc")
        with col2:
            st.selectbox("Primary niche", NICHES, index=NICHES.index(own["niche"]) if own["niche"] in NICHES else 0, key="iniche")
            st.number_input("Engagement rate (%)", value=own["engagement"], step=0.1, key="ieng")
            st.multiselect("Content formats", FORMATS, default=own["formats"], key="ifmt")

        st.text_area("Bio", value=own["bio"], height=100, key="ibio")

        if st.button("Save profile", type="primary"):
            st.info("Will connect to PUT /influencers/{id} once backend is ready.")
