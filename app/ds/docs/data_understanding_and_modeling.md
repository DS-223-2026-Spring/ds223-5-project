# Data Understanding and Baseline Modeling Notes

## Data source and access pattern
- Primary source: backend influencer CRUD endpoint (`/api/v1/influencers`).
- DS pipeline access pattern: read and write through API calls (via `TestClient`) rather than flat-file-only workflows.
- Reason: keeps analysis consistent with product data contracts and validates compatibility with backend schemas.

## Observed data quality issues
- Very small initial dataset (2 records) is insufficient for meaningful model training.
- `bio` can be optional, which introduces missing-text behavior.
- Categorical fields (`niche`, `location`) are free text and may drift or fragment in production.
- No explicit target/label field exists for supervised learning.
- No timestamp/history fields (e.g., post frequency, growth trend), limiting temporal analysis.

## Missing fields with high modeling value
- Campaign performance outcomes (conversion rate, clicks, revenue per post).
- Audience quality metrics (demographics, geography mix, fake-follower risk).
- Post cadence and recency features.
- Brand-fit or category affinity scores.
- Longitudinal engagement trend features.

## Synthetic data policy
- Synthetic records are generated only when row count is too low for baseline experiments.
- Synthetic records are inserted through CRUD create operations so the same data contract is exercised.
- All synthetic record IDs are documented in `app/ds/docs/synthetic_data_manifest.json`.
- Synthetic creator names are prefixed with `Synthetic Creator` for clear traceability.

## Feature and target definition
- Engineered features:
  - `tags_count`: number of content formats.
  - `bio_length`: length of bio text.
  - Native fields: `follower_count`, `engagement_rate`, `niche`, `location`.
- Target definition:
  - `target_high_performer = 1` when `engagement_rate >= median(engagement_rate)`, else `0`.
  - This is a proxy label to enable baseline classification until business outcome labels exist.

## Baseline models
- Logistic Regression.
- Random Forest Classifier.
- Comparison metrics are exported to `app/ds/outputs/baseline_model_comparison.csv`:
  - accuracy
  - f1
  - precision
  - recall

## EDA deliverables
- Null counts and descriptive statistics in `app/ds/outputs/eda_summary.json`.
- Correlation matrix saved as `app/ds/outputs/correlation_heatmap.png`.
- Distribution and category-level visuals:
  - `app/ds/outputs/engagement_distribution.png`
  - `app/ds/outputs/engagement_by_niche.png`

## Assumptions
- Engagement rate is a valid early proxy for influencer quality.
- Synthetic data shape approximates plausible ranges but is not production truth.
- Current baseline is intended for workflow validation and signal detection, not production deployment.
