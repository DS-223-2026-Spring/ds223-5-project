# PairUp

> A data-driven marketplace connecting small businesses with micro-influencers.

Brands discover creators ranked by a transparent compatibility score. Creators get found by brands that actually fit their audience. Both sides connect and collaborate — no agency, no intermediary.

---

## Links

| Resource | URL |
|---|---|
| Documentation site | https://ds-223-2026-spring.github.io/ds223-5-project/ |
| GitHub repository | https://github.com/DS-223-2026-Spring/ds223-5-project |

---

## Architecture

```
app/
├── front/      React + Vite        port 8501   User interface
├── backend/    FastAPI + Python     port 8000   REST API and matching algorithm
├── db/         PostgreSQL 17        port 5433   Persistent storage
└── ds/         Python scripts       —           ML training and prediction pipeline
```

All four services are orchestrated with Docker Compose from the `app/` directory.

---

## How to run

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Git

### 1. Clone the repository

```bash
git clone https://github.com/DS-223-2026-Spring/ds223-5-project.git
cd ds223-5-project/app
```

### 2. Start all services

```bash
docker compose up --build
```

This starts all four containers. The first run takes a few minutes to build images and initialise the database.


### 3. Stop all services

```bash
docker compose down
```

To also delete the database volume:

```bash
docker compose down -v
```

---

## Run the DS pipeline manually

The DS container runs automatically on `docker compose up`. To run it separately:

```bash
cd app/ds
pip install -r requirements.txt
python train_and_store_model.py
```

To recompute predictions without retraining:

```bash
python predict_and_store_model.py
```

To run the full Milestone 4 workflow in one step:

```bash
python run_milestone4.py
```

Outputs are saved to `app/ds/outputs/` — model artifact, performance summary, prediction CSV, segment charts.

---

## Environment variables

Set automatically by Docker Compose. For local development outside Docker:

```
DB_HOST=localhost
DB_PORT=5433
DB_NAME=imp
DB_USER=imp_user
DB_PASSWORD=imp_password
```

---

## Project structure

```
ds223-5-project/
├── app/
│   ├── docker-compose.yml
│   ├── backend/
│   │   ├── main.py
│   │   ├── api/endpoints/      influencers, brands, matches, contact, past-collaborations
│   │   ├── services/scoring.py matching algorithm
│   │   └── schemas/            Pydantic request and response models
│   ├── db/
│   │   ├── init/               SQL schema applied on first container start
│   │   ├── migrations/         Numbered migration scripts (0001–0005)
│   │   └── tools/              DS metric and dataset publishing scripts
│   ├── ds/
│   │   ├── modeling_pipeline.py     feature engineering, model selection, DB write-back
│   │   ├── train_and_store_model.py entry point for training
│   │   ├── predict_and_store_model.py entry point for inference
│   │   ├── run_milestone4.py        full M4 workflow in one command
│   │   └── outputs/            model.pkl, charts, CSVs
│   └── front/
│       ├── src/
│       │   ├── pages/          LandingPage, OnboardingPage, DiscoverPage, ProfilePage, MatchesPage
│       │   ├── components/     ScoreBars, FilterPanel, ProfileCard, ContactModal
│       │   └── api.js          all HTTP calls to the backend
│       └── Dockerfile
├── docs/                       MkDocs source files
│   ├── index.md
│   ├── api.md
│   ├── app.md
│   ├── demo.md
│   └── etl.md
├── mkdocs.yaml
└── milestone_1/
    ├── Problem Definition.pdf
    └── RoadMap.pdf
```

---

## Matching algorithm

Scores are computed in `app/backend/services/scoring.py` and stored in the `matches` table.

| Sub-score | Weight | What it measures |
|---|---|---|
| Niche alignment | 35% | Creator niche vs brand preferred niches, with adjacency graph for fuzzy matching |
| Audience compatibility | 30% | Age range overlap, gender alignment, geographic proximity |
| Engagement quality | 25% | Engagement rate normalised against the creator's follower tier benchmark |
| Collaboration history | 10% | Past collab categories vs brand niches |

```
total_score = round(niche × 0.35 + audience × 0.30 + engagement × 0.25 + history × 0.10)
```

---

## DS pipeline

The DS service trains a binary classifier to predict which influencers are high performers (engagement rate above median). Three models compete — Logistic Regression, Random Forest, Histogram Gradient Boosting — and the best by ROC-AUC is stored.

Outputs written to PostgreSQL:

- `model_runs` — trained model artifact, metrics, feature schema
- `influencer_predictions` — predicted label, probability, segment (low / medium / high), `is_recommended` flag per influencer

---

## Database

PostgreSQL 17. Schema applied automatically on first `docker compose up`.

Core tables: `brands`, `influencers`, `matches`, `past_collaborations`, `contact_requests`

DS tables: `model_runs`, `influencer_predictions`, `ds_model_metrics`, `ds_modeling_dataset`

Five migrations in `app/db/migrations/` track all schema changes from Milestone 1 through Milestone 4.

---

## Documentation

Built with MkDocs + Material theme.

```bash
pip install mkdocs mkdocs-material mkdocstrings mkdocstrings-python
mkdocs serve        # live preview at http://127.0.0.1:8000
mkdocs gh-deploy    # deploy to GitHub Pages
```

---

## Team

DS-223 · Spring 2026 · DS-223-2026-Spring / ds223-5-project
