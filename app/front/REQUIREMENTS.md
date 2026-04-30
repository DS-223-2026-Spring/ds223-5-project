# PairUp — Backend API Requirements

This document is the contract between the frontend and backend teams.
The frontend is fully built and ready. All functions in `api.py` return
placeholder data. To connect the backend, replace each function body
with a real HTTP call to the endpoints documented below.

---

## Base URL

```
http://back:8000          # inside docker-compose
http://localhost:8000     # local development
```

All responses are JSON. All list endpoints return results sorted by
`total_score` descending unless otherwise noted.

---

## 1. Influencers

### `GET /influencers`
Search and filter influencers. Called on every filter change in `1_Discover.py`.

**Query params:**

| Param | Type | Required | Description |
|---|---|---|---|
| `niche` | string | no | e.g. `"Fitness"` |
| `location` | string | no | partial match, e.g. `"New York"` |
| `min_engagement` | float | no | e.g. `2.5` |
| `max_followers` | int | no | e.g. `100000` |
| `min_match_score` | int | no | 0–100 |
| `format` | string | no | `"Reels"` \| `"Stories"` \| `"Long-form"` \| `"Posts"` |
| `age_group` | string | no | `"13–17"` \| `"18–24"` \| `"25–34"` \| `"35+"` |
| `brand_id` | int | no | if provided, include pre-computed match scores for this brand |

**Response — array of influencer objects:**

```json
[
  {
    "id": 1,
    "name": "@sara.fit",
    "niche": "Fitness",
    "location": "New York, US",
    "followers": 42400,
    "engagement": 3.8,
    "age": "18–34",
    "gender": "72% F",
    "formats": ["Reels", "Stories"],
    "rate": "$800–$1,500/post",
    "bio": "Fitness & wellness creator. NYC-based.",
    "is_synthetic": true,
    "total_score": 93,
    "niche_score": 95,
    "audience_score": 92,
    "engagement_score": 96,
    "history_score": 80
  }
]
```

> **Important:** All four sub-scores must be included in every list result.
> The frontend renders the score breakdown bar on every card using these values.

---

### `GET /influencers/{id}`
Single influencer profile. Called when loading `3_My_Profile.py`.

**Response:** same object as above (single item, not array).

---

### `POST /influencers`
Create a new influencer profile. Called at the end of onboarding (creator flow, step 4).

**Request body:**

```json
{
  "name": "@yourhandle",
  "niche": "Fitness",
  "follower_count": 42000,
  "engagement_rate": 3.8,
  "location": "New York, US",
  "audience_age_group": "18–24",
  "gender_split": "65% F",
  "content_formats": ["Reels", "Stories"],
  "rate": "$800–$1,500/post",
  "bio": "Your bio here.",
  "past_collab_categories": ["Sportswear", "Wellness"]
}
```

**Response:** created influencer object with assigned `id`.

---

### `PUT /influencers/{id}`
Update influencer profile. Called when creator clicks "Edit profile" in `3_My_Profile.py`.

**Request body:** same fields as POST, all optional.

**Response:** updated influencer object.

---

## 2. Brands

### `GET /brands`
Search and filter brands. Called on every filter change in `1_Discover.py` (creator view).

**Query params:**

| Param | Type | Required | Description |
|---|---|---|---|
| `industry` | string | no | partial match, e.g. `"Fitness"` |
| `size` | string | no | `"Startup"` \| `"SMB"` \| `"Enterprise"` |
| `budget_min` | int | no | minimum campaign budget |
| `budget_max` | int | no | maximum campaign budget |
| `min_match_score` | int | no | 0–100 |
| `influencer_id` | int | no | if provided, include pre-computed match scores for this influencer |

**Response — array of brand objects:**

```json
[
  {
    "id": 1,
    "name": "FitFuel Nutrition",
    "industry": "Fitness / Nutrition",
    "size": "Startup",
    "budget_min": 3000,
    "budget_max": 8000,
    "target": "Active adults 20–35, fitness-focused",
    "location": "Austin, US",
    "preferences": ["Fitness", "Wellness", "Running", "Reels", "Stories"],
    "email": "collab@fitfuelnutrition.com",
    "website": "fitfuelnutrition.com",
    "instagram": "@fitfuelnutrition",
    "total_score": 92,
    "niche_score": 95,
    "audience_score": 90,
    "engagement_score": 88,
    "history_score": 80
  }
]
```

---

### `GET /brands/{id}`
Single brand profile. Called when loading `3_My_Profile.py`.

**Response:** same object as above (single item).

---

### `POST /brands`
Create a new brand profile. Called at end of onboarding (brand flow, step 4).

**Request body:**

```json
{
  "name": "FitFuel Nutrition",
  "industry": "Fitness / Nutrition",
  "size": "Startup",
  "budget_min": 3000,
  "budget_max": 8000,
  "target": "Active adults 20–35, fitness-focused",
  "location": "Austin, US",
  "preferences": ["Fitness", "Wellness", "Reels"],
  "email": "collab@brand.com",
  "website": "brand.com",
  "instagram": "@brand"
}
```

**Response:** created brand object with assigned `id`.

---

### `PUT /brands/{id}`
Update brand profile. Called when brand clicks "Edit profile" in `3_My_Profile.py`.

**Request body:** same fields as POST, all optional.

**Response:** updated brand object.

---

## 3. Matches

### `POST /matches/generate`
Compute or refresh the match score for a brand–influencer pair.
Called when a brand runs a search or selects an influencer.

**Request body:**

```json
{ "brand_id": 1, "influencer_id": 3 }
```

**Response:**

```json
{
  "brand_id": 1,
  "influencer_id": 3,
  "total_score": 87,
  "niche_score": 90,
  "audience_score": 85,
  "engagement_score": 82,
  "history_score": 78
}
```

---

## 4. Past Collaborations

### `GET /past-collaborations`
Called when loading a creator's full profile in `3_My_Profile.py`.

**Query params:**

| Param | Type | Required |
|---|---|---|
| `influencer_id` | int | yes |

**Response:**

```json
[
  {
    "id": 1,
    "influencer_id": 1,
    "brand": "Nike",
    "category": "Sportswear",
    "year": "2023",
    "campaign_type": "Sponsored post",
    "estimated_reach": 38000,
    "outcome_tag": "positive"
  }
]
```

---

## 5. Contact Requests

### `POST /contact`
Send a collaboration request or creator pitch.
Called when brand clicks "Send collab request" or creator clicks "Send pitch to brand".

**Request body:**

```json
{
  "brand_id": 1,
  "influencer_id": 3,
  "direction": "brand_to_influencer",
  "message": "We'd love to work with you on our protein launch.",
  "budget": "$2,000–$5,000",
  "email": "collab@fitfuel.com"
}
```

`direction` must be `"brand_to_influencer"` or `"influencer_to_brand"`.

**Response:**

```json
{
  "id": 42,
  "brand_id": 1,
  "influencer_id": 3,
  "direction": "brand_to_influencer",
  "message": "We'd love to work with you.",
  "budget": "$2,000–$5,000",
  "email": "collab@fitfuel.com",
  "status": "pending",
  "created_at": "2026-04-29T16:00:00Z"
}
```

---

### `GET /contact-requests`
Load sent and received requests. Called when loading `2_My_Matches.py`.

**Query params:**

| Param | Type | Required | Description |
|---|---|---|---|
| `user_id` | int | yes | the logged-in user's ID |
| `direction` | string | no | `"brand_to_influencer"` or `"influencer_to_brand"` to filter |

**Response:** array of contact request objects (same shape as POST response above).

---

## 6. Scoring algorithm (backend implementation notes)

The matching algorithm is defined in the backend spec. Summary for reference:

| Sub-score | Weight | Logic |
|---|---|---|
| `niche_score` | 35% | Exact match = 100, adjacent = 60–80, mismatch = 0–30 |
| `audience_score` | 30% | Age + gender + location, each scored independently, averaged |
| `engagement_score` | 25% | Normalised against follower tier benchmark |
| `history_score` | 10% | Past collab category match = boost, no history = 60, mismatch = small penalty |

```
total_score = round(
    niche_score * 0.35 +
    audience_score * 0.30 +
    engagement_score * 0.25 +
    history_score * 0.10
)
```

---

## 7. Connecting the backend (step by step)

1. Start the backend service (`app/back/`) and confirm it runs on `http://localhost:8000`
2. Open `api.py` in `app/front/`
3. Set `BASE_URL = "http://back:8000"` (docker) or `"http://localhost:8000"` (local)
4. For each function, replace the placeholder return with the commented HTTP call:

```python
# example — get_influencers()
def get_influencers(...) -> list[dict]:
    # remove: return sorted(list(INFLUENCERS), ...)
    # add:
    params = {k: v for k, v in {...}.items() if v is not None}
    r = requests.get(f"{BASE_URL}/influencers", params=params, timeout=5)
    r.raise_for_status()
    return r.json()
```

5. Test each page and verify data loads correctly
6. Remove `INFLUENCERS` and `BRANDS` placeholder lists from `api.py` once all endpoints are connected

---

## Summary table

| Method | Endpoint | Used in | Purpose |
|---|---|---|---|
| GET | `/influencers` | `1_Discover.py` | Creator search |
| GET | `/influencers/{id}` | `3_My_Profile.py` | Creator detail |
| POST | `/influencers` | `main.py` onboarding | Create creator profile |
| PUT | `/influencers/{id}` | `3_My_Profile.py` | Edit creator profile |
| GET | `/brands` | `1_Discover.py` | Brand search |
| GET | `/brands/{id}` | `3_My_Profile.py` | Brand detail |
| POST | `/brands` | `main.py` onboarding | Create brand profile |
| PUT | `/brands/{id}` | `3_My_Profile.py` | Edit brand profile |
| POST | `/matches/generate` | `1_Discover.py` | Compute match score |
| GET | `/past-collaborations` | `3_My_Profile.py` | Past collab list |
| POST | `/contact` | `3_My_Profile.py` | Send request/pitch |
| GET | `/contact-requests` | `2_My_Matches.py` | Load sent/received requests |
