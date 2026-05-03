"""
api.py — Backend API client
============================
Connects Streamlit frontend to the FastAPI backend.
All functions return parsed JSON (dict/list) or None on 404.
"""

import requests

BASE_URL = "http://back:8000/api/v1"


# ── Influencer endpoints ─────────────────────────────────────────────────────

def get_influencers(niche=None, location=None, min_engagement=None,
                    max_followers=None, min_match_score=None,
                    format_=None, age_group=None) -> list[dict]:
    """GET /influencers with optional query filters."""
    params = {}
    if niche:           params["niche"] = niche
    if location:        params["location"] = location
    if min_engagement:  params["min_engagement"] = min_engagement
    if max_followers:   params["max_followers"] = max_followers
    if min_match_score: params["min_match_score"] = min_match_score
    if format_:         params["format"] = format_
    if age_group:       params["age_group"] = age_group
    try:
        r = requests.get(f"{BASE_URL}/influencers", params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


def get_influencer(influencer_id: int) -> dict | None:
    """GET /influencers/{id}"""
    try:
        r = requests.get(f"{BASE_URL}/influencers/{influencer_id}", timeout=10)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def create_influencer(payload: dict) -> dict:
    """POST /influencers"""
    r = requests.post(f"{BASE_URL}/influencers", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()


def update_influencer(influencer_id: int, payload: dict) -> dict:
    """PUT /influencers/{id}"""
    r = requests.put(f"{BASE_URL}/influencers/{influencer_id}", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()


# ── Brand endpoints ──────────────────────────────────────────────────────────

def get_brands(industry=None, size=None, budget_min=None,
               budget_max=None, min_match_score=None) -> list[dict]:
    """GET /brands with optional query filters."""
    params = {}
    if industry:        params["industry"] = industry
    if size:            params["size"] = size
    if budget_min:      params["budget_min"] = budget_min
    if budget_max:      params["budget_max"] = budget_max
    if min_match_score: params["min_match_score"] = min_match_score
    try:
        r = requests.get(f"{BASE_URL}/brands", params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


def get_brand(brand_id: int) -> dict | None:
    """GET /brands/{id}"""
    try:
        r = requests.get(f"{BASE_URL}/brands/{brand_id}", timeout=10)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def create_brand(payload: dict) -> dict:
    """POST /brands"""
    r = requests.post(f"{BASE_URL}/brands", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()


def update_brand(brand_id: int, payload: dict) -> dict:
    """PUT /brands/{id}"""
    r = requests.put(f"{BASE_URL}/brands/{brand_id}", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()


# ── Match endpoints ──────────────────────────────────────────────────────────

def generate_match(brand_id: int, influencer_id: int) -> dict:
    """POST /matches/generate"""
    r = requests.post(
        f"{BASE_URL}/matches/generate",
        json={"brand_id": brand_id, "influencer_id": influencer_id},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def get_past_collaborations(influencer_id: int) -> list[dict]:
    """GET /past-collaborations?influencer_id={id}"""
    try:
        r = requests.get(
            f"{BASE_URL}/past-collaborations",
            params={"influencer_id": influencer_id},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


# ── Contact endpoints ────────────────────────────────────────────────────────

def send_contact(brand_id: int, influencer_id: int, direction: str,
                 message: str = "", budget: str = "", email: str = "") -> dict:
    """POST /contact"""
    r = requests.post(
        f"{BASE_URL}/contact",
        json={
            "brand_id": brand_id,
            "influencer_id": influencer_id,
            "direction": direction,
            "message": message,
            "budget": budget,
            "email": email,
        },
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def get_contact_requests(user_id: int, direction: str = None) -> list[dict]:
    """GET /contact-requests?user_id={id}&direction={direction}"""
    params = {"user_id": user_id}
    if direction:
        params["direction"] = direction
    try:
        r = requests.get(f"{BASE_URL}/contact-requests", params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


# ── Lazy-loaded lists for backward compat (used by 2_My_Matches.py) ──────────

class _LazyList(list):
    """List subclass that fetches data from the backend on first access."""
    def __init__(self, fetcher):
        super().__init__()
        self._fetcher = fetcher
        self._loaded = False

    def _ensure_loaded(self):
        if not self._loaded:
            self._loaded = True
            try:
                data = self._fetcher()
                super().extend(data)
            except Exception:
                pass

    def __iter__(self):
        self._ensure_loaded()
        return super().__iter__()

    def __len__(self):
        self._ensure_loaded()
        return super().__len__()

    def __getitem__(self, index):
        self._ensure_loaded()
        return super().__getitem__(index)

    def __bool__(self):
        self._ensure_loaded()
        return super().__bool__()


INFLUENCERS = _LazyList(get_influencers)
BRANDS = _LazyList(get_brands)