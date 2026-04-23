# DS Service

This folder contains a standalone data science workflow for EDA and baseline
modeling of influencer performance data.

## Files
- `Dockerfile`: DS service container setup
- `docker-compose.yml`: DS container configuration
- `requirements.txt`: Python dependencies
- `eda_modeling.py`: EDA and baseline model comparison pipeline
- `data_understanding_and_modeling.md`: data assumptions and feature notes

## Run locally
```bash
pip install -r requirements.txt
python eda_modeling.py
```

## Run with Docker
```bash
docker compose up --build
```

## Outputs
Artifacts are generated in `outputs/`:
- `null_counts.csv`
- `correlation_matrix.csv`
- `baseline_model_comparison.csv` (accuracy, F1, RMSE)
- `distribution_follower_count.png`
- `distribution_engagement_rate.png`
- `correlation_heatmap.png`
