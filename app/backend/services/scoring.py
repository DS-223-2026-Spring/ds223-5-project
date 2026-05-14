from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Sequence


# Niche adjacency graph for fuzzy niche matching
ADJACENT_NICHES: Dict[str, List[str]] = {
    "Fitness":       ["Wellness", "Running", "Sports", "Sportswear"],
    "Wellness":      ["Fitness", "Beauty", "Yoga", "Health"],
    "Beauty":        ["Fashion", "Wellness", "Skincare"],
    "Fashion":       ["Beauty", "Lifestyle"],
    "Food":          ["Wellness", "Cooking", "Nutrition", "Organic"],
    "Tech":          ["Gaming", "Productivity", "SaaS", "Software"],
    "Gaming":        ["Tech", "Entertainment"],
    "Travel":        ["Lifestyle", "Food", "Adventure"],
    "Lifestyle":     ["Fashion", "Travel", "Beauty"],
    "Running":       ["Fitness", "Sports", "Wellness"],
    "Sports":        ["Fitness", "Running"],
    "Skincare":      ["Beauty", "Wellness"],
    "Nutrition":     ["Food", "Fitness", "Wellness"],
}

# Expected engagement rates by follower tier (nano/micro/mid/macro)
_TIER_BENCHMARKS = [
    (10_000,   5.0),   # nano
    (50_000,   3.0),   # micro
    (200_000,  2.0),   # mid
    (float("inf"), 1.5),  # macro
]


# Tokenize comma/slash-separated string into normalized lowercase terms
def _tokenize(text: str) -> List[str]:
    return [t.strip().lower() for t in re.split(r"[,/·;|]+", text) if t.strip()]


# Niche sub-score (weight: 35%) — exact=100, adjacent=60-80, mismatch=20
def _compute_niche_score(brand: Dict[str, Any], influencer: Dict[str, Any]) -> int:
    brand_niches = _tokenize(brand.get("preferred_niches", ""))
    inf_niche = (influencer.get("niche") or "").strip().lower()

    if not inf_niche or not brand_niches:
        return 30

    # Direct niche match
    if inf_niche in brand_niches:
        return 100

    # Adjacency lookup via niche graph
    adjacent = [a.lower() for a in ADJACENT_NICHES.get(inf_niche.title(), [])]
    overlap = [n for n in brand_niches if n in adjacent]
    if overlap:
        return 60 + min(20, len(overlap) * 10)

    # Reverse adjacency: brand niche has influencer niche as neighbor
    for bn in brand_niches:
        rev_adjacent = [a.lower() for a in ADJACENT_NICHES.get(bn.title(), [])]
        if inf_niche in rev_adjacent:
            return 65

    return 20


# Audience sub-score (weight: 30%) — average of age, gender, and location components
def _compute_audience_score(brand: Dict[str, Any], influencer: Dict[str, Any]) -> int:
    scores: List[int] = []

    # Age overlap: compute intersection of numeric ranges (bucket labels like 18-24)
    inf_age = (influencer.get("audience_age_group") or "").lower()
    tgt_age = (brand.get("target_audience_age_group") or "").lower()
    age_score = 50
    if inf_age and tgt_age:
        inf_nums = [int(x) for x in re.findall(r"\d+", inf_age)]
        tgt_nums = [int(x) for x in re.findall(r"\d+", tgt_age)]
        if inf_nums and tgt_nums:
            inf_range = set(range(inf_nums[0], inf_nums[-1] + 1))
            tgt_range = set(range(tgt_nums[0], tgt_nums[-1] + 1))
            if inf_range & tgt_range:
                overlap_pct = len(inf_range & tgt_range) / max(len(tgt_range), 1)
                age_score = int(50 + 50 * overlap_pct)
            else:
                age_score = 25
    scores.append(age_score)

    # Gender alignment: structured values (parity with influencer audience_gender)
    inf_gender = (influencer.get("audience_gender") or "").strip().lower()
    tgt_gender = (brand.get("target_audience_gender") or "").strip().lower()
    gender_score = 50
    if inf_gender and tgt_gender:
        broad = {"non_binary", "unknown"}
        if inf_gender == tgt_gender:
            gender_score = 90
        elif inf_gender in broad or tgt_gender in broad:
            gender_score = 70
        else:
            gender_score = 35
    scores.append(gender_score)

    # Geographic proximity: exact match, partial (country/city), or none
    inf_loc = (influencer.get("location") or "").lower()
    brand_loc = (brand.get("location") or "").lower()
    loc_score = 50
    if inf_loc and brand_loc:
        if inf_loc == brand_loc:
            loc_score = 100
        elif any(part in brand_loc for part in inf_loc.split(",") if len(part.strip()) > 2):
            loc_score = 75
        elif any(part in inf_loc for part in brand_loc.split(",") if len(part.strip()) > 2):
            loc_score = 75
        else:
            loc_score = 40
    scores.append(loc_score)

    return int(sum(scores) / len(scores)) if scores else 50


# Engagement sub-score (weight: 25%) — rate normalized against follower-tier benchmark
def _compute_engagement_score(influencer: Dict[str, Any]) -> int:
    followers = int(influencer.get("follower_count", 0))
    eng_rate = float(influencer.get("engagement_rate", 0))

    if followers <= 0 or eng_rate <= 0:
        return 30

    benchmark = 3.0
    for max_followers, bench in _TIER_BENCHMARKS:
        if followers <= max_followers:
            benchmark = bench
            break

    ratio = eng_rate / benchmark
    score = int(min(100, ratio * 70))
    return max(0, score)


# History sub-score (weight: 10%) — past collaboration category alignment
def _compute_history_score(
    brand: Dict[str, Any],
    past_collabs: Sequence[Dict[str, Any]],
) -> int:
    if not past_collabs:
        return 60

    brand_niches = _tokenize(brand.get("preferred_niches", ""))
    if not brand_niches:
        return 60

    match_count = 0
    for collab in past_collabs:
        cat = (collab.get("brand_category") or "").strip().lower()
        if cat in brand_niches:
            match_count += 1
        else:
            adjacent = [a.lower() for a in ADJACENT_NICHES.get(cat.title(), [])]
            if any(n in adjacent for n in brand_niches):
                match_count += 0.5

    if match_count >= 1:
        return min(100, 70 + int(match_count * 10))
    return 45


# Compute all sub-scores and return weighted total (clamped 0-100)
def compute_match(
    brand: Dict[str, Any],
    influencer: Dict[str, Any],
    past_collabs: Optional[Sequence[Dict[str, Any]]] = None,
) -> Dict[str, int]:
    collabs = list(past_collabs or [])

    niche = _compute_niche_score(brand, influencer)
    audience = _compute_audience_score(brand, influencer)
    engagement = _compute_engagement_score(influencer)
    history = _compute_history_score(brand, collabs)

    total = round(
        niche * 0.35
        + audience * 0.30
        + engagement * 0.25
        + history * 0.10
    )

    return {
        "total_score": max(0, min(100, total)),
        "niche_score": max(0, min(100, niche)),
        "audience_score": max(0, min(100, audience)),
        "engagement_score": max(0, min(100, engagement)),
        "history_score": max(0, min(100, history)),
    }
