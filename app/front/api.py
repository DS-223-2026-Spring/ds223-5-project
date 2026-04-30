"""
api.py — Backend API client
============================
All data currently returns placeholder values.
To connect the backend: replace each function body with a real HTTP call.

Example swap:
    # placeholder
    return INFLUENCERS

    # connected
    r = requests.get(f"{BASE_URL}/influencers", params=filters, timeout=5)
    r.raise_for_status()
    return r.json()
"""

import requests

BASE_URL = "http://localhost:8000"   # ← change to backend service URL when ready


# ── placeholder data ───────────────────────────────────────────────────────────

INFLUENCERS = [
    {"id": 1,  "name": "@sara.fit",       "niche": "Fitness",  "location": "New York, US",      "followers": 42400, "engagement": 3.8, "age": "18–34", "gender": "72% F", "formats": ["Reels","Stories"],      "rate": "$800–$1,500/post",   "bio": "Fitness & wellness creator. NYC-based. Brand partner for 3+ years.",         "total_score": 93, "niche_score": 95, "audience_score": 92, "engagement_score": 96, "history_score": 80, "past_collabs": [{"brand": "Nike",    "category": "Sportswear",   "year": "2023"}, {"brand": "Whoop",        "category": "Fitness Tech",  "year": "2024"}]},
    {"id": 2,  "name": "@move.with.mia",  "niche": "Wellness", "location": "Brooklyn, US",      "followers": 27200, "engagement": 4.1, "age": "18–34", "gender": "68% F", "formats": ["Reels","Stories"],      "rate": "$500–$900/post",    "bio": "Mindful movement and wellness. Brooklyn vibes.",                              "total_score": 81, "niche_score": 82, "audience_score": 85, "engagement_score": 88, "history_score": 60, "past_collabs": [{"brand": "Lululemon","category": "Activewear",    "year": "2023"}, {"brand": "Calm",         "category": "Wellness App",  "year": "2024"}]},
    {"id": 3,  "name": "@danielruns",     "niche": "Running",  "location": "Jersey City, US",   "followers": 61000, "engagement": 1.9, "age": "25–34", "gender": "55% M", "formats": ["Posts","Stories"],       "rate": "$1,200–$2,000/post", "bio": "Marathon runner & coach. Jersey City represent.",                             "total_score": 62, "niche_score": 68, "audience_score": 60, "engagement_score": 55, "history_score": 72, "past_collabs": [{"brand": "Brooks",  "category": "Running Gear",  "year": "2022"}, {"brand": "Garmin",       "category": "Fitness Tech",  "year": "2024"}]},
    {"id": 4,  "name": "@nourish.nina",   "niche": "Food",     "location": "Los Angeles, US",   "followers": 38900, "engagement": 3.3, "age": "25–34", "gender": "71% F", "formats": ["Reels","Long-form"],    "rate": "$700–$1,200/post",  "bio": "Clean eating and nutrition recipes. LA food scene.",                          "total_score": 55, "niche_score": 50, "audience_score": 58, "engagement_score": 62, "history_score": 45, "past_collabs": [{"brand": "Thrive",  "category": "Food",          "year": "2023"}, {"brand": "Vitamix",      "category": "Kitchen",       "year": "2024"}]},
    {"id": 5,  "name": "@glowwithgrace",  "niche": "Beauty",   "location": "Chicago, US",       "followers": 54000, "engagement": 2.9, "age": "18–24", "gender": "88% F", "formats": ["Reels","Stories","Long-form"], "rate": "$900–$1,500/post", "bio": "Beauty & skincare tutorials. Chicago-based creator.",                        "total_score": 49, "niche_score": 45, "audience_score": 52, "engagement_score": 50, "history_score": 44, "past_collabs": [{"brand": "Glossier","category": "Beauty",        "year": "2023"}, {"brand": "Tatcha",       "category": "Skincare",      "year": "2024"}]},
    {"id": 6,  "name": "@levelup.leo",    "niche": "Gaming",   "location": "Austin, US",        "followers": 95000, "engagement": 3.5, "age": "13–24", "gender": "71% M", "formats": ["Long-form","Reels"],    "rate": "$2,500–$5,000/post","bio": "Gaming content and esports coverage. Austin, TX.",                            "total_score": 46, "niche_score": 40, "audience_score": 48, "engagement_score": 58, "history_score": 30, "past_collabs": [{"brand": "Razer",   "category": "Gaming",        "year": "2023"}, {"brand": "G Fuel",       "category": "Energy Drinks", "year": "2024"}]},
    {"id": 7,  "name": "@passport.alex",  "niche": "Travel",   "location": "Miami, US",         "followers": 73000, "engagement": 2.2, "age": "25–34", "gender": "Mixed 51%F","formats": ["Reels","Stories"],   "rate": "$1,500–$3,000/post","bio": "Full-time traveler. 60+ countries. Miami home base.",                         "total_score": 44, "niche_score": 42, "audience_score": 46, "engagement_score": 40, "history_score": 50, "past_collabs": [{"brand": "Airbnb",  "category": "Travel",        "year": "2022"}, {"brand": "Away",         "category": "Luggage",       "year": "2023"}, {"brand": "Chase Sapphire","category": "Finance",      "year": "2024"}]},
    {"id": 8,  "name": "@techbytomas",    "niche": "Tech",     "location": "San Francisco, US", "followers": 88000, "engagement": 1.4, "age": "18–34", "gender": "62% M", "formats": ["Long-form","Posts"],    "rate": "$2,000–$4,000/post","bio": "Tech reviews and startup culture. SF-based.",                                 "total_score": 33, "niche_score": 30, "audience_score": 35, "engagement_score": 32, "history_score": 28, "past_collabs": [{"brand": "Notion",  "category": "Productivity",  "year": "2023"}, {"brand": "Linear",       "category": "Software",      "year": "2024"}]},
]

BRANDS = [
    {"id": 1, "name": "FitFuel Nutrition","industry": "Fitness / Nutrition","size": "Startup",  "budget_min": 3000,  "budget_max": 8000,  "target": "Active adults 20–35, fitness-focused",  "location": "Austin, US",       "preferences": ["Fitness","Wellness","Running","Reels","Stories"],       "email": "collab@fitfuelnutrition.com",  "website": "fitfuelnutrition.com",  "instagram": "@fitfuelnutrition",  "total_score": 92, "niche_score": 95, "audience_score": 90, "engagement_score": 88, "history_score": 80},
    {"id": 2, "name": "Bloom Skincare",   "industry": "Beauty / Skincare",  "size": "SMB",      "budget_min": 2000,  "budget_max": 5000,  "target": "Women 18–28, skincare & clean beauty",  "location": "New York, US",     "preferences": ["Beauty","Wellness","Fashion","Reels"],                  "email": "hello@bloomskincare.com",      "website": "bloomskincare.com",     "instagram": "@bloom.skincare",    "total_score": 87, "niche_score": 90, "audience_score": 85, "engagement_score": 82, "history_score": 78},
    {"id": 3, "name": "Petal Foods",      "industry": "Food / Organic",     "size": "SMB",      "budget_min": 2500,  "budget_max": 6000,  "target": "Health-conscious adults 25–40",         "location": "Portland, US",     "preferences": ["Food","Wellness","Fitness"],                            "email": "partners@petalfoods.com",      "website": "petalfoods.com",        "instagram": "@petal.foods",       "total_score": 79, "niche_score": 75, "audience_score": 82, "engagement_score": 78, "history_score": 70},
    {"id": 4, "name": "Wanderly Travel",  "industry": "Travel / Lifestyle", "size": "SMB",      "budget_min": 4000,  "budget_max": 10000, "target": "Adults 25–40, frequent travelers",      "location": "San Francisco, US","preferences": ["Travel","Food","Lifestyle","Reels","Stories"],          "email": "creators@wanderly.com",        "website": "wanderly.com",          "instagram": "@wanderly.travel",   "total_score": 78, "niche_score": 78, "audience_score": 82, "engagement_score": 79, "history_score": 72},
    {"id": 5, "name": "ByteDesk",         "industry": "Productivity / SaaS","size": "Startup",  "budget_min": 1500,  "budget_max": 4000,  "target": "Developers and tech professionals 22–40","location": "Remote",           "preferences": ["Tech","Gaming","Productivity","Long-form"],             "email": "growth@bytedesk.io",          "website": "bytedesk.io",           "instagram": "@bytedesk",          "total_score": 74, "niche_score": 72, "audience_score": 70, "engagement_score": 78, "history_score": 65},
]


# ── influencer functions ───────────────────────────────────────────────────────

def get_influencers(niche=None, location=None, min_engagement=None,
                    max_followers=None, min_match_score=None,
                    format_=None, age_group=None) -> list[dict]:
    """
    GET /influencers
    Returns list of influencers sorted by total_score descending.
    """
    # TODO: replace with → requests.get(f"{BASE_URL}/influencers", params={...}).json()
    results = list(INFLUENCERS)
    if niche:           results = [r for r in results if r["niche"] == niche]
    if location:        results = [r for r in results if location.lower() in r["location"].lower()]
    if min_engagement:  results = [r for r in results if r["engagement"] >= min_engagement]
    if max_followers:   results = [r for r in results if r["followers"] <= max_followers]
    if min_match_score: results = [r for r in results if r["total_score"] >= min_match_score]
    if format_:         results = [r for r in results if format_ in r["formats"]]
    if age_group:       results = [r for r in results if r["age"] == age_group]
    return sorted(results, key=lambda x: x["total_score"], reverse=True)


def get_influencer(influencer_id: int) -> dict | None:
    """GET /influencers/{id}"""
    # TODO: replace with → requests.get(f"{BASE_URL}/influencers/{influencer_id}").json()
    return next((i for i in INFLUENCERS if i["id"] == influencer_id), None)


def create_influencer(payload: dict) -> dict:
    """POST /influencers — called from onboarding step 2 (creator)"""
    # TODO: replace with → requests.post(f"{BASE_URL}/influencers", json=payload).json()
    return {"id": 99, **payload}


def update_influencer(influencer_id: int, payload: dict) -> dict:
    """PUT /influencers/{id} — called from My Profile save"""
    # TODO: replace with → requests.put(f"{BASE_URL}/influencers/{influencer_id}", json=payload).json()
    return {"id": influencer_id, **payload}


# ── brand functions ────────────────────────────────────────────────────────────

def get_brands(industry=None, size=None, budget_min=None,
               budget_max=None, min_match_score=None) -> list[dict]:
    """GET /brands — Returns list sorted by total_score descending."""
    # TODO: replace with → requests.get(f"{BASE_URL}/brands", params={...}).json()
    results = list(BRANDS)
    if industry:        results = [r for r in results if industry.lower() in r["industry"].lower()]
    if size:            results = [r for r in results if r["size"] == size]
    if min_match_score: results = [r for r in results if r["total_score"] >= min_match_score]
    return sorted(results, key=lambda x: x["total_score"], reverse=True)


def get_brand(brand_id: int) -> dict | None:
    """GET /brands/{id}"""
    # TODO: replace with → requests.get(f"{BASE_URL}/brands/{brand_id}").json()
    return next((b for b in BRANDS if b["id"] == brand_id), None)


def create_brand(payload: dict) -> dict:
    """POST /brands — called from onboarding step 2 (brand)"""
    # TODO: replace with → requests.post(f"{BASE_URL}/brands", json=payload).json()
    return {"id": 99, **payload}


def update_brand(brand_id: int, payload: dict) -> dict:
    """PUT /brands/{id} — called from My Profile save"""
    # TODO: replace with → requests.put(f"{BASE_URL}/brands/{brand_id}", json=payload).json()
    return {"id": brand_id, **payload}


# ── match functions ────────────────────────────────────────────────────────────

def generate_match(brand_id: int, influencer_id: int) -> dict:
    """POST /matches/generate — compute or refresh match score for a pair"""
    # TODO: replace with → requests.post(f"{BASE_URL}/matches/generate", json={...}).json()
    return {"brand_id": brand_id, "influencer_id": influencer_id, "total_score": 0}


def get_past_collaborations(influencer_id: int) -> list[dict]:
    """GET /past-collaborations?influencer_id={id}"""
    # TODO: replace with → requests.get(f"{BASE_URL}/past-collaborations", params={"influencer_id": influencer_id}).json()
    inf = get_influencer(influencer_id)
    return inf.get("past_collabs", []) if inf else []


# ── contact / requests ─────────────────────────────────────────────────────────

def send_contact(brand_id: int, influencer_id: int, direction: str,
                 message: str = "", budget: str = "", email: str = "") -> dict:
    """POST /contact — send a collaboration request"""
    # TODO: replace with → requests.post(f"{BASE_URL}/contact", json={...}).json()
    return {
        "id": 1,
        "brand_id": brand_id,
        "influencer_id": influencer_id,
        "direction": direction,
        "message": message,
        "budget": budget,
        "email": email,
        "status": "pending",
    }


def get_contact_requests(user_id: int, direction: str = None) -> list[dict]:
    """GET /contact-requests?user_id={id}&direction={direction}"""
    # TODO: replace with → requests.get(f"{BASE_URL}/contact-requests", params={...}).json()
    return []