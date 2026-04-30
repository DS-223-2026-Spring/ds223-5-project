from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from schemas.influencer import Influencer, InfluencerCreate, InfluencerUpdate
from db.crud import insert_one, select_many, update_many, delete_many

router = APIRouter()


@router.get("/", response_model=List[Influencer])
def get_influencers(
    niche: Optional[str] = Query(None, description="Filter by niche"),
    location: Optional[str] = Query(None, description="Filter by location"),
    min_followers: Optional[int] = Query(None, description="Minimum follower count"),
):
    # search & filter influencers
    where = {}
    if niche:
        where["niche"] = niche
    if location:
        where["location"] = location

    rows = select_many("influencers", where=where or None, order_by=[("influencer_id", "ASC")])
    results = [dict(r) for r in rows]

    if min_followers is not None:
        results = [r for r in results if r["follower_count"] >= min_followers]

    return results


@router.get("/{influencer_id}", response_model=Influencer)
def get_influencer(influencer_id: int):
    # get single influencer by id
    rows = select_many("influencers", where={"influencer_id": influencer_id})
    if not rows:
        raise HTTPException(status_code=404, detail="Influencer not found")
    return dict(rows[0])


@router.post("/", response_model=Influencer, status_code=201)
def create_influencer(influencer_in: InfluencerCreate):
    # create new influencer
    data = influencer_in.model_dump()
    result = insert_one("influencers", data, returning=["influencer_id"])
    created_id = result["influencer_id"]
    rows = select_many("influencers", where={"influencer_id": created_id})
    return dict(rows[0])


@router.put("/{influencer_id}", response_model=Influencer)
def update_influencer(influencer_id: int, influencer_in: InfluencerUpdate):
    # update existing influencer
    # Check existence
    rows = select_many("influencers", where={"influencer_id": influencer_id})
    if not rows:
        raise HTTPException(status_code=404, detail="Influencer not found")

    update_data = influencer_in.model_dump(exclude_unset=True)
    if not update_data:
        return dict(rows[0])

    update_many("influencers", update_data, where={"influencer_id": influencer_id})
    rows = select_many("influencers", where={"influencer_id": influencer_id})
    return dict(rows[0])


@router.delete("/{influencer_id}", status_code=204)
def delete_influencer(influencer_id: int):
    # delete influencer
    deleted = delete_many("influencers", where={"influencer_id": influencer_id})
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Influencer not found")
