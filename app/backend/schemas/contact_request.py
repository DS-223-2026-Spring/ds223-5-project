from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ContactRequestBase(BaseModel):
    brand_id: int
    influencer_id: int
    direction: str
    message: str
    budget_offer: Optional[str] = None
    contact_email: str
    status: str


class ContactRequestCreate(ContactRequestBase):
    pass


class ContactRequestUpdate(BaseModel):
    direction: Optional[str] = None
    message: Optional[str] = None
    budget_offer: Optional[str] = None
    contact_email: Optional[str] = None
    status: Optional[str] = None


class ContactRequest(ContactRequestBase):
    request_id: int
    sent_at: datetime
