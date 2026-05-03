from __future__ import annotations

from fastapi import APIRouter, HTTPException

from schemas.contact_request import ContactCreate, ContactResponse
from db.crud import insert_one, select_many

router = APIRouter()


# POST /contact — create a new collaboration request between brand and influencer
@router.post("/", response_model=ContactResponse, status_code=201)
def send_contact(body: ContactCreate):
    # Validate direction enum
    valid_directions = {"brand_to_influencer", "influencer_to_brand"}
    if body.direction not in valid_directions:
        raise HTTPException(
            status_code=422,
            detail=f"direction must be one of {valid_directions}",
        )

    # Verify referenced brand exists
    if not select_many("brands", where={"brand_id": body.brand_id}):
        raise HTTPException(status_code=404, detail="Brand not found")

    # Verify referenced influencer exists
    if not select_many("influencers", where={"influencer_id": body.influencer_id}):
        raise HTTPException(status_code=404, detail="Influencer not found")

    # Map contract field names to DB column names (budget -> budget_offer, email -> contact_email)
    db_data = {
        "brand_id": body.brand_id,
        "influencer_id": body.influencer_id,
        "direction": body.direction,
        "message": body.message,
        "budget_offer": body.budget,
        "contact_email": body.email,
        "status": "pending",
    }

    result = insert_one("contact_requests", db_data, returning=["request_id"])
    created_id = result["request_id"]
    rows = select_many("contact_requests", where={"request_id": created_id})
    row = dict(rows[0])

    # Map DB columns back to contract field names for response
    return {
        "id": row["request_id"],
        "brand_id": row["brand_id"],
        "influencer_id": row["influencer_id"],
        "direction": row["direction"],
        "message": row["message"],
        "budget": row.get("budget_offer", ""),
        "email": row.get("contact_email", ""),
        "status": row["status"],
        "created_at": row["sent_at"],
    }
