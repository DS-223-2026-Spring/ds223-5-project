from fastapi import APIRouter
from app.api.endpoints import influencers

api_router = APIRouter()
api_router.include_router(influencers.router, prefix="/influencers", tags=["influencers"])
