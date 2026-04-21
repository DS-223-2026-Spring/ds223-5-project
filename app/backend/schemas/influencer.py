from pydantic import BaseModel
from typing import List, Optional

class InfluencerBase(BaseModel):
    name: str
    niche: str
    follower_count: int
    engagement_rate: float
    location: str
    content_format_tags: List[str]
    bio: Optional[str] = None

class InfluencerCreate(InfluencerBase):
    pass

class InfluencerUpdate(BaseModel):
    name: Optional[str] = None
    niche: Optional[str] = None
    follower_count: Optional[int] = None
    engagement_rate: Optional[float] = None
    location: Optional[str] = None
    content_format_tags: Optional[List[str]] = None
    bio: Optional[str] = None

class InfluencerInDB(InfluencerBase):
    id: int

class Influencer(InfluencerInDB):
    pass
