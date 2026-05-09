from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from schemas.contact_request import ContactResponse
from db.crud import execute_raw, update_many, select_many

router = APIRouter()


# Enriched response that includes sender name for display purposes
class EnrichedContactResponse(ContactResponse):
    sender_name: str = ""
    receiver_name: str = ""


# Pydantic model for PATCH body
class ContactStatusUpdate(BaseModel):
    status: str  # "accepted" or "rejected"


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


def _enrich_with_names(resp: dict) -> dict:
    """Add sender_name and receiver_name by looking up brand/influencer tables."""
    brand_rows = select_many("brands", where={"brand_id": resp["brand_id"]}, columns=("name",))
    inf_rows = select_many("influencers", where={"influencer_id": resp["influencer_id"]}, columns=("handle", "full_name"))

    brand_name = dict(brand_rows[0])["name"] if brand_rows else f"Brand #{resp['brand_id']}"
    inf_name = dict(inf_rows[0]).get("full_name") or dict(inf_rows[0]).get("handle", f"Influencer #{resp['influencer_id']}") if inf_rows else f"Influencer #{resp['influencer_id']}"

    if resp["direction"] == "brand_to_influencer":
        resp["sender_name"] = brand_name
        resp["receiver_name"] = inf_name
    else:
        resp["sender_name"] = inf_name
        resp["receiver_name"] = brand_name

    return resp


# GET /contact-requests — returns requests where user is either the brand or influencer
@router.get("/", response_model=List[EnrichedContactResponse], description="Retrieve a list of contact requests and collaboration pitches associated with a specific user (either brand or influencer).")
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
    results = []
    for r in rows:
        resp = _db_row_to_response(dict(r))
        resp = _enrich_with_names(resp)
        results.append(resp)
    return results


# PATCH /contact-requests/{request_id} — accept or reject a request
@router.patch("/{request_id}", response_model=EnrichedContactResponse, description="Update the status of a contact request (accept or reject).")
def update_contact_request(request_id: int, body: ContactStatusUpdate):
    if body.status not in ("accepted", "rejected"):
        raise HTTPException(status_code=400, detail="Status must be 'accepted' or 'rejected'")

    rows = select_many("contact_requests", where={"request_id": request_id})
    if not rows:
        raise HTTPException(status_code=404, detail="Contact request not found")

    row = dict(rows[0])
    if row["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"Request is already {row['status']}")

    update_many("contact_requests", data={"status": body.status}, where={"request_id": request_id})

    updated_rows = select_many("contact_requests", where={"request_id": request_id})
    resp = _db_row_to_response(dict(updated_rows[0]))
    resp = _enrich_with_names(resp)
    return resp
