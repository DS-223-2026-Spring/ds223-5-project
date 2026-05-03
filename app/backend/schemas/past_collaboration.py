from typing import Optional

from pydantic import BaseModel


# GET /past-collaborations response — maps DB columns to contract fields
class PastCollaborationResponse(BaseModel):
    id: int
    influencer_id: int
    brand: str
    category: str
    year: str
    content_type: str = ""


# Internal creation schema — uses DB column names directly
class PastCollaborationCreate(BaseModel):
    influencer_id: int
    brand_name: str
    brand_category: str
    collab_year: int
    content_type: str


# Internal update schema — partial update, only provided fields are applied
class PastCollaborationUpdate(BaseModel):
    brand_name: Optional[str] = None
    brand_category: Optional[str] = None
    collab_year: Optional[int] = None
    content_type: Optional[str] = None
