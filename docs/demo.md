# Demo Walkthrough

This page presents the PairUp workflow from onboarding to collaboration discovery.

The platform was designed to feel simple from the user's perspective while running a complete matching and scoring pipeline behind the scenes.

---

# Full User Flow

```text
User enters platform
        │
        ▼
Choose role (Brand / Creator)
        │
        ▼
Complete onboarding profile
        │
        ▼
Marketplace discovery
        │
        ▼
Match scoring and ranking
        │
        ▼
Send collaboration request
```

---

# Landing Page

The landing page introduces the platform and explains the marketplace idea:

- brands discover creators
- creators get discovered by compatible brands
- transparent compatibility scoring
- direct communication without agencies

The entry screen also routes users to onboarding depending on their role.

---

# Creator Onboarding

Creators submit:

- niche
- audience demographics
- follower count
- engagement rate
- preferred content formats
- pricing range
- bio and contact information

This information feeds directly into the matching algorithm and DS pipeline.

The onboarding process was intentionally kept lightweight so creators can join quickly without complex setup.

---

# Brand Onboarding

Brands define:

- industry
- company size
- budget range
- target audience
- preferred creator niches
- contact details

These inputs become the basis for compatibility scoring.

The system prioritizes meaningful matching rather than follower count alone.

---

# Marketplace Discovery

The discovery page is the central experience of PairUp.

Users can filter by:

- niche
- location
- engagement rate
- audience age group
- content format
- follower count
- match score threshold

Results are ranked by compatibility score.

---

# Match Score Breakdown

Every profile contains a transparent score explanation.

Instead of showing only a single number, PairUp exposes:

| Score Type | Purpose |
|---|---|
| Niche score | Category similarity |
| Audience score | Demographic overlap |
| Engagement score | Audience quality |
| History score | Relevant collaborations |

This helps users understand *why* a recommendation appears.

---

# Collaboration Requests

Once a match is found:

- brands can pitch creators
- creators can reach out to brands
- requests are stored in the backend
- notifications are logged through the notification service

The goal is to create direct communication without third-party intermediaries.

---

# Data Science Pipeline Demo

The DS service runs independently from the frontend and backend.

Pipeline workflow:

```text
Influencer Data
      │
      ▼
Feature Engineering
      │
      ▼
Model Training
      │
      ▼
Model Selection
      │
      ▼
Prediction Generation
      │
      ▼
PostgreSQL Storage
```

The pipeline compares multiple models and stores predictions for future recommendation improvements.

Generated outputs include:

- prediction CSVs
- charts
- segment summaries
- feature importance tables
- saved model artifacts

---

# Dockerized Architecture Demo

All services run through Docker Compose.

```text
React Frontend
        │
        ▼
FastAPI Backend
        │
        ▼
PostgreSQL Database
        ▲
        │
DS Pipeline Service
```

This structure made integration significantly easier across frontend, backend, and DS roles.

---

# Example Local Run

From the `app/` directory:

```bash
docker compose up --build
```

Frontend:

```text
http://localhost:5173
```

Backend:

```text
http://localhost:8000
```

API Docs:

```text
http://localhost:8000/docs
```

---

# What Makes PairUp Different

Many influencer platforms rely heavily on popularity metrics.

PairUp instead focuses on:

- compatibility
- audience quality
- explainable recommendations
- accessibility for small businesses
- visibility for micro-influencers

The system was designed around trust and transparency rather than opaque recommendation logic.

---

# Current Milestone Status

| Component | Status |
|---|---|
| Frontend integration | Complete |
| Backend API | Complete |
| Database integration | Complete |
| Match scoring | Complete |
| DS pipeline | Complete |
| Docker deployment | Complete |
| GitHub Pages documentation | In progress |

---

# Future Demonstration Goals

Future versions of the demo may include:

- live analytics dashboards
- campaign tracking
- real-time notifications
- authentication and user accounts
- creator recommendation explanations powered by ML
- performance analytics visualizations