from __future__ import annotations

import re
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from schemas.influencer import InfluencerCreate, InfluencerResponse, InfluencerUpdate
from db.crud import execute_raw, insert_one, select_many, update_many

router = APIRouter()


# Extract numeric rate range from display string (e.g. "$800–$1,500/post" -> (800, 1500))
def _parse_rate(rate_str: str) -> tuple[int, int]:
    nums = re.findall(r"[\d,]+", rate_str.replace(",", ""))
    if len(nums) >= 2:
        return int(nums[0]), int(nums[1])
    if len(nums) == 1:
        return int(nums[0]), int(nums[0])
    return 0, 0


# Format rate range as display string with en-dash separator
def _format_rate(rate_min: int, rate_max: int) -> str:
    return f"${rate_min:,}\u2013${rate_max:,}/post"


# Normalize free-text gender input to ref_audience_gender FK value
def _normalize_gender(raw: str) -> str:
    low = raw.strip().lower().replace("%", "")
    if "f" in low and "m" not in low:
        return "female"
    if "m" in low and "f" not in low:
        return "male"
    if "non" in low or "nb" in low:
        return "non_binary"
    return "unknown"


# Normalize age group to ref_audience_age_group FK value (en-dash -> hyphen)
def _normalize_age_group(raw: str) -> str:
    normalized = raw.strip().replace("\u2013", "-").replace("\u2014", "-")
    valid = {"13-17", "18-24", "25-34", "35-44", "45-54", "55+"}
    if normalized in valid:
        return normalized
    # Handle "35+" style
    if "+" in normalized:
        return normalized
    return normalized


# Transform DB row dict to response schema
def _db_row_to_response(row: dict, scores: dict | None = None) -> dict:
    s = scores or {}
    formats_str = row.get("content_formats") or ""
    formats = [f.strip() for f in formats_str.split(",") if f.strip()]
    return {
        "id": row["influencer_id"],
        "name": row["handle"],
        "niche": row.get("niche", ""),
        "location": row.get("location", ""),
        "followers": int(row.get("follower_count", 0)),
        "engagement": float(row.get("engagement_rate", 0)),
        "age": row.get("audience_age_group", ""),
        "gender": row.get("audience_gender", ""),
        "formats": formats,
        "rate": _format_rate(
            int(row.get("rate_min", 0)),
            int(row.get("rate_max", 0)),
        ),
        "bio": row.get("bio"),
        "is_synthetic": bool(row.get("is_synthetic", False)),
        "total_score": s.get("total_score", 0),
        "niche_score": s.get("niche_score", 0),
        "audience_score": s.get("audience_score", 0),
        "engagement_score": s.get("engagement_score", 0),
        "history_score": s.get("history_score", 0),
    }


# Map InfluencerCreate fields to DB column names for INSERT
def _create_body_to_db(data: InfluencerCreate) -> dict:
    rate_min, rate_max = _parse_rate(data.rate)
    handle = data.name
    # DB requires email; derive from handle since contract doesn't include it
    email = handle.lstrip("@") + "@pairup.placeholder"
    return {
        "handle": handle,
        "full_name": handle,
        "niche": data.niche,
        "location": data.location,
        "follower_count": data.follower_count,
        "engagement_rate": data.engagement_rate,
        "audience_age_group": _normalize_age_group(data.audience_age_group),
        "audience_gender": _normalize_gender(data.gender_split),
        "content_formats": ", ".join(data.content_formats),
        "rate_min": rate_min,
        "rate_max": rate_max,
        "bio": data.bio or "",
        "email": email,
        "is_synthetic": False,
    }


# Map InfluencerUpdate fields to DB column names, excluding unset fields
def _update_body_to_db(data: InfluencerUpdate) -> dict:
    db_data: dict = {}
    raw = data.model_dump(exclude_unset=True)
    if "name" in raw:
        db_data["handle"] = raw["name"]
        db_data["full_name"] = raw["name"]
    if "niche" in raw:
        db_data["niche"] = raw["niche"]
    if "location" in raw:
        db_data["location"] = raw["location"]
    if "follower_count" in raw:
        db_data["follower_count"] = raw["follower_count"]
    if "engagement_rate" in raw:
        db_data["engagement_rate"] = raw["engagement_rate"]
    if "audience_age_group" in raw:
        db_data["audience_age_group"] = _normalize_age_group(raw["audience_age_group"])
    if "gender_split" in raw:
        db_data["audience_gender"] = _normalize_gender(raw["gender_split"])
    if "content_formats" in raw:
        db_data["content_formats"] = ", ".join(raw["content_formats"])
    if "rate" in raw:
        rate_min, rate_max = _parse_rate(raw["rate"])
        db_data["rate_min"] = rate_min
        db_data["rate_max"] = rate_max
    if "bio" in raw:
        db_data["bio"] = raw["bio"]
    return db_data


# Load cached match scores from the matches table, keyed by influencer_id
def _get_scores_map(brand_id: int | None) -> dict[int, dict]:
    if brand_id is None:
        return {}
    rows = select_many("matches", where={"brand_id": brand_id})
    return {
        int(r["influencer_id"]): {
            "total_score": int(r["total_score"]),
            "niche_score": int(r["niche_score"]),
            "audience_score": int(r["audience_score"]),
            "engagement_score": int(r["engagement_score"]),
            "history_score": int(r["history_score"]),
        }
        for r in rows
    }


# GET /influencers — filterable list with optional pre-computed scores
@router.get("/", response_model=List[InfluencerResponse])
def get_influencers(
    niche: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    min_engagement: Optional[float] = Query(None),
    max_followers: Optional[int] = Query(None),
    min_match_score: Optional[int] = Query(None),
    format: Optional[str] = Query(None),
    age_group: Optional[str] = Query(None),
    brand_id: Optional[int] = Query(None),
):
    # Construct dynamic WHERE clause from query params
    clauses: list[str] = []
    params: dict = {}

    if niche:
        clauses.append('"niche" = :niche')
        params["niche"] = niche
    if location:
        clauses.append('"location" ILIKE :location')
        params["location"] = f"%{location}%"
    if min_engagement is not None:
        clauses.append('"engagement_rate" >= :min_eng')
        params["min_eng"] = min_engagement
    if max_followers is not None:
        clauses.append('"follower_count" <= :max_fol')
        params["max_fol"] = max_followers
    if age_group:
        clauses.append('"audience_age_group" = :age_group')
        params["age_group"] = age_group

    sql = 'SELECT * FROM "influencers"'
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += ' ORDER BY "influencer_id" ASC'

    rows = execute_raw(sql, params)
    scores_map = _get_scores_map(brand_id)

    results = []
    for r in rows:
        row = dict(r)
        scores = scores_map.get(row["influencer_id"], {})
        resp = _db_row_to_response(row, scores)

        # Post-query filter: format requires in-memory check against parsed list
        if format and format not in resp["formats"]:
            continue
        # Post-query filter: score threshold applied after DB fetch
        if min_match_score is not None and resp["total_score"] < min_match_score:
            continue

        results.append(resp)

    # Primary sort by match relevance
    results.sort(key=lambda x: x["total_score"], reverse=True)
    return results


# GET /influencers/{id} — single profile lookup
@router.get("/{influencer_id}", response_model=InfluencerResponse)
def get_influencer(influencer_id: int):
    rows = select_many("influencers", where={"influencer_id": influencer_id})
    if not rows:
        raise HTTPException(status_code=404, detail="Influencer not found")
    return _db_row_to_response(dict(rows[0]))


# POST /influencers — register new influencer profile
@router.post("/", response_model=InfluencerResponse, status_code=201)
def create_influencer(influencer_in: InfluencerCreate):
    db_data = _create_body_to_db(influencer_in)
    result = insert_one("influencers", db_data, returning=["influencer_id"])
    created_id = result["influencer_id"]
    rows = select_many("influencers", where={"influencer_id": created_id})
    return _db_row_to_response(dict(rows[0]))


# PUT /influencers/{id} — partial profile update
@router.put("/{influencer_id}", response_model=InfluencerResponse)
def update_influencer(influencer_id: int, influencer_in: InfluencerUpdate):
    rows = select_many("influencers", where={"influencer_id": influencer_id})
    if not rows:
        raise HTTPException(status_code=404, detail="Influencer not found")

    db_data = _update_body_to_db(influencer_in)
    if not db_data:
        return _db_row_to_response(dict(rows[0]))

    update_many("influencers", db_data, where={"influencer_id": influencer_id})
    rows = select_many("influencers", where={"influencer_id": influencer_id})
    return _db_row_to_response(dict(rows[0]))
