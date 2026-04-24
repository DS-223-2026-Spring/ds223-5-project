from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class InfluencerBase(BaseModel):
    handle: str
    full_name: str
    niche: str
    location: str
    follower_count: int
    engagement_rate: float
    audience_age_group: str
    audience_gender: str
    content_formats: str
    rate_min: int
    rate_max: int
    bio: Optional[str] = None
    email: str
    is_synthetic: bool = False


class InfluencerCreate(InfluencerBase):
    pass


class InfluencerUpdate(BaseModel):
    handle: Optional[str] = None
    full_name: Optional[str] = None
    niche: Optional[str] = None
    location: Optional[str] = None
    follower_count: Optional[int] = None
    engagement_rate: Optional[float] = None
    audience_age_group: Optional[str] = None
    audience_gender: Optional[str] = None
    content_formats: Optional[str] = None
    rate_min: Optional[int] = None
    rate_max: Optional[int] = None
    bio: Optional[str] = None
    email: Optional[str] = None
    is_synthetic: Optional[bool] = None


class Influencer(InfluencerBase):
    influencer_id: int
    created_at: datetime
