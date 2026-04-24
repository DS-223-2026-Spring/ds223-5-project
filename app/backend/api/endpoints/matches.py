from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from schemas.match import Match, MatchCreate, MatchUpdate
from db.crud import insert_one, select_many, update_many, delete_many

router = APIRouter()


@router.get("/", response_model=List[Match])
def get_matches(
    brand_id: Optional[int] = Query(None, description="Filter by brand ID"),
    influencer_id: Optional[int] = Query(None, description="Filter by influencer ID"),
):
    # list matches with optional filters
    where = {}
    if brand_id is not None:
        where["brand_id"] = brand_id
    if influencer_id is not None:
        where["influencer_id"] = influencer_id

    rows = select_many("matches", where=where or None, order_by=[("total_score", "DESC")])
    return [dict(r) for r in rows]


@router.get("/{match_id}", response_model=Match)
def get_match(match_id: int):
    # get single match by id
    rows = select_many("matches", where={"match_id": match_id})
    if not rows:
        raise HTTPException(status_code=404, detail="Match not found")
    return dict(rows[0])


@router.post("/", response_model=Match, status_code=201)
def create_match(match_in: MatchCreate):
    # create new match
    data = match_in.model_dump()
    result = insert_one("matches", data, returning=["match_id"])
    created_id = result["match_id"]
    rows = select_many("matches", where={"match_id": created_id})
    return dict(rows[0])


@router.put("/{match_id}", response_model=Match)
def update_match(match_id: int, match_in: MatchUpdate):
    # update existing match
    rows = select_many("matches", where={"match_id": match_id})
    if not rows:
        raise HTTPException(status_code=404, detail="Match not found")

    update_data = match_in.model_dump(exclude_unset=True)
    if not update_data:
        return dict(rows[0])

    update_many("matches", update_data, where={"match_id": match_id})
    rows = select_many("matches", where={"match_id": match_id})
    return dict(rows[0])


@router.delete("/{match_id}", status_code=204)
def delete_match(match_id: int):
    # delete match
    deleted = delete_many("matches", where={"match_id": match_id})
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Match not found")
