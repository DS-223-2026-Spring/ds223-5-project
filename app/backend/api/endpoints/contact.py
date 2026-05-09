from __future__ import annotations

from fastapi import APIRouter, HTTPException

from schemas.contact_request import ContactCreate, ContactResponse
from db.crud import insert_one, select_many
from services.notifications import send_collab_email

router = APIRouter()


# POST /contact — create a new collaboration request between brand and influencer
@router.post("/", response_model=ContactResponse, status_code=201, description="Create a new collaboration pitch or contact request between a brand and an influencer. Dispatches an automated mock email notification to the recipient.")
def send_contact(body: ContactCreate):

    # Verify referenced brand exists
    brand_rows = select_many("brands", where={"brand_id": body.brand_id})
    if not brand_rows:
        raise HTTPException(status_code=404, detail="Brand not found")

    # Verify referenced influencer exists
    influencer_rows = select_many("influencers", where={"influencer_id": body.influencer_id})
    if not influencer_rows:
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

    # Determine recipient and send mock email
    brand = dict(brand_rows[0])
    influencer = dict(influencer_rows[0])
    
    if body.direction == "brand_to_influencer":
        to_email = influencer.get("email")
        subject = f"New Collaboration Request from {brand.get('name')}"
        email_body = f"Message:\n{body.message}\n\nBudget: {body.budget}\nReply to: {body.email}"
    else:
        to_email = brand.get("email")
        subject = f"New Collaboration Pitch from {influencer.get('handle')}"
        email_body = f"Message:\n{body.message}\n\nReply to: {body.email}"
        
    if to_email:
        send_collab_email(to_email, subject, email_body)

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
