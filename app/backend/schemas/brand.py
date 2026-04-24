from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BrandBase(BaseModel):
    name: str
    industry: str
    location: str
    company_size: str
    budget_min: int
    budget_max: int
    target_audience: str
    preferred_niches: str


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    company_size: Optional[str] = None
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    target_audience: Optional[str] = None
    preferred_niches: Optional[str] = None


class Brand(BrandBase):
    brand_id: int
    created_at: datetime
