# Application Architecture

PairUp is structured as a multi-service application designed around separation of concerns.

The platform combines:

- a React frontend
- a FastAPI backend
- PostgreSQL storage
- a standalone DS pipeline

Each service is isolated through Docker while remaining fully integrated through shared infrastructure.

---

# High-Level Architecture

```text
                ┌─────────────────┐
                │ React Frontend  │
                └────────┬────────┘
                         │ HTTP
                         ▼
                ┌─────────────────┐
                │ FastAPI Backend │
                └────────┬────────┘
                         │ SQL
                         ▼
                ┌─────────────────┐
                │ PostgreSQL DB   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ DS Pipeline     │
                └─────────────────┘
```

---

# Frontend Service

## Technology

- React
- Vite
- JavaScript
- ESLint

## Responsibilities

The frontend handles:

- onboarding flows
- marketplace discovery
- filtering and search
- profile rendering
- score visualization
- collaboration requests

The UI was designed to feel lightweight and marketplace-oriented rather than corporate or overly technical.

---

# Backend Service

## Technology

- FastAPI
- Python
- Pydantic
- SQLAlchemy-style CRUD helpers

## Responsibilities

The backend provides:

- REST endpoints
- profile management
- match score generation
- filtering logic
- database operations
- notification handling

The API is organized into modular endpoint groups:

| Module | Purpose |
|---|---|
| `brands.py` | Brand management |
| `influencers.py` | Creator management |
| `matches.py` | Match score generation |
| `contact.py` | Collaboration requests |
| `past_collaborations.py` | Historical partnerships |

---

# Database Layer

## Technology

- PostgreSQL 17

## Responsibilities

The database stores:

- influencer profiles
- brand profiles
- match scores
- collaboration requests
- DS predictions
- model metadata

The schema was structured to support both transactional operations and analytical outputs.

---

# DS Service

## Technology

- Python
- scikit-learn
- pandas
- matplotlib

## Responsibilities

The DS pipeline handles:

- preprocessing
- feature engineering
- model training
- evaluation
- prediction generation
- analytics exports

Unlike the backend, the DS service runs offline and asynchronously.

This separation keeps the API lightweight while still supporting analytical workflows.

---

# Match Scoring System

One of the most important parts of PairUp is the explainable scoring engine.

The score combines four components:

| Component | Weight |
|---|---|
| Niche alignment | 35% |
| Audience compatibility | 30% |
| Engagement quality | 25% |
| Collaboration history | 10% |

The scoring logic lives inside:

```text
app/backend/services/scoring.py
```

The system was intentionally designed to remain interpretable rather than behaving like a black-box recommendation engine.

---

# Dockerized Deployment

All services are orchestrated with Docker Compose.

## Run Everything

```bash
cd app
docker compose up --build
```

---

# Service Ports

| Service | Port |
|---|---|
| Frontend | 5173 |
| Backend | 8000 |
| PostgreSQL | 5433 |

---

# Repository Structure

```text
ds223-5-project/
├── app/
│   ├── backend/
│   ├── front/
│   ├── db/
│   └── ds/
├── docs/
├── milestone_1/
└── mkdocs.yaml
```

---

# Development Workflow

The project was developed collaboratively across multiple roles:

| Role | Main Contribution |
|---|---|
| Frontend | UI and marketplace experience |
| Backend | API and business logic |
| DS | Modeling and analytics |
| PM | Integration, documentation, coordination |

The architecture intentionally separated responsibilities to reduce merge conflicts and improve maintainability.

---

# Documentation Structure

MkDocs documentation includes:

| Page | Purpose |
|---|---|
| `index.md` | Overview and problem statement |
| `api.md` | Backend endpoint documentation |
| `etl.md` | DS pipeline and analytics |
| `demo.md` | Workflow walkthrough |
| `app.md` | Architecture and deployment |

---

# Deployment Notes

Documentation is deployed through GitHub Pages using MkDocs.

Main commands:

Build locally:

```bash
mkdocs serve
```

Deploy:

```bash
mkdocs gh-deploy
```

---

# Current Integration Status

| Component | Status |
|---|---|
| Frontend ↔ Backend | Integrated |
| Backend ↔ Database | Integrated |
| DS ↔ Database | Integrated |
| Docker orchestration | Complete |
| MkDocs deployment | In progress |

---

# Future Improvements

Planned application improvements:

- authentication and authorization
- cloud deployment
- async processing
- recommendation caching
- analytics dashboards
- campaign management
- creator verification
- fraud detection
- real-time messaging
- ML-powered ranking enhancements

---

# Design Philosophy

PairUp was built around a simple idea:

small businesses should be able to find trustworthy creators without needing agencies, massive budgets, or opaque recommendation systems.

The technical architecture reflects that philosophy by prioritizing:

- transparency
- modularity
- scalability
- explainability
- collaboration between services