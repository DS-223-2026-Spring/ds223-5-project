from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from schemas.contact_request import ContactRequest, ContactRequestCreate, ContactRequestUpdate
from db.crud import insert_one, select_many, update_many, delete_many

router = APIRouter()


@router.get("/", response_model=List[ContactRequest])
def get_contact_requests(
    brand_id: Optional[int] = Query(None, description="Filter by brand ID"),
    influencer_id: Optional[int] = Query(None, description="Filter by influencer ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
):
    # list contact requests with optional filters
    where = {}
    if brand_id is not None:
        where["brand_id"] = brand_id
    if influencer_id is not None:
        where["influencer_id"] = influencer_id
    if status:
        where["status"] = status

    rows = select_many("contact_requests", where=where or None, order_by=[("sent_at", "DESC")])
    return [dict(r) for r in rows]


@router.get("/{request_id}", response_model=ContactRequest)
def get_contact_request(request_id: int):
    # get single contact request by id
    rows = select_many("contact_requests", where={"request_id": request_id})
    if not rows:
        raise HTTPException(status_code=404, detail="Contact request not found")
    return dict(rows[0])


@router.post("/", response_model=ContactRequest, status_code=201)
def create_contact_request(request_in: ContactRequestCreate):
    # create new contact request
    data = request_in.model_dump()
    result = insert_one("contact_requests", data, returning=["request_id"])
    created_id = result["request_id"]
    rows = select_many("contact_requests", where={"request_id": created_id})
    return dict(rows[0])


@router.put("/{request_id}", response_model=ContactRequest)
def update_contact_request(request_id: int, request_in: ContactRequestUpdate):
    # update existing contact request
    rows = select_many("contact_requests", where={"request_id": request_id})
    if not rows:
        raise HTTPException(status_code=404, detail="Contact request not found")

    update_data = request_in.model_dump(exclude_unset=True)
    if not update_data:
        return dict(rows[0])

    update_many("contact_requests", update_data, where={"request_id": request_id})
    rows = select_many("contact_requests", where={"request_id": request_id})
    return dict(rows[0])


@router.delete("/{request_id}", status_code=204)
def delete_contact_request(request_id: int):
    # delete contact request
    deleted = delete_many("contact_requests", where={"request_id": request_id})
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Contact request not found")
