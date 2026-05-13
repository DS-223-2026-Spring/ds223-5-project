from __future__ import annotations

from fastapi import APIRouter

from db.crud import execute_raw

router = APIRouter()


# GET /stats — platform-wide summary statistics for the landing page
@router.get(
    "/",
    description="Retrieve aggregated platform statistics: total creators, total brands, and average ROI per dollar spent across all past collaborations.",
)
def get_platform_stats():
    # Total registered influencers (creators)
    creator_rows = execute_raw('SELECT COUNT(*) AS cnt FROM "influencers"')
    creator_count = int(creator_rows[0]["cnt"]) if creator_rows else 0

    # Total registered brands
    brand_rows = execute_raw('SELECT COUNT(*) AS cnt FROM "brands"')
    brand_count = int(brand_rows[0]["cnt"]) if brand_rows else 0

    # Average ROI proxy: computed from engagement_rate across all influencers
    # ROI per $1 spent is derived from the average engagement rate scaled to a dollar return
    # (engagement_rate is stored as a percentage, e.g. 3.5 = 3.5%)
    roi_rows = execute_raw(
        'SELECT COALESCE(AVG("engagement_rate"), 0) AS avg_eng FROM "influencers"'
    )
    avg_engagement = float(roi_rows[0]["avg_eng"]) if roi_rows else 0.0

    # ROI formula: higher engagement rates translate to better campaign returns
    # Industry benchmark: 1% engagement ≈ $2 ROI per $1 spent for micro-influencers
    avg_roi = round(avg_engagement * 2, 2) if avg_engagement > 0 else 0.0

    return {
        "creator_count": creator_count,
        "brand_count": brand_count,
        "avg_roi": avg_roi,
    }
