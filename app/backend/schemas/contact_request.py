from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# POST /contact request body — initiates a collaboration request
class ContactCreate(BaseModel):
    brand_id: int
    influencer_id: int
    direction: str = Field(
        ...,
        description="'brand_to_influencer' or 'influencer_to_brand'",
    )
    message: str = ""
    budget: str = ""
    email: str = ""


# Shared response for POST /contact and GET /contact-requests
class ContactResponse(BaseModel):
    id: int
    brand_id: int
    influencer_id: int
    direction: str
    message: str
    budget: str = ""
    email: str = ""
    status: str = "pending"
    created_at: datetime
