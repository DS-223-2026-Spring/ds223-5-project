# PairUp — Backend API Requirements

This document is the contract between the frontend and backend teams.
The frontend is fully built and ready. All functions in `api.js` connect
to the real HTTP endpoints documented below.

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
Search and filter influencers. Called on every filter change in `DiscoverPage.jsx`.

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
Single influencer profile. Called when loading `ProfilePage.jsx`.

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
Update influencer profile. Called when creator clicks "Save Profile" in `ProfilePage.jsx`.

**Request body:** same fields as POST, all optional.

**Response:** updated influencer object.

---

## 2. Brands

### `GET /brands`
Search and filter brands. Called on every filter change in `DiscoverPage.jsx` (creator view).

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
Single brand profile. Called when loading `ProfilePage.jsx`.

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
Update brand profile. Called when brand clicks "Save Profile" in `ProfilePage.jsx`.

**Request body:** same fields as POST, all optional.

**Response:** updated brand object.

---

## 3. Matches

### `POST /matches/generate`
Compute or refresh the match score for a brand–influencer pair.

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
Called when loading a creator's full profile in `ProfilePage.jsx`.

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
Load sent and received requests. Called when loading `MatchesPage.jsx`.

**Query params:**

| Param | Type | Required | Description |
|---|---|---|---|
| `user_id` | int | yes | the logged-in user's ID |
| `direction` | string | no | `"brand_to_influencer"` or `"influencer_to_brand"` to filter |

**Response:** array of contact request objects (same shape as POST response above).
