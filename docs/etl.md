# Data Science and ETL Pipeline

The DS service powers the analytical layer of PairUp.

Its role is not only to train models, but also to transform raw creator data into meaningful recommendation signals that can later be surfaced inside the platform.

---

# Goals of the DS Layer

The pipeline was designed to answer several practical questions:

- Which creators are likely to perform well?
- Which audience characteristics matter most?
- Can we identify high-potential micro-influencers automatically?
- How can recommendations become more data-driven over time?

The DS layer complements the rule-based scoring engine rather than replacing it.

---

# Overall Pipeline

```text
Raw Influencer Data
        │
        ▼
Cleaning and preprocessing
        │
        ▼
Feature engineering
        │
        ▼
Model training
        │
        ▼
Model evaluation
        │
        ▼
Prediction generation
        │
        ▼
Database persistence
```

---

# Dataset Features

The modeling pipeline uses influencer-related attributes such as:

| Feature | Description |
|---|---|
| `follower_count` | Creator audience size |
| `engagement_rate` | Engagement quality |
| `niche` | Creator category |
| `location` | Geographic region |
| `audience_age_group` | Main audience demographic |
| `audience_gender` | Audience distribution |
| `content_formats` | Reels, posts, stories, etc. |
| `past_collaborations` | Historical brand partnerships |

---

# Feature Engineering

The DS workflow converts raw profile data into machine-learning-ready features.

Transformations include:

- categorical encoding
- engagement normalization
- niche representation
- content format expansion
- missing value handling
- segment generation

The preprocessing pipeline ensures all models receive consistent input structure.

---

# Models Evaluated

The project compares multiple baseline approaches.

| Model | Purpose |
|---|---|
| Logistic Regression | Interpretable baseline |
| Random Forest | Nonlinear ensemble model |
| Histogram Gradient Boosting | Performance-oriented boosting model |

The best-performing model is selected automatically during training.

---

# Training Workflow

Training is handled by:

```text
train_and_store_model.py
```

Main responsibilities:

1. load influencer data
2. preprocess features
3. train candidate models
4. evaluate metrics
5. select best model
6. persist predictions and artifacts

---

# Prediction Workflow

Predictions can later be regenerated without retraining through:

```text
predict_and_store_model.py
```

This separation keeps inference lightweight and reproducible.

---

# Model Outputs

The pipeline produces multiple artifacts for analytics and visualization.

| Output | Description |
|---|---|
| `model.pkl` | Serialized trained model |
| `predictions.csv` | Prediction results |
| `segment_summary.csv` | Influencer segmentation |
| `feature_importance.csv` | Important features |
| `baseline_model_comparison.csv` | Model evaluation comparison |
| `run_metadata.json` | Pipeline metadata |
| PNG charts | Visualization outputs |

---

# Generated Visualizations

The DS service automatically generates charts such as:

- engagement rate distributions
- follower count distributions
- segment count plots
- probability distributions
- correlation heatmaps

These outputs were prepared for future frontend analytics integration.

---

# Milestone 4 Unified Script

The project includes a rerunnable milestone workflow:

```bash
python run_milestone4.py
```

This script:

- trains the final model
- saves all outputs
- exports visualizations
- stores predictions
- generates summary tables

Optional arguments:

```bash
python run_milestone4.py --seed 42 --n-samples 250
```

---

# DS and Backend Integration

The DS service communicates with PostgreSQL directly.

Predictions are stored in tables such as:

- `model_runs`
- `influencer_predictions`

This allows future frontend components to surface:

- recommended creators
- confidence scores
- creator segments
- analytics dashboards

---

# Why the DS Layer Matters

The platform already includes a transparent rule-based scoring system.

The DS pipeline adds an additional analytical layer capable of:

- detecting hidden performance patterns
- identifying strong creators early
- improving recommendation quality over time
- supporting future personalization

The long-term vision is a hybrid recommendation system combining explainable matching with learned behavioral insights.

---

# Project Structure

```text
app/ds/
├── eda_modeling.py
├── modeling_pipeline.py
├── train_and_store_model.py
├── predict_and_store_model.py
├── run_milestone4.py
├── modeling_pipeline.md
└── data_understanding_and_modeling.md
```

---

# Running the DS Service

Install dependencies:

```bash
pip install -r requirements.txt
```

Run exploratory modeling:

```bash
python eda_modeling.py
```

Run full training pipeline:

```bash
python train_and_store_model.py
```

Run prediction-only workflow:

```bash
python predict_and_store_model.py
```

---

# Future Improvements

Planned DS improvements include:

- recommendation ranking models
- collaborative filtering
- fraud detection
- creator clustering
- campaign ROI prediction
- time-series engagement tracking
- personalized brand recommendations
- real-time analytics integration