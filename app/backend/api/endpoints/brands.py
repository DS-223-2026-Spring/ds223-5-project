from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from schemas.brand import Brand, BrandCreate, BrandUpdate
from db.crud import insert_one, select_many, update_many, delete_many

router = APIRouter()


@router.get("/", response_model=List[Brand])
def get_brands(
    industry: Optional[str] = Query(None, description="Filter by industry"),
    location: Optional[str] = Query(None, description="Filter by location"),
):
    # search & filter brands
    where = {}
    if industry:
        where["industry"] = industry
    if location:
        where["location"] = location

    rows = select_many("brands", where=where or None, order_by=[("brand_id", "ASC")])
    return [dict(r) for r in rows]


@router.get("/{brand_id}", response_model=Brand)
def get_brand(brand_id: int):
    # get single brand by id
    rows = select_many("brands", where={"brand_id": brand_id})
    if not rows:
        raise HTTPException(status_code=404, detail="Brand not found")
    return dict(rows[0])


@router.post("/", response_model=Brand, status_code=201)
def create_brand(brand_in: BrandCreate):
    # create new brand
    data = brand_in.model_dump()
    result = insert_one("brands", data, returning=["brand_id"])
    created_id = result["brand_id"]
    rows = select_many("brands", where={"brand_id": created_id})
    return dict(rows[0])


@router.put("/{brand_id}", response_model=Brand)
def update_brand(brand_id: int, brand_in: BrandUpdate):
    # update existing brand
    rows = select_many("brands", where={"brand_id": brand_id})
    if not rows:
        raise HTTPException(status_code=404, detail="Brand not found")

    update_data = brand_in.model_dump(exclude_unset=True)
    if not update_data:
        return dict(rows[0])

    update_many("brands", update_data, where={"brand_id": brand_id})
    rows = select_many("brands", where={"brand_id": brand_id})
    return dict(rows[0])


@router.delete("/{brand_id}", status_code=204)
def delete_brand(brand_id: int):
    # delete brand
    deleted = delete_many("brands", where={"brand_id": brand_id})
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Brand not found")
