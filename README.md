# PairUp — Influencer & Brand Matching Platform

## Overview

PairUp is a full-stack platform designed to simplify collaborations between brands and influencers.

The platform helps businesses discover compatible creators using transparent matching logic based on:

* niche alignment
* audience compatibility
* engagement quality
* collaboration history

Unlike traditional influencer marketplaces that prioritize follower count alone, PairUp focuses on explainable and compatibility-driven recommendations.

---

# Project Goals

The main goals of the project were:

* create a complete multi-service application
* integrate frontend, backend, database, and DS workflows
* build transparent creator-brand recommendation logic
* support scalable analytics and future ML integration
* provide fully documented architecture and deployment

---

# System Architecture

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
Data Science Pipeline
```

---

# Main Features

## Frontend

* Creator and brand onboarding
* Marketplace discovery
* Filtering and search
* Match score visualization
* Collaboration request flows
* Responsive React interface

## Backend

* REST API with FastAPI
* Match scoring engine
* CRUD operations
* PostgreSQL integration
* Contact request system
* Dynamic filtering endpoints

## Data Science

* Feature engineering pipeline
* Baseline model comparison
* Prediction generation
* Influencer segmentation
* Analytics exports
* Visualization generation

---

# Match Scoring Logic

The recommendation engine combines multiple weighted components:

| Component              | Weight |
| ---------------------- | ------ |
| Niche Alignment        | 35%    |
| Audience Compatibility | 30%    |
| Engagement Quality     | 25%    |
| Collaboration History  | 10%    |

This allows recommendations to remain explainable instead of functioning as a black-box system.

---

# Tech Stack

| Layer         | Technology                       |
| ------------- | -------------------------------- |
| Frontend      | React, Vite                      |
| Backend       | FastAPI, Python                  |
| Database      | PostgreSQL                       |
| Data Science  | scikit-learn, pandas, matplotlib |
| Deployment    | Docker, Docker Compose           |
| Documentation | MkDocs Material                  |

---

# Repository Structure

```text
app/
├── backend/
├── front/
├── db/
└── ds/

docs/
├── index.md
├── api.md
├── demo.md
├── etl.md
└── app.md
```

---

# Documentation

## MkDocs Pages

| Page       | Description                            |
| ---------- | -------------------------------------- |
| `index.md` | Project overview and problem statement |
| `api.md`   | Backend API documentation              |
| `etl.md`   | DS and ETL workflow                    |
| `demo.md`  | User workflow demonstration            |
| `app.md`   | Application architecture               |

---

# Running the Project

## Clone Repository

```bash
git clone https://github.com/DS-223-2026-Spring/ds223-5-project.git
```

```bash
cd ds223-5-project
```

---

# Docker Setup

Navigate to the app directory:

```bash
cd app
```

Run all services:

```bash
docker compose up --build
```

---

# Service URLs

| Service      | URL                                                        |
| ------------ | ---------------------------------------------------------- |
| Frontend     | [http://localhost:5173](http://localhost:5173)             |
| Backend      | [http://localhost:8000](http://localhost:8000)             |
| Swagger Docs | [http://localhost:8000/docs](http://localhost:8000/docs)   |
| ReDoc        | [http://localhost:8000/redoc](http://localhost:8000/redoc) |

---

# Running MkDocs Locally

Install dependencies:

```bash
pip install mkdocs mkdocs-material mkdocstrings mkdocstrings-python
```

Run documentation locally:

```bash
mkdocs serve
```

Open:

```text
http://127.0.0.1:8000
```

Deploy GitHub Pages:

```bash
mkdocs gh-deploy --force
```

---

# Data Science Pipeline

The DS pipeline supports:

* preprocessing
* feature engineering
* model training
* evaluation
* prediction generation
* analytics export

Main scripts:

```text
train_and_store_model.py
predict_and_store_model.py
run_milestone4.py
```

Run pipeline:

```bash
python run_milestone4.py
```

---

# Screenshots

## Landing Page

Add screenshot:

```text
README_assets/landing_page.png
```

## Marketplace Discovery

Add screenshot:

```text
README_assets/discovery_page.png
```

## Match Scoring

Add screenshot:

```text
README_assets/match_scores.png
```

## API Documentation

Add screenshot:

```text
README_assets/swagger_docs.png
```

## MkDocs Documentation

Add screenshot:

```text
README_assets/mkdocs_site.png
```

---

# Team Workflow

The project was developed collaboratively across:

* frontend development
* backend engineering
* data science
* project management
* documentation and deployment

The architecture was intentionally modular to simplify integration and maintenance.

---

# Future Improvements

Potential future improvements include:

* authentication system
* real-time messaging
* analytics dashboards
* ML-powered recommendation ranking
* campaign tracking
* creator verification
* recommendation caching


The project combines software engineering, analytics, deployment, and documentation into a fully integrated platform.
