from pydantic import BaseModel
from typing import Optional

class BrandBase(BaseModel):
    name: str
    industry: str
    target_audience_description: str
    budget_range: str
    preferred_niche: str

class BrandCreate(BrandBase):
    pass

class BrandUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    target_audience_description: Optional[str] = None
    budget_range: Optional[str] = None
    preferred_niche: Optional[str] = None

class BrandInDB(BrandBase):
    id: int

class Brand(BrandInDB):
    pass
