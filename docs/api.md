# API Reference

PairUp exposes a REST API built with FastAPI.  
The backend is responsible for profile management, marketplace discovery, match scoring, collaboration requests, and DS-powered outputs.

Base URL (local development):

```text
http://localhost:8000/api/v1
```

---

# API Architecture

```text
Frontend (React + Vite)
        │
        ▼
 FastAPI Backend
        │
        ├── Match Scoring Service
        ├── Notification Service
        ├── CRUD Layer
        └── PostgreSQL
```

The backend follows a modular structure:

| Layer | Responsibility |
|---|---|
| `api/endpoints/` | Route definitions |
| `schemas/` | Request and response validation |
| `services/` | Matching and notification logic |
| `db/` | Database connection and CRUD helpers |
| `core/` | App configuration |

---

# Health Endpoints

## `GET /`

Basic API welcome route.

### Response

```json
{
  "message": "Welcome to the PairUp API"
}
```

---

## `GET /health`

Checks whether the backend and PostgreSQL connection are working correctly.

### Response

```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

# Influencer Endpoints

## `GET /influencers`

Retrieve influencers with optional filters and dynamic match scoring.

### Query Parameters

| Parameter | Type | Description |
|---|---|---|
| `niche` | string | Filter by creator niche |
| `location` | string | Partial location search |
| `min_engagement` | float | Minimum engagement rate |
| `max_followers` | int | Maximum follower count |
| `format` | string | Filter by content format |
| `age_group` | string | Audience age group |
| `brand_id` | int | Compute live match scores against a brand |
| `min_match_score` | int | Minimum compatibility score |

### Example Request

```http
GET /api/v1/influencers?niche=fitness&brand_id=2
```

### Example Response

```json
[
  {
    "id": 12,
    "name": "FitWithAnna",
    "niche": "fitness",
    "location": "Los Angeles",
    "follower_count": 54000,
    "engagement_rate": 6.8,
    "total_score": 89,
    "niche_score": 35,
    "audience_score": 27,
    "engagement_score": 22,
    "history_score": 5
  }
]
```

---

## `GET /influencers/{id}`

Retrieve a single influencer profile.

### Example

```http
GET /api/v1/influencers/5
```

---

## `POST /influencers`

Create a new influencer profile.

### Request Body

```json
{
  "name": "TravelWithLena",
  "niche": "travel",
  "location": "Paris",
  "follower_count": 85000,
  "engagement_rate": 5.4,
  "audience_age_group": "18-24",
  "audience_gender": "female",
  "content_formats": ["reels", "stories"],
  "rate_min": 200,
  "rate_max": 600,
  "bio": "Travel creator",
  "email": "lena@example.com"
}
```

---

## `PUT /influencers/{id}`

Partially update an influencer profile.

Only submitted fields are modified.

---

# Brand Endpoints

## `GET /brands`

Retrieve brands with optional filtering and dynamic scoring.

### Query Parameters

| Parameter | Type | Description |
|---|---|---|
| `industry` | string | Filter by industry |
| `size` | string | Company size |
| `budget_min` | int | Minimum campaign budget |
| `budget_max` | int | Maximum campaign budget |
| `influencer_id` | int | Compute scores against an influencer |
| `min_match_score` | int | Minimum compatibility score |

---

## `GET /brands/{id}`

Retrieve a single brand profile.

---

## `POST /brands`

Create a new brand profile.

### Request Example

```json
{
  "name": "Glow Cosmetics",
  "industry": "beauty",
  "size": "small",
  "budget_min": 500,
  "budget_max": 3000,
  "target": "Gen Z skincare audience",
  "location": "New York",
  "preferences": ["beauty", "lifestyle"],
  "email": "team@glow.com",
  "website": "https://glow.com",
  "instagram": "@glow"
}
```

---

## `PUT /brands/{id}`

Update an existing brand profile.

---

# Match Scoring Endpoint

## `POST /matches/generate`

Generate and persist a compatibility score between a brand and influencer.

The endpoint computes:

- niche alignment
- audience compatibility
- engagement quality
- collaboration history

### Request Body

```json
{
  "brand_id": 2,
  "influencer_id": 14
}
```

### Response

```json
{
  "brand_id": 2,
  "influencer_id": 14,
  "total_score": 91,
  "niche_score": 35,
  "audience_score": 28,
  "engagement_score": 23,
  "history_score": 5
}
```

---

# Collaboration Endpoints

## `POST /contact`

Create a collaboration request between a brand and creator.

The notification service simulates sending an email event.

### Request Example

```json
{
  "brand_id": 1,
  "influencer_id": 8,
  "direction": "brand_to_influencer",
  "message": "We would love to collaborate on our summer campaign.",
  "budget": 1200,
  "email": "marketing@brand.com"
}
```

---

## `GET /contact-requests`

Retrieve collaboration requests.

Supports inbox-style communication between creators and brands.

---

# Past Collaboration Endpoint

## `GET /past-collaborations`

Retrieve historical collaborations for an influencer.

### Query Parameters

| Parameter | Required |
|---|---|
| `influencer_id` | yes |

### Example

```http
GET /api/v1/past-collaborations?influencer_id=4
```

---

# Match Scoring Logic

The scoring engine combines four weighted components.

| Component | Weight |
|---|---|
| Niche alignment | 35% |
| Audience compatibility | 30% |
| Engagement quality | 25% |
| Collaboration history | 10% |

The backend computes scores dynamically when discovery endpoints are queried with `brand_id` or `influencer_id`.

This allows the frontend to display transparent ranking explanations instead of black-box recommendations.

---

# Running the API

From the `app/` directory:

```bash
docker compose up --build
```

Backend service:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

ReDoc documentation:

```text
http://localhost:8000/redoc
```

---

# Future Improvements

Planned backend improvements include:

- JWT authentication
- saved searches
- recommendation caching
- async email delivery
- DS prediction exposure through endpoints
- analytics endpoints for dashboard visualizations
- campaign performance tracking