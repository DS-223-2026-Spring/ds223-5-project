from typing import Optional

from pydantic import BaseModel


class PastCollaborationBase(BaseModel):
    influencer_id: int
    brand_name: str
    brand_category: str
    collab_year: int
    content_type: str


class PastCollaborationCreate(PastCollaborationBase):
    pass


class PastCollaborationUpdate(BaseModel):
    brand_name: Optional[str] = None
    brand_category: Optional[str] = None
    collab_year: Optional[int] = None
    content_type: Optional[str] = None


class PastCollaboration(PastCollaborationBase):
    collab_id: int
