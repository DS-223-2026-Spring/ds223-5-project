from pydantic import BaseModel


# POST /matches/generate request — identifies the brand-influencer pair
class MatchGenerateRequest(BaseModel):
    brand_id: int
    influencer_id: int


# POST /matches/generate response — includes weighted sub-scores and total
class MatchResponse(BaseModel):
    brand_id: int
    influencer_id: int
    total_score: int
    niche_score: int
    audience_score: int
    engagement_score: int
    history_score: int
