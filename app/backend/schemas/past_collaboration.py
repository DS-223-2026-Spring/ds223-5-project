from typing import Optional

from pydantic import BaseModel


# GET /past-collaborations response — maps DB columns to contract fields
class PastCollaborationResponse(BaseModel):
    id: int
    influencer_id: int
    brand: str
    category: str
    year: str
    campaign_type: str = ""
    estimated_reach: int = 0
    outcome_tag: str = "neutral"


# Internal creation schema — uses DB column names directly
class PastCollaborationCreate(BaseModel):
    influencer_id: int
    brand_name: str
    brand_category: str
    collab_year: int
    content_type: str
    campaign_type: str = ""
    estimated_reach: int = 0
    outcome_tag: str = "neutral"


# Internal update schema — partial update, only provided fields are applied
class PastCollaborationUpdate(BaseModel):
    brand_name: Optional[str] = None
    brand_category: Optional[str] = None
    collab_year: Optional[int] = None
    content_type: Optional[str] = None
    campaign_type: Optional[str] = None
    estimated_reach: Optional[int] = None
    outcome_tag: Optional[str] = None
