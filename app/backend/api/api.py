from fastapi import APIRouter
from api.endpoints import influencers, brands, matches, contact_requests, past_collaborations

api_router = APIRouter()
api_router.include_router(influencers.router, prefix="/influencers", tags=["influencers"])
api_router.include_router(brands.router, prefix="/brands", tags=["brands"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(contact_requests.router, prefix="/contact-requests", tags=["contact-requests"])
api_router.include_router(past_collaborations.router, prefix="/past-collaborations", tags=["past-collaborations"])
