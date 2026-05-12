"""Idempotent synthetic seed: influencers, brands, and match-score generation via API."""

from __future__ import annotations

import os
import random
import sys
from decimal import Decimal
from pathlib import Path

import numpy as np
import requests
from faker import Faker
from sqlalchemy import text

random.seed(42)
np.random.seed(42)

_APP_ROOT = Path(__file__).resolve().parents[2]
if str(_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_APP_ROOT))

from backend.db.connection import DatabaseConfig, get_engine, wait_for_db  # noqa: E402

fake = Faker()
fake.seed_instance(42)

NICHE_CHOICES = ["Fitness","Wellness","Fashion","Food","Tech","Travel","Beauty","Gaming","Running","Lifestyle"]
INFLUENCER_LOCATIONS = ["New York US","Los Angeles US","Chicago US","Austin US","Miami US","Brooklyn US","San Francisco US","London UK","Toronto CA","Sydney AU"]
AUDIENCE_AGE = ["13-17", "18-24", "25-34", "35-44", "45-54", "55+"]
AUDIENCE_GENDER = ["female", "male", "non_binary", "unknown"]
CONTENT_FORMAT_POOL = ["Reels", "Stories", "Long-form", "Posts", "Live"]
INDUSTRIES = ["Fitness / Nutrition","Beauty / Skincare","Travel / Lifestyle","Productivity / SaaS","Food / Organic","Fashion / Apparel","Gaming / Tech","Wellness / Health"]
BRAND_LOCATIONS = ["Austin US","New York US","San Francisco US","Portland US","Remote","Los Angeles US","Chicago US"]
COMPANY_SIZES = ["Startup", "SMB"]
BUDGET_MIN_CHOICES = [1000, 1500, 2000, 2500, 3000]
BUDGET_MAX_DELTA = [2000, 3000, 4000, 5000, 7000]

INDUSTRY_TO_PREFERRED_NICHES: dict[str, list[str]] = {
    "Fitness / Nutrition": ["Fitness", "Wellness", "Running", "Lifestyle"],
    "Beauty / Skincare": ["Beauty", "Fashion", "Lifestyle", "Wellness"],
    "Travel / Lifestyle": ["Travel", "Lifestyle", "Food", "Fashion"],
    "Productivity / SaaS": ["Tech", "Lifestyle"],
    "Food / Organic": ["Food", "Lifestyle", "Wellness", "Travel"],
    "Fashion / Apparel": ["Fashion", "Beauty", "Lifestyle"],
    "Gaming / Tech": ["Gaming", "Tech", "Lifestyle"],
    "Wellness / Health": ["Wellness", "Fitness", "Lifestyle", "Beauty"],
}

TARGET_AUDIENCE_TEMPLATES = [
    "Primary buyers are {adj1} {noun} enthusiasts aged 18–44 with {adj2} spending habits.",
    "We target {adj1} consumers who value {noun} and shop mostly {channel}.",
    "Ideal customers are busy professionals seeking {adj1} {noun} solutions in {channel}.",
    "The core audience is {adj1} households focused on {noun} and {adj2} quality signals.",
    "We reach {adj1} communities passionate about {noun}, mainly discovering brands via {channel}.",
]




def _lognormal_followers() -> int:
    raw = float(np.random.lognormal(mean=np.log(22000.0), sigma=0.65))
    return int(np.clip(raw, 5000, 100_000))


def _engagement_for_followers(follower_count: int) -> Decimal:
    if follower_count < 20_000:
        base = 4.2
    elif follower_count < 50_000:
        base = 2.9
    else:
        base = 1.7
    val = base + float(np.random.normal(loc=0.0, scale=0.4))
    val = float(np.clip(val, 0.5, 10.0))
    return Decimal(str(round(val, 2)))


def _comma_formats(pool: list[str], lo: int, hi: int) -> str:
    k = int(np.random.randint(lo, hi + 1))
    picks = list(np.random.choice(pool, size=k, replace=False))
    return ",".join(picks)


def _preferred_niches_for_industry(industry: str) -> str:
    pool = INDUSTRY_TO_PREFERRED_NICHES.get(industry, NICHE_CHOICES)
    k = int(np.random.randint(2, 4))
    take = min(k, len(pool))
    picks = list(np.random.choice(pool, size=take, replace=False))
    return ",".join(picks)


def _target_audience_sentence() -> str:
    tpl = str(np.random.choice(TARGET_AUDIENCE_TEMPLATES))
    return tpl.format(
        adj1=fake.word().capitalize(),
        adj2=fake.word().capitalize(),
        noun=fake.word(),
        channel=str(np.random.choice(["online", "in-store", "on social", "via subscriptions"])),
    )


def _unique_company_names(n: int) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for i in range(1, n + 1):
        name = fake.company()
        while name in seen:
            name = f"{fake.company()} {i}"
        seen.add(name)
        out.append(name)
    return out


def main() -> None:
    cfg = DatabaseConfig.from_env()
    engine = get_engine(cfg)
    wait_for_db(engine=engine, timeout_s=120)

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM influencers WHERE is_synthetic = TRUE"))
        conn.execute(text("DELETE FROM brands WHERE email LIKE :pat"), {"pat": "brand_%@pairup.dev"})

    company_names = _unique_company_names(50)

    influencer_ids: list[int] = []
    ins_influencer = text(
        """
        INSERT INTO influencers (
            handle, full_name, niche, location, follower_count, engagement_rate,
            audience_age_group, audience_gender, content_formats,
            rate_min, rate_max, bio, email, is_synthetic
        ) VALUES (
            :handle, :full_name, :niche, :location, :follower_count, :engagement_rate,
            :audience_age_group, :audience_gender, :content_formats,
            :rate_min, :rate_max, :bio, :email, TRUE
        )
        RETURNING influencer_id
        """
    )

    for i in range(1, 51):
        follower_count = _lognormal_followers()
        engagement_rate = _engagement_for_followers(follower_count)
        rate_min = int(np.random.randint(300, 2001))
        rate_max = rate_min + int(np.random.randint(500, 3001))

        row = {
            "handle": f"@creator_{i}",
            "full_name": f"{fake.first_name()} {fake.last_name()}",
            "niche": str(np.random.choice(NICHE_CHOICES)),
            "location": str(np.random.choice(INFLUENCER_LOCATIONS)),
            "follower_count": follower_count,
            "engagement_rate": engagement_rate,
            "audience_age_group": str(np.random.choice(AUDIENCE_AGE)),
            "audience_gender": str(np.random.choice(AUDIENCE_GENDER)),
            "content_formats": _comma_formats(CONTENT_FORMAT_POOL, 1, 3),
            "rate_min": rate_min,
            "rate_max": rate_max,
            "bio": fake.sentence(),
            "email": f"creator_{i}@pairup.dev",
        }

        with engine.begin() as conn:
            rid = conn.execute(ins_influencer, row).scalar_one()
            influencer_ids.append(int(rid))

        print(f"Inserted influencer {i}/50")

    brand_ids: list[int] = []
    ins_brand = text(
        """
        INSERT INTO brands (
            name, industry, location, company_size, budget_min, budget_max,
            target_audience, preferred_niches,
            email, website, instagram
        ) VALUES (
            :name, :industry, :location, :company_size, :budget_min, :budget_max,
            :target_audience, :preferred_niches,
            :email, :website, :instagram
        )
        RETURNING brand_id
        """
    )

    for i in range(1, 51):
        industry = str(np.random.choice(INDUSTRIES))
        bmin = int(np.random.choice(BUDGET_MIN_CHOICES))
        bmax = bmin + int(np.random.choice(BUDGET_MAX_DELTA))

        row = {
            "name": company_names[i - 1],
            "industry": industry,
            "location": str(np.random.choice(BRAND_LOCATIONS)),
            "company_size": str(np.random.choice(COMPANY_SIZES)),
            "budget_min": bmin,
            "budget_max": bmax,
            "target_audience": _target_audience_sentence(),
            "preferred_niches": _preferred_niches_for_industry(industry),
            "email": f"brand_{i}@pairup.dev",
            "website": f"brand{i}.com",
            "instagram": f"@brand_{i}",
        }

        with engine.begin() as conn:
            bid = conn.execute(ins_brand, row).scalar_one()
            brand_ids.append(int(bid))

        print(f"Inserted brand {i}/50")

    base = (os.getenv("MATCH_API_BASE") or "http://back:8000").rstrip("/")
    url = f"{base}/api/v1/matches/generate"
    n_ok = 0
    for b in brand_ids:
        for inf in influencer_ids:
            resp = requests.post(url, json={"brand_id": b, "influencer_id": inf}, timeout=60)
            if resp.ok:
                n_ok += 1

    print(f"Generated {n_ok} match scores")


if __name__ == "__main__":
    main()