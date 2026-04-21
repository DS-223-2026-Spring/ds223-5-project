from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas.influencer import Influencer, InfluencerCreate, InfluencerUpdate

router = APIRouter()

# Dummy in-memory database
influencers_db: List[Influencer] = [
    Influencer(
        id=1,
        name="Alex Doe",
        niche="Tech",
        follower_count=50000,
        engagement_rate=4.5,
        location="New York",
        content_format_tags=["Video", "Blog"],
        bio="Tech enthusiast and reviewer."
    ),
    Influencer(
        id=2,
        name="Jane Smith",
        niche="Fashion",
        follower_count=120000,
        engagement_rate=5.2,
        location="Los Angeles",
        content_format_tags=["Photo", "Reels"],
        bio="Fashion addict and lifestyle creator."
    )
]

# Helper to get the next ID
def get_next_id() -> int:
    if not influencers_db:
        return 1
    return max(inf.id for inf in influencers_db) + 1

@router.get("/", response_model=List[Influencer])
def get_influencers(
    niche: Optional[str] = Query(None, description="Filter by niche"),
    location: Optional[str] = Query(None, description="Filter by location"),
    min_followers: Optional[int] = Query(None, description="Minimum follower count")
):
    """
    Search & Filter endpoint for Influencers.
    """
    results = influencers_db
    if niche:
        results = [inf for inf in results if inf.niche.lower() == niche.lower()]
    if location:
        results = [inf for inf in results if inf.location.lower() == location.lower()]
    if min_followers is not None:
        results = [inf for inf in results if inf.follower_count >= min_followers]
    
    return results

@router.get("/{influencer_id}", response_model=Influencer)
def get_influencer(influencer_id: int):
    """
    Retrieve an influencer by ID.
    """
    for inf in influencers_db:
        if inf.id == influencer_id:
            return inf
    raise HTTPException(status_code=404, detail="Influencer not found")

@router.post("/", response_model=Influencer, status_code=201)
def create_influencer(influencer_in: InfluencerCreate):
    """
    Create a new influencer.
    """
    new_influencer = Influencer(id=get_next_id(), **influencer_in.model_dump())
    influencers_db.append(new_influencer)
    return new_influencer

@router.put("/{influencer_id}", response_model=Influencer)
def update_influencer(influencer_id: int, influencer_in: InfluencerUpdate):
    """
    Update an existing influencer.
    """
    for idx, inf in enumerate(influencers_db):
        if inf.id == influencer_id:
            update_data = influencer_in.model_dump(exclude_unset=True)
            updated_inf = inf.model_copy(update=update_data)
            influencers_db[idx] = updated_inf
            return updated_inf
    raise HTTPException(status_code=404, detail="Influencer not found")

@router.delete("/{influencer_id}", status_code=204)
def delete_influencer(influencer_id: int):
    """
    Delete an influencer.
    """
    for idx, inf in enumerate(influencers_db):
        if inf.id == influencer_id:
            influencers_db.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Influencer not found")
