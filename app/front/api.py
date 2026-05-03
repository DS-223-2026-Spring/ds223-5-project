"""
api.py — Backend API client
============================
Connects Streamlit frontend to the FastAPI backend.
"""

import requests

BASE_URL = "http://back:8000/api/v1"


# Influencer endpoints

def get_influencers(niche=None, location=None, min_engagement=None,
                    max_followers=None, min_match_score=None,
                    format_=None, age_group=None) -> list[dict]:
    """GET /influencers"""
    params = {}
    if niche:           params["niche"] = niche
    if location:        params["location"] = location
    if min_engagement:  params["min_engagement"] = min_engagement
    if max_followers:   params["max_followers"] = max_followers
    if min_match_score: params["min_match_score"] = min_match_score
    if format_:         params["format"] = format_
    if age_group:       params["age_group"] = age_group
    r = requests.get(f"{BASE_URL}/influencers", params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def get_influencer(influencer_id: int) -> dict | None:
    """GET /influencers/{id}"""
    r = requests.get(f"{BASE_URL}/influencers/{influencer_id}", timeout=10)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


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


# Brand endpoints

def get_brands(industry=None, size=None, budget_min=None,
               budget_max=None, min_match_score=None) -> list[dict]:
    """GET /brands"""
    params = {}
    if industry:        params["industry"] = industry
    if size:            params["size"] = size
    if budget_min:      params["budget_min"] = budget_min
    if budget_max:      params["budget_max"] = budget_max
    if min_match_score: params["min_match_score"] = min_match_score
    r = requests.get(f"{BASE_URL}/brands", params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def get_brand(brand_id: int) -> dict | None:
    """GET /brands/{id}"""
    r = requests.get(f"{BASE_URL}/brands/{brand_id}", timeout=10)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


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


# Match endpoints

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
    r = requests.get(
        f"{BASE_URL}/past-collaborations",
        params={"influencer_id": influencer_id},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


# Contact endpoints

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
    r = requests.get(f"{BASE_URL}/contact-requests", params=params, timeout=10)
    r.raise_for_status()
    return r.json()