import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ui_core import inject_css, nav_header, init_session, score_bars, initials, NICHES, FORMATS, INDUSTRIES, SIZES
from api import get_influencer, get_brand, get_past_collaborations, send_contact, update_influencer, update_brand, INFLUENCERS, BRANDS

st.set_page_config(page_title="My Profile · PairUp", page_icon="👤", layout="wide")
inject_css()
init_session()

role        = st.session_state.get("role", "brand")
user_id     = st.session_state.get("user_id", 1)
selected_id = st.session_state.get("selected_id")
selected_type = st.session_state.get("selected_type")

nav_header("profile")

# ── collab modal helper ────────────────────────────────────────────────────────
def collab_modal(profile: dict, is_brand_profile: bool):
    """Show collab request / pitch form."""
    name = profile.get("name","")

    if is_brand_profile:
        title = f"Send pitch to {name}"
        sub   = f"Tell {name} about yourself and what you can offer."
    else:
        title = f"Collab request to {name}"
        sub   = f"Tell {name} about your brand and campaign."

    _, modal_col, _ = st.columns([1, 2, 1])
    with modal_col:
        st.markdown(f"""
        <div style='background:#fff;border:1px solid #E4E5F0;border-radius:16px;
                    padding:28px 32px;box-shadow:0 4px 20px rgba(0,0,0,.10);margin-bottom:0px'>
            <div style='font-size:18px;font-weight:800;color:#0D0E1A;margin-bottom:4px'>{title}</div>
            <div style='font-size:13px;color:#9899B0;margin-bottom:0'>{sub}</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("collab_form", clear_on_submit=True):
            if is_brand_profile:
                st.markdown("<div class='form-lbl'>YOUR HANDLE</div>", unsafe_allow_html=True)
                your_handle = st.text_input("", placeholder="@yourhandle", label_visibility="collapsed", key="modal_handle")
                st.markdown("<div class='form-lbl'>NICHE / CONTENT STYLE</div>", unsafe_allow_html=True)
                your_niche = st.text_input("", placeholder="e.g. Fitness, Wellness", label_visibility="collapsed", key="modal_niche")
                st.markdown("<div class='form-lbl'>RATE PER POST</div>", unsafe_allow_html=True)
                your_rate = st.text_input("", placeholder="e.g. $800–$1,500", label_visibility="collapsed", key="modal_rate")
                st.markdown("<div class='form-lbl'>YOUR CONTACT EMAIL</div>", unsafe_allow_html=True)
                your_email = st.text_input("", placeholder="you@email.com", label_visibility="collapsed", key="modal_email")
            else:
                own_brand = BRANDS[0]
                st.markdown("<div class='form-lbl'>YOUR BRAND NAME</div>", unsafe_allow_html=True)
                your_brand = st.text_input("", value=own_brand["name"], label_visibility="collapsed", key="modal_brand")
                st.markdown("<div class='form-lbl'>CAMPAIGN / COLLAB IDEA</div>", unsafe_allow_html=True)
                campaign_idea = st.text_area("", placeholder="Describe your campaign idea, timeline, and what you're looking for...",
                                            height=100, label_visibility="collapsed", key="modal_idea")
                st.markdown("<div class='form-lbl'>BUDGET RANGE</div>", unsafe_allow_html=True)
                budget = st.text_input("", placeholder="e.g. $2,000–$5,000", label_visibility="collapsed", key="modal_budget")
                st.markdown("<div class='form-lbl'>YOUR CONTACT EMAIL</div>", unsafe_allow_html=True)
                contact_email = st.text_input("", value=own_brand["email"], label_visibility="collapsed", key="modal_email")

            col_cancel, col_send = st.columns(2)
            with col_cancel:
                cancel = st.form_submit_button("Cancel", use_container_width=True)
            with col_send:
                send = st.form_submit_button("Send request", type="primary", use_container_width=True)

            if cancel:
                st.session_state.show_collab_modal = False
                st.rerun()

            if send:
                if is_brand_profile:
                    direction = "influencer_to_brand"
                    brand_id  = selected_id
                    inf_id    = user_id
                    msg = f"Handle: {your_handle}, Niche: {your_niche}, Rate: {your_rate}"
                else:
                    direction = "brand_to_influencer"
                    brand_id  = user_id
                    inf_id    = selected_id
                    msg = campaign_idea
                    budget_val = budget

                result = send_contact(
                    brand_id=brand_id,
                    influencer_id=inf_id,
                    direction=direction,
                    message=msg,
                )
                st.session_state.contacted.add(selected_id)
                st.session_state.show_collab_modal = False
                st.success("Request sent successfully! 🎉")
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# VIEWING SOMEONE ELSE'S PROFILE
# ══════════════════════════════════════════════════════════════════════════════
if selected_id is not None:

    # show modal if triggered
    if st.session_state.get("show_collab_modal"):
        is_brand_profile = selected_type == "brand"
        profile = get_brand(selected_id) if is_brand_profile else get_influencer(selected_id)
        if profile:
            collab_modal(profile, is_brand_profile)
        st.stop()

    # ── INFLUENCER DETAIL (brand viewing a creator) ────────────────────────────
    if selected_type == "influencer" or role == "brand":
        profile = get_influencer(selected_id)
        if not profile:
            st.error("Profile not found.")
            st.stop()

        if st.button("← Back to results"):
            st.session_state.selected_id = None
            st.switch_page("pages/1_Discover.py")

        av    = initials(profile["name"])
        score = profile["total_score"]
        score_cls = "score-high" if score>=75 else ("score-mid" if score>=50 else "score-low")

        # header
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#F0EFFE,#E8E6FF);
                    border:1px solid #E4E5F0;border-radius:14px;padding:24px 28px;margin-bottom:20px'>
            <div style='display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px'>
                <div style='display:flex;align-items:center;gap:14px'>
                    <div class='avatar' style='width:52px;height:52px;font-size:17px'>{av}</div>
                    <div>
                        <div style='font-size:22px;font-weight:800;color:#0D0E1A'>{profile['name']}</div>
                        <div style='font-size:13px;color:#5A5B72'>{profile['niche']} · {profile['location']}</div>
                    </div>
                </div>
                <span class='score-badge {score_cls}' style='font-size:15px;padding:8px 18px'>{score}% match</span>
            </div>
        </div>""", unsafe_allow_html=True)

        # audience & reach
        st.markdown("<div class='sec-title'>AUDIENCE & REACH</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            for lbl, val in [("FOLLOWERS", f"{profile['followers']/1000:.1f}K"),
                             ("PRIMARY AGE GROUP", profile['age']),
                             ("LOCATION", profile['location'])]:
                st.markdown(f"<div class='info-box'><div class='stat-lbl'>{lbl}</div><div class='stat-val'>{val}</div></div>", unsafe_allow_html=True)
        with c2:
            for lbl, val in [("ENGAGEMENT RATE", f"{profile['engagement']}%"),
                             ("GENDER SPLIT", profile.get('gender','—')),
                             ("CONTENT FORMATS", ', '.join(profile['formats']))]:
                st.markdown(f"<div class='info-box'><div class='stat-lbl'>{lbl}</div><div class='stat-val'>{val}</div></div>", unsafe_allow_html=True)

        # match score breakdown
        st.markdown("<div class='sec-title'>MATCH SCORE BREAKDOWN</div>", unsafe_allow_html=True)
        score_bars(profile["niche_score"], profile["audience_score"],
                   profile["engagement_score"], profile["history_score"])

        # past collaborations
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='sec-title'>PAST COLLABORATIONS</div>", unsafe_allow_html=True)
        past = get_past_collaborations(selected_id)
        if past:
            for p in past:
                st.markdown(f"""
                <div style='background:#fff;border:1px solid #E4E5F0;border-radius:10px;
                            padding:14px 18px;margin-bottom:8px;
                            display:flex;justify-content:space-between;align-items:center'>
                    <div>
                        <div style='font-size:14px;font-weight:700;color:#0D0E1A'>{p['brand']}</div>
                        <div style='font-size:12px;color:#9899B0'>{p['category']}</div>
                    </div>
                    <div style='font-size:13px;color:#9899B0'>{p['year']}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<div style='font-size:13px;color:#9899B0;padding:12px 0'>No past collaborations on record yet.</div>", unsafe_allow_html=True)

        # contact & rates
        st.markdown("<div class='sec-title'>CONTACT & RATES</div>", unsafe_allow_html=True)
        handle = profile["name"].replace("@","")
        st.markdown(f"""
        <div style='background:#fff;border:1px solid #E4E5F0;border-radius:10px;padding:4px 18px'>
            <div class='contact-row'><span class='contact-lbl'>EMAIL</span><span class='contact-val'>{handle}@email.com</span></div>
            <div class='contact-row'><span class='contact-lbl'>INSTAGRAM</span><span class='contact-val'>{profile['name']}</span></div>
            <div class='contact-row'><span class='contact-lbl'>RATE CARD</span><span class='contact-val'>{profile['rate']}</span></div>
        </div>""", unsafe_allow_html=True)

        # action buttons
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        already_saved     = selected_id in st.session_state.get("saved", set())
        already_contacted = selected_id in st.session_state.get("contacted", set())

        col1, col2 = st.columns(2)
        with col1:
            label = "★ Saved" if already_saved else "☆ Save creator"
            if st.button(label, use_container_width=True, key="save_btn"):
                st.session_state.saved.add(selected_id)
                st.rerun()
        with col2:
            if already_contacted:
                st.button("✅ Request sent", use_container_width=True, disabled=True, key="sent_btn")
            else:
                if st.button("Send collab request", type="primary", use_container_width=True, key="collab_btn"):
                    st.session_state.show_collab_modal = True
                    st.rerun()

    # ── BRAND DETAIL (creator viewing a brand) ─────────────────────────────────
    else:
        profile = get_brand(selected_id)
        if not profile:
            st.error("Profile not found.")
            st.stop()

        if st.button("← Back to results"):
            st.session_state.selected_id = None
            st.switch_page("pages/1_Discover.py")

        av    = profile["name"][:2].upper()
        score = profile["total_score"]
        score_cls = "score-high" if score>=75 else ("score-mid" if score>=50 else "score-low")

        # header
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#E0FBF4,#D0F5EB);
                    border:1px solid #E4E5F0;border-radius:14px;padding:24px 28px;margin-bottom:20px'>
            <div style='display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px'>
                <div style='display:flex;align-items:center;gap:14px'>
                    <div class='avatar' style='width:52px;height:52px;font-size:17px;background:#E0FBF4;color:#00A87D'>{av}</div>
                    <div>
                        <div style='font-size:22px;font-weight:800;color:#0D0E1A'>{profile['name']}</div>
                        <div style='font-size:13px;color:#5A5B72'>{profile['industry']} · {profile['location']}</div>
                    </div>
                </div>
                <span class='score-badge {score_cls}' style='font-size:15px;padding:8px 18px'>{score}% match</span>
            </div>
        </div>""", unsafe_allow_html=True)

        # brand details
        st.markdown("<div class='sec-title'>BRAND DETAILS</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='info-box'><div class='stat-lbl'>INDUSTRY</div><div class='stat-val'>{profile['industry']}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='info-box'><div class='stat-lbl'>CAMPAIGN BUDGET</div><div class='stat-val'>${profile['budget_min']:,}–${profile['budget_max']:,}</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='info-box'><div class='stat-lbl'>COMPANY SIZE</div><div class='stat-val'>{profile['size']}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='info-box'><div class='stat-lbl'>LOCATION</div><div class='stat-val'>{profile['location']}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='info-box'><div class='stat-lbl'>TARGET AUDIENCE</div><div class='stat-val'>{profile['target']}</div></div>", unsafe_allow_html=True)

        # creator niches wanted
        st.markdown("<div class='sec-title'>CREATOR NICHES WANTED</div>", unsafe_allow_html=True)
        chips = "".join(f"<span class='niche-chip'>{p}</span>" for p in profile["preferences"])
        st.markdown(f"<div style='margin-bottom:12px'>{chips}</div>", unsafe_allow_html=True)

        # fit score
        st.markdown("<div class='sec-title'>YOUR FIT SCORE FOR THIS BRAND</div>", unsafe_allow_html=True)
        score_bars(profile["niche_score"], profile["audience_score"],
                   profile["engagement_score"], profile["history_score"])

        # contact info
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='sec-title'>CONTACT INFORMATION</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background:#fff;border:1px solid #E4E5F0;border-radius:10px;padding:4px 18px'>
            <div class='contact-row'><span class='contact-lbl'>EMAIL</span><span class='contact-val'>{profile['email']}</span></div>
            <div class='contact-row'><span class='contact-lbl'>WEBSITE</span><span class='contact-val'>{profile['website']}</span></div>
            <div class='contact-row'><span class='contact-lbl'>INSTAGRAM</span><span class='contact-val'>{profile['instagram']}</span></div>
        </div>""", unsafe_allow_html=True)

        # action buttons
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        already_saved     = selected_id in st.session_state.get("saved", set())
        already_contacted = selected_id in st.session_state.get("contacted", set())

        col1, col2 = st.columns(2)
        with col1:
            label = "★ Saved" if already_saved else "☆ Save brand"
            if st.button(label, use_container_width=True, key="save_brand_btn"):
                st.session_state.saved.add(selected_id)
                st.rerun()
        with col2:
            if already_contacted:
                st.button("✅ Pitch sent", use_container_width=True, disabled=True, key="pitched_btn")
            else:
                if st.button("Send pitch to brand", type="primary", use_container_width=True, key="pitch_btn"):
                    st.session_state.show_collab_modal = True
                    st.session_state.selected_type = "brand"
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# OWN PROFILE
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.session_state.show_collab_modal = False

    if role == "brand":
        brand_list = list(BRANDS)
        own = brand_list[0] if brand_list else {
            "id": 1, "name": "Your Brand", "industry": "General",
            "size": "SMB", "budget_min": 0, "budget_max": 0,
            "target": "", "location": "", "preferences": [],
            "email": "", "website": "", "instagram": "",
            "total_score": 0, "niche_score": 0, "audience_score": 0,
            "engagement_score": 0, "history_score": 0,
        }
        st.markdown("""<div style='font-size:26px;font-weight:800;color:#0D0E1A;margin-bottom:4px'>My profile</div>
        <div style='font-size:14px;color:#9899B0;margin-bottom:24px'>Your brand profile visible to creators on PairUp</div>""",
        unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Creators matched", 8)
        c2.metric("Requests sent", len(st.session_state.get("contacted", set())))
        c3.metric("Saved", len(st.session_state.get("saved", set())))

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='sec-title'>PROFILE DETAILS</div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='form-lbl'>BRAND NAME</div>", unsafe_allow_html=True)
            brand_name = st.text_input("", value=own["name"], label_visibility="collapsed", key="edit_bname")
            st.markdown("<div class='form-lbl'>CAMPAIGN BUDGET</div>", unsafe_allow_html=True)
            budget = st.text_input("", value=f"${own['budget_min']:,}–${own['budget_max']:,}", label_visibility="collapsed", key="edit_budget")
        with col2:
            st.markdown("<div class='form-lbl'>INDUSTRY</div>", unsafe_allow_html=True)
            industry = st.selectbox("", INDUSTRIES, label_visibility="collapsed", key="edit_ind")
            st.markdown("<div class='form-lbl'>LOCATION</div>", unsafe_allow_html=True)
            location = st.text_input("", value=own["location"], label_visibility="collapsed", key="edit_bloc")

        st.markdown("<div class='form-lbl'>TARGET AUDIENCE</div>", unsafe_allow_html=True)
        target = st.text_input("", value=own["target"], label_visibility="collapsed", key="edit_target")

        st.markdown("<div class='sec-title'>CREATOR PREFERENCES</div>", unsafe_allow_html=True)
        prefs = st.multiselect("", ["Fitness","Wellness","Running","Beauty","Tech","Food","Travel","Gaming","Reels","Stories","Long-form","Posts"],
                               default=own["preferences"], label_visibility="collapsed", key="edit_prefs")

        col_edit, col_dl = st.columns(2)
        with col_edit:
            if st.button("Edit profile", type="primary", use_container_width=True):
                try:
                    payload = {
                        "name":                       brand_name,
                        "industry":                   industry,
                        "target_audience_description": target,
                        "budget_range":               budget,
                        "preferred_niche":            prefs[0] if prefs else industry,
                    }
                    update_brand(user_id, payload)
                    st.success("Profile saved successfully!")
                except Exception as e:
                    st.error(f"Failed to save profile: {e}")
        with col_dl:
            st.button("Download media kit", use_container_width=True)

    else:
        inf_list = list(INFLUENCERS)
        own = inf_list[0] if inf_list else {
            "id": 1, "name": "@yourhandle", "niche": "General",
            "followers": 0, "engagement": 0.0, "age": "18–24",
            "gender": "—", "formats": [], "rate": "—",
            "bio": "", "total_score": 0, "niche_score": 0,
            "audience_score": 0, "engagement_score": 0, "history_score": 0,
            "past_collabs": [],
        }
        st.markdown("""<div style='font-size:26px;font-weight:800;color:#0D0E1A;margin-bottom:4px'>My profile</div>
        <div style='font-size:14px;color:#9899B0;margin-bottom:24px'>Your creator profile visible to brands on PairUp</div>""",
        unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Brands matched", 5)
        c2.metric("Requests received", 0)
        c3.metric("Saved by brands", 0)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='sec-title'>PROFILE DETAILS</div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='form-lbl'>HANDLE</div>", unsafe_allow_html=True)
            st.text_input("", value=own["name"], label_visibility="collapsed", key="edit_iname")
            st.markdown("<div class='form-lbl'>FOLLOWERS</div>", unsafe_allow_html=True)
            st.number_input("", value=own["followers"], label_visibility="collapsed", key="edit_ifol")
            st.markdown("<div class='form-lbl'>LOCATION</div>", unsafe_allow_html=True)
            st.text_input("", value=own["location"], label_visibility="collapsed", key="edit_iloc")
        with c2:
            st.markdown("<div class='form-lbl'>NICHE</div>", unsafe_allow_html=True)
            st.selectbox("", NICHES, index=NICHES.index(own["niche"]) if own["niche"] in NICHES else 0,
                        label_visibility="collapsed", key="edit_iniche")
            st.markdown("<div class='form-lbl'>ENGAGEMENT RATE (%)</div>", unsafe_allow_html=True)
            st.number_input("", value=float(own["engagement"]), step=0.1,
                           label_visibility="collapsed", key="edit_ieng")
            st.markdown("<div class='form-lbl'>CONTENT FORMATS</div>", unsafe_allow_html=True)
            st.multiselect("", FORMATS, default=own["formats"],
                          label_visibility="collapsed", key="edit_ifmt")
        st.markdown("<div class='form-lbl'>BIO</div>", unsafe_allow_html=True)
        st.text_area("", value=own["bio"], height=80,
                    label_visibility="collapsed", key="edit_ibio")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # inbound requests
        st.markdown("<div class='sec-title'>INBOUND BRAND REQUESTS</div>", unsafe_allow_html=True)
        # placeholder inbound requests (will come from GET /contact-requests?user_id=&direction=brand_to_influencer)
        inbound = [
            {"brand": "FitFuel Nutrition", "industry": "Fitness / Nutrition", "budget": "$3K–$8K", "score": 92, "campaign": "Protein launch campaign · Reels + Stories", "status": "new"},
            {"brand": "Petal Foods",       "industry": "Food / Organic",       "budget": "$2.5K–$6K","score": 76, "campaign": "Organic meal kit launch · open to long-form", "status": "responded"},
        ]
        for req in inbound:
            score_cls = "score-high" if req["score"]>=75 else "score-mid"
            status_color = "#E0FBF4" if req["status"]=="responded" else "#FFF8EC"
            status_text_color = "#007A5A" if req["status"]=="responded" else "#D48A00"
            st.markdown(f"""
            <div class='creator-card' style='margin-bottom:8px'>
                <div style='display:flex;align-items:flex-start;justify-content:space-between'>
                    <div style='display:flex;align-items:center;gap:12px'>
                        <div class='avatar' style='background:#E0FBF4;color:#00A87D;width:36px;height:36px;font-size:11px'>{req['brand'][:2].upper()}</div>
                        <div>
                            <div style='font-size:14px;font-weight:700;color:#0D0E1A'>{req['brand']}</div>
                            <div style='font-size:12px;color:#9899B0'>{req['industry']} · {req['budget']} · {req['score']}% match</div>
                            <div style='font-size:12px;color:#5A5B72;margin-top:2px'>{req['campaign']}</div>
                        </div>
                    </div>
                    <span style='background:{status_color};color:{status_text_color};font-size:11px;font-weight:700;
                                 padding:3px 10px;border-radius:10px;white-space:nowrap'>{req['status'].capitalize()}</span>
                </div>
            </div>""", unsafe_allow_html=True)

        col_edit, col_dl = st.columns(2)
        with col_edit:
            if st.button("Edit profile", type="primary", use_container_width=True):
                try:
                    payload = {
                        "name":               st.session_state.get("edit_iname", own["name"]),
                        "niche":              st.session_state.get("edit_iniche", own["niche"]),
                        "follower_count":     int(st.session_state.get("edit_ifol", own["followers"]) or 0),
                        "engagement_rate":    float(st.session_state.get("edit_ieng", own["engagement"]) or 0.0),
                        "location":           st.session_state.get("edit_iloc", own["location"]),
                        "content_format_tags": st.session_state.get("edit_ifmt", own["formats"]),
                        "bio":                st.session_state.get("edit_ibio", own["bio"]),
                    }
                    update_influencer(user_id, payload)
                    st.success("Profile saved successfully!")
                except Exception as e:
                    st.error(f"Failed to save profile: {e}")
        with col_dl:
            st.button("Download media kit", use_container_width=True)