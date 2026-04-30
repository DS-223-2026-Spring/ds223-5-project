# PairUp — Frontend

Streamlit frontend for the PairUp influencer-brand marketplace.

---

## Quick start

```bash
cd app/front
pip install streamlit requests
streamlit run main.py
```

## Docker

```bash
docker build -t front .
docker run -p 8501:8501 front
```

---

## File structure

```
app/front/
├── main.py              Landing page + onboarding wizard
├── ui_core.py           Shared CSS, components, placeholder data
├── Dockerfile
├── pyproject.toml
├── README.md
└── pages/
    ├── 1_Discover.py    Search and filter creators or brands
    ├── 2_My_Matches.py  Saved profiles and sent requests
    └── 3_My_Profile.py  Own profile view and editor
```

---

## Issue #55 — Backend data requirements

The frontend currently runs on hardcoded placeholder data inside `ui_core.py`.
Once the backend is ready, each placeholder gets replaced with a real API call.
Below is every endpoint the frontend will need, with exact field names and formats.

---

### Influencers

#### `GET /influencers`
**Used on:** `1_Discover.py` — brand searches for creators

**Query params:**

```
niche           string    "Fitness"
location        string    "New York"
min_engagement  float     2.5
max_followers   int       100000
min_match_score int       60
format          string    "Reels"
age_group       string    "18–24"
```

**Response** — array of objects:

```json
{
  "id": 1,
  "name": "@sara.fit",
  "niche": "Fitness",
  "location": "New York, US",
  "follower_count": 42400,
  "engagement_rate": 3.8,
  "audience_age_group": "18–34",
  "audience_gender": "72% F",
  "content_formats": ["Reels", "Stories"],
  "rate": "$800–$1,500/post",
  "bio": "Fitness creator based in NYC.",
  "is_synthetic": true,
  "total_score": 93,
  "niche_score": 95,
  "audience_score": 92,
  "engagement_score": 96,
  "history_score": 80
}
```

> All four sub-scores must be included in every list result — the frontend
> uses them to render the score breakdown bar on each card.

---

#### `GET /influencers/{id}`
**Used on:** `3_My_Profile.py` — load own profile
Same object as above, single record.

---

#### `PUT /influencers/{id}`
**Used on:** `3_My_Profile.py` — save profile edits

**Request body:**

```json
{
  "name": "@sara.fit",
  "niche": "Fitness",
  "follower_count": 42400,
  "engagement_rate": 3.8,
  "location": "New York, US",
  "audience_age_group": "18–24",
  "content_formats": ["Reels", "Stories"],
  "bio": "Fitness creator based in NYC."
}
```

---

### Brands

#### `GET /brands`
**Used on:** `1_Discover.py` — creator searches for brands

**Query params:**

```
industry        string    "Fitness"
size            string    "SMB"
budget_min      int       1000
budget_max      int       10000
min_match_score int       60
```

**Response** — array of objects:

```json
{
  "id": 1,
  "name": "FitFuel Nutrition",
  "industry": "Fitness",
  "company_size": "SMB",
  "budget_min": 3000,
  "budget_max": 8000,
  "target_audience": "Active adults 20–35, fitness-focused",
  "location": "Austin, US",
  "preferences": ["Fitness", "Wellness", "Reels"],
  "total_score": 92,
  "niche_score": 95,
  "audience_score": 90,
  "engagement_score": 88,
  "history_score": 80
}
```

#### `GET /brands/{id}`
**Used on:** `3_My_Profile.py` — load own brand profile. Same fields as above.

#### `PUT /brands/{id}`
**Used on:** `3_My_Profile.py` — save brand profile edits. Same fields as body.

---

### Matches

#### `POST /matches/generate`
**Used on:** `1_Discover.py` — triggered when a brand runs a search

**Request body:**

```json
{ "brand_id": 1, "influencer_id": 3 }
```

---

### Past collaborations

#### `GET /past-collaborations?influencer_id={id}`
**Used on:** `3_My_Profile.py` — show past work history

**Response:**

```json
{
  "id": 1,
  "influencer_id": 1,
  "brand_category": "Sportswear",
  "campaign_type": "Sponsored post",
  "estimated_reach": 38000,
  "outcome_tag": "positive"
}
```

---

### Contact requests

#### `POST /contact`
**Used on:** `3_My_Profile.py` — send a collaboration request

**Request body:**

```json
{
  "brand_id": 1,
  "influencer_id": 3,
  "direction": "brand_to_influencer",
  "message": "We'd love to work with you on our protein launch."
}
```

#### `GET /contact-requests?user_id={id}`
**Used on:** `2_My_Matches.py` — load sent and received requests

Optional param: `direction` = `"brand_to_influencer"` or `"influencer_to_brand"`

**Response:**

```json
{
  "id": 1,
  "brand_id": 1,
  "influencer_id": 3,
  "direction": "brand_to_influencer",
  "message": "We'd love to work with you.",
  "status": "pending"
}
```

---

### All endpoints at a glance

```
GET  /influencers                        1_Discover.py    creator search results
GET  /influencers/{id}                   3_My_Profile.py  own creator profile
PUT  /influencers/{id}                   3_My_Profile.py  save creator edits
GET  /brands                             1_Discover.py    brand search results
GET  /brands/{id}                        3_My_Profile.py  own brand profile
PUT  /brands/{id}                        3_My_Profile.py  save brand edits
POST /matches/generate                   1_Discover.py    compute match scores
GET  /past-collaborations?influencer_id  3_My_Profile.py  past collabs list
POST /contact                            3_My_Profile.py  send collab request
GET  /contact-requests?user_id           2_My_Matches.py  sent + received requests
```

---

## Milestone 2 — Issues covered

```
#50  Create frontend service named 'front'         Dockerfile, pyproject.toml   ✅
#51  Translate prototype to Streamlit structure     main.py, all pages           ✅
#52  Build UI skeleton with navigation + layout     main.py, all pages           ✅
#53  Reusable UI components and helper functions    ui_core.py                   ✅
#54  Placeholders for charts, forms, filters        all pages                    ✅
#55  Document backend data requirements             This README                  ✅
#56  Push to front branch and open PR               git push + GitHub PR         ✅
```
