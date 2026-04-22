# DS Service

This service runs exploratory analysis and baseline modeling for influencer data.

## Run with Docker Compose
From `app/backend`:

```bash
docker compose up --build ds
```

Outputs are written to:
- `app/ds/outputs/`
- `app/ds/docs/synthetic_data_manifest.json`

## What the pipeline does
1. Pulls influencer data via backend CRUD API.
2. Generates and inserts synthetic records if data is too small for training.
3. Runs EDA (null counts, distributions, correlations, visualizations).
4. Trains and compares baseline models (logistic regression, random forest).
