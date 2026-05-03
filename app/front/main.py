import streamlit as st
from ui_core import inject_css, init_session, nav_header, NICHES, FORMATS, COLLAB_CATS
from api import create_brand, create_influencer

st.set_page_config(
    page_title="PairUp — Where Brands Meet the Right Creators",
    page_icon="🔗", layout="wide", initial_sidebar_state="collapsed",
)
inject_css()
init_session()

# ── onboarding CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
.ob-prog-seg { height:4px; flex:1; border-radius:2px; background:#E4E5F0; display:inline-block; }
.ob-prog-seg.done { background:#6C63FF; }
.ob-step-lbl { font-size:11px;font-weight:700;color:#9899B0;text-transform:uppercase;letter-spacing:.6px;margin-bottom:8px; }
.ob-title { font-size:22px;font-weight:800;color:#0D0E1A;margin-bottom:6px; }
.ob-sub   { font-size:14px;color:#5A5B72;margin-bottom:24px;line-height:1.5; }
.role-card { border:2px solid #E4E5F0;border-radius:14px;padding:24px 20px;text-align:center;background:#fff; }
.role-card.selected { border-color:#6C63FF;background:#F8F7FF; }
.role-icon { width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:22px;margin:0 auto 12px; }
.role-name { font-size:15px;font-weight:700;color:#0D0E1A;margin-bottom:6px; }
.role-desc { font-size:12px;color:#9899B0;line-height:1.5; }
.success-circle { width:56px;height:56px;border-radius:50%;background:#F0EFFE;display:flex;align-items:center;justify-content:center;font-size:24px;margin:8px auto 16px; }
.match-summary { background:#F7F8FC;border:1px solid #E4E5F0;border-radius:12px;padding:18px 20px;margin-top:16px; }
.match-row { display:flex;justify-content:space-between;align-items:center;font-size:13px;color:#5A5B72;padding:6px 0;border-bottom:1px solid #F0F1F8; }
.match-row:last-child { border-bottom:none; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ONBOARDING WIZARD
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.show_onboarding:
    nav_header("home")
    step = st.session_state.ob_step

    _, col, _ = st.columns([1, 2, 1])
    with col:
        # progress bar
        segs = "".join(f'<span class="ob-prog-seg {"done" if i <= step else ""}"></span>' for i in range(4))
        st.markdown(f'<div style="display:flex;gap:4px;margin-bottom:24px">{segs}</div>', unsafe_allow_html=True)

        # ── step 0 — role ──────────────────────────────────────────────────────
        if step == 0:
            st.markdown("""<div class='ob-step-lbl'>STEP 1 OF 4</div>
            <div class='ob-title'>Welcome to PairUp</div>
            <div class='ob-sub'>The smart marketplace for brands and micro-influencers. Who are you?</div>""",
            unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                sel = st.session_state.ob_role == "brand"
                st.markdown(f"""<div class='role-card {"selected" if sel else ""}'>
                    <div class='role-icon' style='background:#E0DEFF'>🏢</div>
                    <div class='role-name'>Brand / Business</div>
                    <div class='role-desc'>Find creators for your campaigns and measure match quality before reaching out</div>
                </div>""", unsafe_allow_html=True)
                if st.button("Select Brand", use_container_width=True,
                             type="primary" if sel else "secondary", key="sel_brand"):
                    st.session_state.ob_role = "brand"
                    st.session_state.role = "brand"
                    st.rerun()
            with c2:
                sel = st.session_state.ob_role == "creator"
                st.markdown(f"""<div class='role-card {"selected" if sel else ""}'>
                    <div class='role-icon' style='background:#C5F5E5'>✨</div>
                    <div class='role-name'>Creator / Influencer</div>
                    <div class='role-desc'>Get discovered by the right brands and receive inbound collaboration opportunities</div>
                </div>""", unsafe_allow_html=True)
                if st.button("Select Creator", use_container_width=True,
                             type="primary" if sel else "secondary", key="sel_creator"):
                    st.session_state.ob_role = "creator"
                    st.session_state.role = "creator"
                    st.rerun()

            _, rc = st.columns([3, 1])
            with rc:
                if st.button("Continue →", type="primary", use_container_width=True,
                             key="ob0_next", disabled=st.session_state.ob_role is None):
                    st.session_state.ob_step = 1
                    st.rerun()

        # ── step 1 — basic info ────────────────────────────────────────────────
        elif step == 1:
            role = st.session_state.ob_role or "brand"
            if role == "brand":
                st.markdown("""<div class='ob-step-lbl'>STEP 2 OF 4</div>
                <div class='ob-title'>Tell us about your brand</div>
                <div class='ob-sub'>Help us personalise your match scores.</div>""", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("<div class='form-lbl'>BRAND NAME</div>", unsafe_allow_html=True)
                    st.text_input("", placeholder="e.g. FitFuel Nutrition", label_visibility="collapsed", key="ob_bname")
                    st.markdown("<div class='form-lbl'>LOCATION</div>", unsafe_allow_html=True)
                    st.text_input("", placeholder="e.g. Austin, US", label_visibility="collapsed", key="ob_bloc")
                    st.markdown("<div class='form-lbl'>CAMPAIGN BUDGET</div>", unsafe_allow_html=True)
                    st.selectbox("", ["Under $1,000","$1,000–$5,000","$5,000–$15,000","$15,000+"],
                                 label_visibility="collapsed", key="ob_budget")
                with c2:
                    st.markdown("<div class='form-lbl'>INDUSTRY / NICHE</div>", unsafe_allow_html=True)
                    st.text_input("", placeholder="e.g. Fitness, Tech", label_visibility="collapsed", key="ob_industry")
                    st.markdown("<div class='form-lbl'>COMPANY SIZE</div>", unsafe_allow_html=True)
                    st.selectbox("", ["Startup","SMB","Enterprise"], label_visibility="collapsed", key="ob_size")
                    st.markdown("<div class='form-lbl'>TARGET AUDIENCE</div>", unsafe_allow_html=True)
                    st.text_input("", placeholder="e.g. Women 18–34 into fitness",
                                 label_visibility="collapsed", key="ob_target")
            else:
                st.markdown("""<div class='ob-step-lbl'>STEP 2 OF 4</div>
                <div class='ob-title'>Tell us about yourself</div>
                <div class='ob-sub'>So brands can find and evaluate you accurately.</div>""", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("<div class='form-lbl'>YOUR HANDLE</div>", unsafe_allow_html=True)
                    st.text_input("", placeholder="@yourhandle", label_visibility="collapsed", key="ob_handle")
                    st.markdown("<div class='form-lbl'>FOLLOWER COUNT</div>", unsafe_allow_html=True)
                    st.text_input("", placeholder="e.g. 42000", label_visibility="collapsed", key="ob_followers")
                    st.markdown("<div class='form-lbl'>AUDIENCE PRIMARY AGE</div>", unsafe_allow_html=True)
                    st.selectbox("", ["13–17","18–24","25–34","35+"], label_visibility="collapsed", key="ob_age")
                    st.markdown("<div class='form-lbl'>LOCATION</div>", unsafe_allow_html=True)
                    st.text_input("", placeholder="e.g. New York, US", label_visibility="collapsed", key="ob_loc")
                with c2:
                    st.markdown("<div class='form-lbl'>PRIMARY NICHE</div>", unsafe_allow_html=True)
                    st.text_input("", placeholder="e.g. Fitness, Beauty", label_visibility="collapsed", key="ob_niche")
                    st.markdown("<div class='form-lbl'>ENGAGEMENT RATE (%)</div>", unsafe_allow_html=True)
                    st.text_input("", placeholder="e.g. 3.8", label_visibility="collapsed", key="ob_eng")
                    st.markdown("<div class='form-lbl'>GENDER SPLIT (% FEMALE)</div>", unsafe_allow_html=True)
                    st.text_input("", placeholder="e.g. 65", label_visibility="collapsed", key="ob_gender")
                    st.markdown("<div class='form-lbl'>RATE PER POST</div>", unsafe_allow_html=True)
                    st.text_input("", placeholder="e.g. $800–$1,500", label_visibility="collapsed", key="ob_rate")

            bc, _, nc = st.columns([1,3,1])
            with bc:
                if st.button("← Back", key="ob1_back", use_container_width=True):
                    st.session_state.ob_step = 0; st.rerun()
            with nc:
                if st.button("Continue →", type="primary", key="ob1_next", use_container_width=True):
                    st.session_state.ob_step = 2; st.rerun()

        # ── step 2 — preferences ───────────────────────────────────────────────
        elif step == 2:
            role = st.session_state.ob_role or "brand"
            if role == "brand":
                st.markdown("""<div class='ob-step-lbl'>STEP 3 OF 4</div>
                <div class='ob-title'>Define your ideal match</div>
                <div class='ob-sub'>Define your ideal creator so PairUp can calculate accurate match scores.</div>""", unsafe_allow_html=True)
                st.markdown("<div class='form-lbl'>CREATOR NICHES YOU WANT</div>", unsafe_allow_html=True)
                st.multiselect("", NICHES, label_visibility="collapsed", key="ob_niches")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("<div class='form-lbl'>MIN FOLLOWERS</div>", unsafe_allow_html=True)
                    st.text_input("", placeholder="e.g. 10,000", label_visibility="collapsed", key="ob_min_fol")
                with c2:
                    st.markdown("<div class='form-lbl'>MIN ENGAGEMENT RATE</div>", unsafe_allow_html=True)
                    st.text_input("", placeholder="e.g. 2%", label_visibility="collapsed", key="ob_min_eng")
                st.markdown("<div class='form-lbl'>PREFERRED CONTENT FORMATS</div>", unsafe_allow_html=True)
                st.multiselect("", FORMATS, label_visibility="collapsed", key="ob_formats")
                st.markdown("<div class='form-lbl'>TARGET AUDIENCE AGE</div>", unsafe_allow_html=True)
                st.multiselect("", ["13–17","18–24","25–34","35+"], label_visibility="collapsed", key="ob_ages")
            else:
                st.markdown("""<div class='ob-step-lbl'>STEP 3 OF 4</div>
                <div class='ob-title'>Define your ideal match</div>
                <div class='ob-sub'>Help brands understand your content style and past work.</div>""", unsafe_allow_html=True)
                st.markdown("<div class='form-lbl'>CONTENT FORMATS YOU CREATE</div>", unsafe_allow_html=True)
                st.multiselect("", FORMATS, label_visibility="collapsed", key="ob_creator_formats")
                st.markdown("<div class='form-lbl'>PAST COLLABORATION CATEGORIES</div>", unsafe_allow_html=True)
                st.multiselect("", COLLAB_CATS, label_visibility="collapsed", key="ob_past_collabs")
                st.markdown("<div class='form-lbl'>SHORT BIO (SHOWN TO BRANDS)</div>", unsafe_allow_html=True)
                st.text_area("", placeholder="Describe your content style and what makes you a great brand partner...",
                            height=100, label_visibility="collapsed", key="ob_bio")

            bc, _, nc = st.columns([1,3,1])
            with bc:
                if st.button("← Back", key="ob2_back", use_container_width=True):
                    st.session_state.ob_step = 1; st.rerun()
            with nc:
                if st.button("Continue →", type="primary", key="ob2_next", use_container_width=True):
                    st.session_state.ob_step = 3; st.rerun()

        # ── step 3 — success ───────────────────────────────────────────────────
        elif step == 3:
            role = st.session_state.ob_role or "brand"
            top = "@sara.fit — 93%" if role == "brand" else "FitFuel Nutrition — 89%"
            count = "8 creators" if role == "brand" else "5 brands"

            st.markdown(f"""
            <div class='ob-step-lbl'>STEP 4 OF 4</div>
            <div class='ob-title'>You're all set</div>
            <div class='ob-sub'>PairUp has processed your profile and found your first matches.</div>
            <div style='text-align:center;margin:20px 0'>
                <div class='success-circle'>✓</div>
                <div style='font-size:15px;font-weight:700;color:#0D0E1A'>Profile created successfully</div>
            </div>
            <div class='match-summary'>
                <div style='font-size:11px;font-weight:700;color:#9899B0;text-transform:uppercase;letter-spacing:.6px;margin-bottom:10px'>MATCH SUMMARY</div>
                <div class='match-row'><span>Profiles in database</span><span style='font-weight:700;color:#0D0E1A'>{count}</span></div>
                <div class='match-row'><span>Your top match</span><span style='color:#6C63FF;font-weight:700'>{top}</span></div>
                <div class='match-row'><span>Avg match score</span><span style='font-weight:700;color:#0D0E1A'>72%</span></div>
            </div>
            """, unsafe_allow_html=True)

            bc, _, nc = st.columns([1,3,1])
            with bc:
                if st.button("← Back", key="ob3_back", use_container_width=True):
                    st.session_state.ob_step = 2; st.rerun()
            with nc:
                if st.button("Go to marketplace", type="primary", key="ob3_finish", use_container_width=True):
                    st.session_state.show_onboarding = False
                    st.switch_page("pages/1_Discover.py")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════
nav_header("home")
st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

_, center, _ = st.columns([1,2,1])
with center:
    st.markdown("""
    <div style='text-align:center'>
        <div style='display:inline-flex;align-items:center;gap:6px;background:#F0EFFE;color:#6C63FF;
                    font-size:13px;font-weight:600;padding:6px 18px;border-radius:20px;
                    border:1px solid #C5C2FF;margin-bottom:24px'>
            <span style='width:7px;height:7px;background:#6C63FF;border-radius:50%;display:inline-block'></span>
            Smart matching · No agencies needed
        </div>
        <div style='font-size:44px;font-weight:800;color:#0D0E1A;line-height:1.15;letter-spacing:-1px;margin-bottom:16px'>
            Where brands meet<br><span style='color:#6C63FF'>the right creators</span>
        </div>
        <div style='font-size:16px;color:#5A5B72;line-height:1.6;margin-bottom:36px'>
            PairUp connects small businesses with micro-influencers using
            data-driven match scores — not guesswork. Find your perfect creative partner in minutes.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏢  I'm a brand", use_container_width=True, type="primary"):
            st.session_state.role = "brand"; st.session_state.ob_role = "brand"
            st.session_state.ob_step = 0; st.session_state.show_onboarding = True; st.session_state.ob_submitted = False; st.rerun()
    with c2:
        if st.button("✨  I'm a creator", use_container_width=True):
            st.session_state.role = "creator"; st.session_state.ob_role = "creator"
            st.session_state.ob_step = 0; st.session_state.show_onboarding = True; st.session_state.ob_submitted = False; st.rerun()
    with c3:
        if st.button("🔍  Browse marketplace", use_container_width=True):
            st.switch_page("pages/1_Discover.py")

# stats
st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)
_, s1, s2, s3, _ = st.columns([1,2,2,2,1])
for col, val, lbl in [(s1,"50","Creators listed"),(s2,"20","Brands seeking"),(s3,"$5.78","Avg ROI per $1 spent")]:
    with col:
        st.markdown(f"""<div style='background:#fff;border:1px solid #E4E5F0;border-radius:14px;padding:24px;text-align:center'>
            <div style='font-size:30px;font-weight:800;color:#6C63FF;margin-bottom:4px'>{val}</div>
            <div style='font-size:13px;color:#5A5B72'>{lbl}</div></div>""", unsafe_allow_html=True)

# how it works
st.markdown("<div style='height:56px'></div>", unsafe_allow_html=True)
st.markdown("""<div style='text-align:center;margin-bottom:32px'>
    <div style='font-size:26px;font-weight:800;color:#0D0E1A;margin-bottom:6px'>How PairUp works</div>
    <div style='font-size:14px;color:#5A5B72'>A transparent, scored marketplace — no black boxes</div>
</div>""", unsafe_allow_html=True)

h1,h2,h3,h4 = st.columns(4)
for col,num,title,desc,bg,clr in [
    (h1,"1","Create your profile",  "Brands describe their campaign. Creators share their audience, engagement, and past collabs.","#F0EFFE","#6C63FF"),
    (h2,"2","Get matched by score", "Our algorithm scores compatibility across niche, audience, engagement, and history — 0 to 100.","#E0FBF4","#00A87D"),
    (h3,"3","Browse and filter",    "Search with smart filters. Every result shows a transparent score breakdown so you know why.","#FFF8EC","#D48A00"),
    (h4,"4","Connect directly",     "Send a collab request or pitch directly. No intermediary, no agency fee.","#FFF0F0","#CC3333"),
]:
    with col:
        st.markdown(f"""<div style='background:#F7F8FC;border:1px solid #E4E5F0;border-radius:12px;padding:20px'>
            <div style='width:32px;height:32px;border-radius:8px;background:{bg};color:{clr};
                        font-size:14px;font-weight:700;display:flex;align-items:center;justify-content:center;margin-bottom:12px'>{num}</div>
            <div style='font-size:14px;font-weight:700;color:#0D0E1A;margin-bottom:6px'>{title}</div>
            <div style='font-size:13px;color:#5A5B72;line-height:1.55'>{desc}</div></div>""", unsafe_allow_html=True)

# for brands / creators
st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)
bl, br = st.columns(2)
with bl:
    st.markdown("""<div style='background:linear-gradient(135deg,#F0EFFE,#E8E6FF);border:1px solid #E4E5F0;border-radius:14px;padding:28px'>
        <div style='font-size:32px;margin-bottom:12px'>🏢</div>
        <div style='font-size:18px;font-weight:700;color:#0D0E1A;margin-bottom:14px'>For brands</div>
        <div style='font-size:13px;color:#5A5B72;padding:4px 0'>🔵 Filter by niche, location, engagement</div>
        <div style='font-size:13px;color:#5A5B72;padding:4px 0'>🔵 See a full match score breakdown</div>
        <div style='font-size:13px;color:#5A5B72;padding:4px 0'>🔵 Send collab requests directly</div>
        <div style='font-size:13px;color:#5A5B72;padding:4px 0'>🔵 Save favourite creators</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    if st.button("Start as a brand", type="primary", use_container_width=True):
        st.session_state.role="brand"; st.session_state.ob_role="brand"
        st.session_state.ob_step=0; st.session_state.show_onboarding=True; st.rerun()

with br:
    st.markdown("""<div style='background:linear-gradient(135deg,#E0FBF4,#D0F5EB);border:1px solid #E4E5F0;border-radius:14px;padding:28px'>
        <div style='font-size:32px;margin-bottom:12px'>✨</div>
        <div style='font-size:18px;font-weight:700;color:#0D0E1A;margin-bottom:14px'>For creators</div>
        <div style='font-size:13px;color:#5A5B72;padding:4px 0'>🟢 Get discovered by matching brands</div>
        <div style='font-size:13px;color:#5A5B72;padding:4px 0'>🟢 Receive inbound pitch requests</div>
        <div style='font-size:13px;color:#5A5B72;padding:4px 0'>🟢 Showcase your rate card and audience</div>
        <div style='font-size:13px;color:#5A5B72;padding:4px 0'>🟢 Track your deal pipeline</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    if st.button("Start as a creator", use_container_width=True):
        st.session_state.role="creator"; st.session_state.ob_role="creator"
        st.session_state.ob_step=0; st.session_state.show_onboarding=True; st.rerun()