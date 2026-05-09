from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

class ContactDirection(str, Enum):
    BRAND_TO_INFLUENCER = "brand_to_influencer"
    INFLUENCER_TO_BRAND = "influencer_to_brand"



# POST /contact request body — initiates a collaboration request
class ContactCreate(BaseModel):
    brand_id: int
    influencer_id: int
    direction: ContactDirection = Field(
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
    direction: ContactDirection
    message: str
    budget: str = ""
    email: str = ""
    status: str = "pending"
    created_at: datetime
