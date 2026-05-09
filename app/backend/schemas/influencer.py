from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

class AudienceGender(str, Enum):
    FEMALE = "female"
    MALE = "male"
    NON_BINARY = "non_binary"
    UNKNOWN = "unknown"

class AudienceAgeGroup(str, Enum):
    AGE_13_17 = "13-17"
    AGE_18_24 = "18-24"
    AGE_25_34 = "25-34"
    AGE_35_44 = "35-44"
    AGE_45_54 = "45-54"
    AGE_55_PLUS = "55+"

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
    rate_min: int = 0
    rate_max: int = 0
    rate: str = ""
    bio: Optional[str] = None
    email: str
    is_synthetic: bool = False
    total_score: int = 0
    niche_score: int = 0
    audience_score: int = 0
    engagement_score: int = 0
    history_score: int = 0


# POST request body — typed fields, no manual string parsing needed
class InfluencerCreate(BaseModel):
    name: str
    niche: str
    follower_count: int
    engagement_rate: float
    location: str
    audience_age_group: AudienceAgeGroup
    audience_gender: AudienceGender
    content_formats: List[str]
    email: str
    rate_min: int = 0
    rate_max: int = 0
    bio: Optional[str] = None


# PUT request body — partial update, only provided fields are applied
class InfluencerUpdate(BaseModel):
    name: Optional[str] = None
    niche: Optional[str] = None
    follower_count: Optional[int] = None
    engagement_rate: Optional[float] = None
    location: Optional[str] = None
    audience_age_group: Optional[AudienceAgeGroup] = None
    audience_gender: Optional[AudienceGender] = None
    content_formats: Optional[List[str]] = None
    email: Optional[str] = None
    rate_min: Optional[int] = None
    rate_max: Optional[int] = None
    bio: Optional[str] = None
