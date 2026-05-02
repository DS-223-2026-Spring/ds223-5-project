from __future__ import annotations

from typing import List

from fastapi import APIRouter, Query

from schemas.past_collaboration import PastCollaborationResponse
from db.crud import select_many

router = APIRouter()


# Transform DB row to contract response schema (collab_id -> id, brand_name -> brand)
def _db_row_to_response(row: dict) -> dict:
    return {
        "id": row["collab_id"],
        "influencer_id": row["influencer_id"],
        "brand": row.get("brand_name", ""),
        "category": row.get("brand_category", ""),
        "year": str(row.get("collab_year", "")),
        "campaign_type": row.get("campaign_type", ""),
        "estimated_reach": int(row.get("estimated_reach", 0) or 0),
        "outcome_tag": row.get("outcome_tag", "neutral"),
    }


# GET /past-collaborations — list collaboration history for a given influencer
@router.get("/", response_model=List[PastCollaborationResponse])
def get_past_collaborations(
    influencer_id: int = Query(...),
):
    rows = select_many(
        "past_collaborations",
        where={"influencer_id": influencer_id},
        order_by=[("collab_id", "ASC")],
    )
    return [_db_row_to_response(dict(r)) for r in rows]
