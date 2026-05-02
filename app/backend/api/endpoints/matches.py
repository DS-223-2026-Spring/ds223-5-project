from __future__ import annotations

from fastapi import APIRouter, HTTPException

from schemas.match import MatchGenerateRequest, MatchResponse
from db.crud import select_many, upsert_one
from services.scoring import compute_match

router = APIRouter()


# POST /matches/generate — compute scores and persist to matches table
@router.post("/generate", response_model=MatchResponse)
def generate_match(body: MatchGenerateRequest):
    # Fetch brand row
    brand_rows = select_many("brands", where={"brand_id": body.brand_id})
    if not brand_rows:
        raise HTTPException(status_code=404, detail="Brand not found")
    brand = dict(brand_rows[0])

    # Fetch influencer row
    inf_rows = select_many("influencers", where={"influencer_id": body.influencer_id})
    if not inf_rows:
        raise HTTPException(status_code=404, detail="Influencer not found")
    influencer = dict(inf_rows[0])

    # Fetch collaboration history for history_score calculation
    collab_rows = select_many(
        "past_collaborations",
        where={"influencer_id": body.influencer_id},
    )
    past_collabs = [dict(r) for r in collab_rows]

    # Compute weighted sub-scores via scoring service
    scores = compute_match(brand, influencer, past_collabs)

    # Upsert into matches table — ON CONFLICT updates existing pair
    match_data = {
        "brand_id": body.brand_id,
        "influencer_id": body.influencer_id,
        "total_score": scores["total_score"],
        "niche_score": scores["niche_score"],
        "audience_score": scores["audience_score"],
        "engagement_score": scores["engagement_score"],
        "history_score": scores["history_score"],
    }
    upsert_one(
        "matches",
        match_data,
        conflict_columns=["brand_id", "influencer_id"],
        update_columns=[
            "total_score", "niche_score", "audience_score",
            "engagement_score", "history_score",
        ],
        returning=["match_id"],
    )

    return {
        "brand_id": body.brand_id,
        "influencer_id": body.influencer_id,
        **scores,
    }
