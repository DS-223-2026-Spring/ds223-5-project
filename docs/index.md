# PairUp

**A data-driven marketplace connecting small businesses with micro-influencers.**

PairUp eliminates the guesswork in influencer marketing. Brands discover creators ranked by a transparent compatibility score. Creators get found by brands that actually fit their audience. Both sides connect and collaborate without any agency in between.

---

## Problem

Small businesses increasingly rely on influencer marketing to reach niche audiences, but finding the right creator is still fragmented and uncertain.

- **44%** of marketers say finding the right influencer is their primary challenge
- **47.4%** of brands spent under $10,000 on influencer marketing in 2024 — leaving no room for bad matches
- **11.9%** of marketers encounter influencer fraud — fake followers and inflated engagement
- **15.5%** cannot accurately measure campaign ROI after the fact

At the same time, micro-influencers with genuine, engaged audiences struggle to get discovered without a big agency or following behind them.

The core problem is not a lack of creators or brands. It is the absence of a transparent, data-driven system that helps both sides make confident decisions before a collaboration starts.

---

## Solution

PairUp is a two-sided web marketplace built on four services working together.

```
React frontend  ──►  FastAPI backend  ──►  PostgreSQL
                                              ▲
                           DS pipeline  ──────┘
```

**Brands** create a profile describing their industry, target audience, and budget. They search and filter creators by niche, location, engagement rate, and audience demographics. Every result is ranked by a pre-computed compatibility score that breaks down into four transparent sub-scores.

**Creators** create a profile showcasing their niche, audience stats, content formats, and past collaborations. They appear in brand search results ranked by how well they match. They can also browse brands actively seeking creators and send a pitch directly.

**The matching score** (computed in `services/scoring.py`) runs on every brand–influencer pair and produces a 0–100 compatibility rating:

| Sub-score | Weight | What it measures |
|---|---|---|
| Niche alignment | 35% | Creator niche vs brand preferred niches, using an adjacency graph for fuzzy matching |
| Audience compatibility | 30% | Age range overlap, gender alignment, geographic proximity |
| Engagement quality | 25% | Engagement rate normalised against the creator's follower tier benchmark |
| Collaboration history | 10% | Past collab categories vs brand niches — no history is neutral, not penalised |

**The DS pipeline** (`app/ds/modeling_pipeline.py`) runs offline as a separate container. It trains a classifier — selecting the best performer from Logistic Regression, Random Forest, and Histogram Gradient Boosting — to predict which influencers are high performers based on their profile attributes. Predictions are stored in PostgreSQL and available for future frontend surfacing.

**Contact** flows directly between brands and creators through the platform. No agency, no intermediary. A brand sends a collab request; a creator sends a pitch. Both land in the other side's matches inbox.

---

## Architecture

| Service | Technology | Port | Role |
|---|---|---|---|
| `front` | React + Vite | 8501 | User interface — all pages and interactions |
| `back` | FastAPI + Python | 8000 | REST API, matching algorithm, business logic |
| `db` | PostgreSQL 17 | 5433 | Persistent storage for all data |
| `ds` | Python scripts | — | Offline ML training and prediction pipeline |

All four services run via `docker compose up` from the `app/` directory.

---

## Pages

| Page | Route | What it does |
|---|---|---|
| Landing | `/` | Welcome screen, role selection (brand or creator) |
| Onboarding | `/onboarding` | Profile creation — brand or creator registration |
| Discover | `/discover` | Marketplace search with live filters and score-ranked results |
| Matches | `/matches` | Saved profiles and sent / received contact requests |
| Profile | `/profile/:type/:id` | Full influencer or brand profile with score breakdown |

---

## Expected outcomes

**For brands**

- Faster discovery — filtered, ranked results instead of manual search
- Transparent decisions — every match score shows its four components so a brand understands exactly why a creator ranked where they did
- Lower wasted spend — bad matches are visible before any money is committed
- Direct contact — send a collaboration request to any creator without leaving the platform

**For creators**

- Genuine discoverability — ranked by compatibility, not follower count or pay-to-play
- Inbound opportunities — brands find creators and pitch directly
- Profile ownership — control over how niche, audience, and past work is presented
- No agency required — direct contact with brands at any budget level

**For the platform**

- A growing two-sided network where every new brand makes the platform more valuable for creators and vice versa
- Pre-computed match scores that return instantly on search — no per-request calculation delay
- A DS layer that continuously produces quality signals (`is_recommended`, `segment_label`) independent of the rule-based matching algorithm, ready to surface when the frontend milestone adds it

---

## Current status

The project is structured across four development branches (`db`, `back`, `front`, `ds`) with all core functionality implemented and integrated.

| Component | Status |
|---|---|
| Database schema + migrations | Complete (5 migrations) |
| FastAPI backend — all endpoints | Complete |
| Matching algorithm | Complete |
| React frontend — all pages | Complete |
| DS training pipeline | Complete |
| DS prediction pipeline | Complete |
| Email notification service | Implemented (mock logger) |
| DS predictions surfaced in UI | Planned |

---

## Navigation

- [Demo](demo.md) — walkthrough and screenshots
- [API](api.md) — all endpoints, request and response shapes
- [DS](etl.md) — data science pipeline, model selection, and outputs
- [App](app.md) — architecture, services, and deployment
