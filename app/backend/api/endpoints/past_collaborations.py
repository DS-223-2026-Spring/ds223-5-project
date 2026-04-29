from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from schemas.past_collaboration import PastCollaboration, PastCollaborationCreate, PastCollaborationUpdate
from db.crud import insert_one, select_many, update_many, delete_many

router = APIRouter()


@router.get("/", response_model=List[PastCollaboration])
def get_past_collaborations(
    influencer_id: Optional[int] = Query(None, description="Filter by influencer ID"),
):
    # list past collaborations with optional filter
    where = {}
    if influencer_id is not None:
        where["influencer_id"] = influencer_id

    rows = select_many("past_collaborations", where=where or None, order_by=[("collab_id", "ASC")])
    return [dict(r) for r in rows]


@router.get("/{collab_id}", response_model=PastCollaboration)
def get_past_collaboration(collab_id: int):
    # get single past collaboration by id
    rows = select_many("past_collaborations", where={"collab_id": collab_id})
    if not rows:
        raise HTTPException(status_code=404, detail="Past collaboration not found")
    return dict(rows[0])


@router.post("/", response_model=PastCollaboration, status_code=201)
def create_past_collaboration(collab_in: PastCollaborationCreate):
    # create new past collaboration
    data = collab_in.model_dump()
    result = insert_one("past_collaborations", data, returning=["collab_id"])
    created_id = result["collab_id"]
    rows = select_many("past_collaborations", where={"collab_id": created_id})
    return dict(rows[0])


@router.put("/{collab_id}", response_model=PastCollaboration)
def update_past_collaboration(collab_id: int, collab_in: PastCollaborationUpdate):
    # update existing past collaboration
    rows = select_many("past_collaborations", where={"collab_id": collab_id})
    if not rows:
        raise HTTPException(status_code=404, detail="Past collaboration not found")

    update_data = collab_in.model_dump(exclude_unset=True)
    if not update_data:
        return dict(rows[0])

    update_many("past_collaborations", update_data, where={"collab_id": collab_id})
    rows = select_many("past_collaborations", where={"collab_id": collab_id})
    return dict(rows[0])


@router.delete("/{collab_id}", status_code=204)
def delete_past_collaboration(collab_id: int):
    # delete past collaboration
    deleted = delete_many("past_collaborations", where={"collab_id": collab_id})
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Past collaboration not found")
