from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# API response schema — maps DB columns to contract field names
class InfluencerResponse(BaseModel):
    id: int
    name: str
    niche: str
    location: str
    followers: int
    engagement: float
    age: str
    gender: str
    formats: List[str] = Field(default_factory=list)
    rate: str
    bio: Optional[str] = None
    is_synthetic: bool = False
    total_score: int = 0
    niche_score: int = 0
    audience_score: int = 0
    engagement_score: int = 0
    history_score: int = 0


# POST request body
class InfluencerCreate(BaseModel):
    name: str
    niche: str
    follower_count: int
    engagement_rate: float
    location: str
    audience_age_group: str
    gender_split: str
    content_formats: List[str]
    rate: str
    bio: Optional[str] = None
    past_collab_categories: Optional[List[str]] = None


# PUT request body — partial update, only provided fields are applied
class InfluencerUpdate(BaseModel):
    name: Optional[str] = None
    niche: Optional[str] = None
    follower_count: Optional[int] = None
    engagement_rate: Optional[float] = None
    location: Optional[str] = None
    audience_age_group: Optional[str] = None
    gender_split: Optional[str] = None
    content_formats: Optional[List[str]] = None
    rate: Optional[str] = None
    bio: Optional[str] = None
    past_collab_categories: Optional[List[str]] = None
