from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Query

from schemas.contact_request import ContactResponse
from db.crud import execute_raw

router = APIRouter()


# Transform DB row to contract response schema (request_id -> id, sent_at -> created_at)
def _db_row_to_response(row: dict) -> dict:
    return {
        "id": row["request_id"],
        "brand_id": row["brand_id"],
        "influencer_id": row["influencer_id"],
        "direction": row["direction"],
        "message": row.get("message", ""),
        "budget": row.get("budget_offer", ""),
        "email": row.get("contact_email", ""),
        "status": row.get("status", "pending"),
        "created_at": row["sent_at"],
    }


# GET /contact-requests — returns requests where user is either the brand or influencer
@router.get("/", response_model=List[ContactResponse])
def get_contact_requests(
    user_id: int = Query(...),
    direction: Optional[str] = Query(None),
):
    # user_id is role-agnostic: match against both FK columns
    clauses = ['("brand_id" = :uid OR "influencer_id" = :uid)']
    params: dict = {"uid": user_id}

    if direction:
        clauses.append('"direction" = :direction')
        params["direction"] = direction

    sql = 'SELECT * FROM "contact_requests"'
    sql += " WHERE " + " AND ".join(clauses)
    sql += ' ORDER BY "sent_at" DESC'

    rows = execute_raw(sql, params)
    return [_db_row_to_response(dict(r)) for r in rows]
