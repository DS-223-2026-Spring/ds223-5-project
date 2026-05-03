from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# API response schema — maps DB columns to contract field names
class BrandResponse(BaseModel):
    id: int
    name: str
    industry: str
    size: str
    budget_min: int
    budget_max: int
    target: str
    location: str
    preferences: List[str] = Field(default_factory=list)
    email: str = ""
    website: str = ""
    instagram: str = ""
    total_score: int = 0
    niche_score: int = 0
    audience_score: int = 0
    engagement_score: int = 0
    history_score: int = 0


# POST request body
class BrandCreate(BaseModel):
    name: str
    industry: str
    size: str
    budget_min: int
    budget_max: int
    target: str
    location: str
    preferences: List[str]
    email: str = ""
    website: str = ""
    instagram: str = ""


# PUT request body — partial update, only provided fields are applied
class BrandUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    target: Optional[str] = None
    location: Optional[str] = None
    preferences: Optional[List[str]] = None
    email: Optional[str] = None
    website: Optional[str] = None
    instagram: Optional[str] = None
