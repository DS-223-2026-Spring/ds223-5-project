from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from schemas.brand import BrandCreate, BrandResponse, BrandUpdate
from db.crud import execute_raw, insert_one, select_many, update_many

router = APIRouter()


# Transform DB row dict to response schema
def _db_row_to_response(row: dict, scores: dict | None = None) -> dict:
    s = scores or {}
    prefs_str = row.get("preferred_niches") or ""
    preferences = [p.strip() for p in prefs_str.split(",") if p.strip()]
    return {
        "id": row["brand_id"],
        "name": row.get("name", ""),
        "industry": row.get("industry", ""),
        "size": row.get("company_size", ""),
        "budget_min": int(row.get("budget_min", 0)),
        "budget_max": int(row.get("budget_max", 0)),
        "target": row.get("target_audience", ""),
        "location": row.get("location", ""),
        "preferences": preferences,
        "email": row.get("email", ""),
        "website": row.get("website", ""),
        "instagram": row.get("instagram", ""),
        "total_score": s.get("total_score", 0),
        "niche_score": s.get("niche_score", 0),
        "audience_score": s.get("audience_score", 0),
        "engagement_score": s.get("engagement_score", 0),
        "history_score": s.get("history_score", 0),
    }


# Map BrandCreate fields to DB column names for INSERT
def _create_body_to_db(data: BrandCreate) -> dict:
    return {
        "name": data.name,
        "industry": data.industry,
        "company_size": data.size,
        "budget_min": data.budget_min,
        "budget_max": data.budget_max,
        "target_audience": data.target,
        "location": data.location,
        "preferred_niches": ", ".join(data.preferences),
        "email": data.email,
        "website": data.website,
        "instagram": data.instagram,
    }


# Map BrandUpdate fields to DB column names, excluding unset fields
def _update_body_to_db(data: BrandUpdate) -> dict:
    db_data: dict = {}
    raw = data.model_dump(exclude_unset=True)
    field_map = {
        "name": "name",
        "industry": "industry",
        "size": "company_size",
        "budget_min": "budget_min",
        "budget_max": "budget_max",
        "target": "target_audience",
        "location": "location",
        "email": "email",
        "website": "website",
        "instagram": "instagram",
    }
    for api_field, db_col in field_map.items():
        if api_field in raw:
            db_data[db_col] = raw[api_field]
    if "preferences" in raw:
        db_data["preferred_niches"] = ", ".join(raw["preferences"])
    return db_data


# Load cached match scores from the matches table, keyed by brand_id
def _get_scores_map(influencer_id: int | None) -> dict[int, dict]:
    if influencer_id is None:
        return {}
    rows = select_many("matches", where={"influencer_id": influencer_id})
    return {
        int(r["brand_id"]): {
            "total_score": int(r["total_score"]),
            "niche_score": int(r["niche_score"]),
            "audience_score": int(r["audience_score"]),
            "engagement_score": int(r["engagement_score"]),
            "history_score": int(r["history_score"]),
        }
        for r in rows
    }


# GET /brands — filterable list with optional pre-computed scores
@router.get("/", response_model=List[BrandResponse], description="Retrieve a list of brand profiles matching optional filter criteria such as industry, size, and budget range. If `influencer_id` is provided, dynamically calculates and includes match scores.")
def get_brands(
    industry: Optional[str] = Query(None),
    size: Optional[str] = Query(None),
    budget_min: Optional[int] = Query(None),
    budget_max: Optional[int] = Query(None),
    min_match_score: Optional[int] = Query(None),
    influencer_id: Optional[int] = Query(None),
):
    clauses: list[str] = []
    params: dict = {}

    if industry:
        clauses.append('"industry" ILIKE :industry')
        params["industry"] = f"%{industry}%"
    if size:
        clauses.append('"company_size" = :size')
        params["size"] = size
    if budget_min is not None:
        clauses.append('"budget_max" >= :budget_min')
        params["budget_min"] = budget_min
    if budget_max is not None:
        clauses.append('"budget_min" <= :budget_max')
        params["budget_max"] = budget_max

    sql = 'SELECT * FROM "brands"'
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += ' ORDER BY "brand_id" ASC'

    rows = execute_raw(sql, params)
    
    scores_map = {}
    if influencer_id:
        from services.scoring import compute_match
        inf_rows = select_many("influencers", where={"influencer_id": influencer_id})
        if inf_rows:
            influencer = dict(inf_rows[0])
            collab_rows = execute_raw('SELECT * FROM "past_collaborations" WHERE "influencer_id" = :inf_id', {"inf_id": influencer_id})
            past_collabs = [dict(cr) for cr in collab_rows]
            
            for r in rows:
                scores_map[r["brand_id"]] = compute_match(dict(r), influencer, past_collabs)

    results = []
    for r in rows:
        row = dict(r)
        scores = scores_map.get(row["brand_id"], {})
        resp = _db_row_to_response(row, scores)

        if min_match_score is not None and resp["total_score"] < min_match_score:
            continue

        results.append(resp)

    results.sort(key=lambda x: x["total_score"], reverse=True)
    return results


# GET /brands/{id} — single profile lookup
@router.get("/{brand_id}", response_model=BrandResponse, description="Retrieve a specific brand's profile by their ID.")
def get_brand(brand_id: int, influencer_id: Optional[int] = Query(None)):
    rows = select_many("brands", where={"brand_id": brand_id})
    if not rows:
        raise HTTPException(status_code=404, detail="Brand not found")
        
    scores = {}
    if influencer_id:
        inf_rows = select_many("influencers", where={"influencer_id": influencer_id})
        if inf_rows:
            collab_rows = select_many("past_collaborations", where={"influencer_id": influencer_id})
            from services.scoring import compute_match
            scores = compute_match(dict(rows[0]), dict(inf_rows[0]), [dict(r) for r in collab_rows])
            
    return _db_row_to_response(dict(rows[0]), scores)


# POST /brands — register new brand profile
@router.post("/", response_model=BrandResponse, status_code=201, description="Register a new brand profile in the system. Required fields include name, industry, company size, and budget parameters.")
def create_brand(brand_in: BrandCreate):
    db_data = _create_body_to_db(brand_in)
    result = insert_one("brands", db_data, returning=["brand_id"])
    created_id = result["brand_id"]
    rows = select_many("brands", where={"brand_id": created_id})
    return _db_row_to_response(dict(rows[0]))


# PUT /brands/{id} — partial profile update
@router.put("/{brand_id}", response_model=BrandResponse, description="Update an existing brand's profile. Accepts a partial payload, modifying only the provided fields.")
def update_brand(brand_id: int, brand_in: BrandUpdate):
    rows = select_many("brands", where={"brand_id": brand_id})
    if not rows:
        raise HTTPException(status_code=404, detail="Brand not found")

    db_data = _update_body_to_db(brand_in)
    if not db_data:
        return _db_row_to_response(dict(rows[0]))

    update_many("brands", db_data, where={"brand_id": brand_id})
    rows = select_many("brands", where={"brand_id": brand_id})
    return _db_row_to_response(dict(rows[0]))
