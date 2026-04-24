from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MatchBase(BaseModel):
    brand_id: int
    influencer_id: int
    total_score: int
    niche_score: int
    audience_score: int
    engagement_score: int
    history_score: int


class MatchCreate(MatchBase):
    pass


class MatchUpdate(BaseModel):
    total_score: Optional[int] = None
    niche_score: Optional[int] = None
    audience_score: Optional[int] = None
    engagement_score: Optional[int] = None
    history_score: Optional[int] = None


class Match(MatchBase):
    match_id: int
    computed_at: datetime
