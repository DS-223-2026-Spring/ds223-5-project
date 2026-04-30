# Influencer High-Performer Modeling Pipeline (DB-Persisted)

This folder contains a **no-notebook** (Python script only) modeling pipeline that:

1. Loads influencer rows from PostgreSQL (`influencers`)
2. Performs feature engineering
3. Trains a classifier and selects the best-performing model
4. Generates:
   - `predicted_proba` (confidence score)
   - `predicted_label` (0/1)
   - `segment_label` (`low`/`medium`/`high`)
   - `is_recommended` (true if `segment_label == 'high'`)
5. Stores/updates all outputs in PostgreSQL using the existing CRUD helpers

## Target definition

The available dataset does not include richer business outcomes, so the initial classification target is defined as:

`target_high_performer = 1 if engagement_rate >= median(engagement_rate) else 0`

`engagement_rate` is used to compute the target only, and is **excluded** from model features to reduce label leakage.

## Feature engineering

For each influencer, we build the following features:

Numeric:
- `follower_count`
- `tag_count` = number of items in `content_format_tags`
- `bio_length` = length of `bio` (0 if null/empty)
- `has_bio` = 1 if `bio_length > 0` else 0
- Binary tag indicators for the most frequent tags in the training data:
  - `tag__<sanitized_tag>` = 1 if that tag is present in `content_format_tags` else 0

Categorical:
- `niche`
- `location`

Missing values are handled by:
- Median imputation for numeric features
- Most-frequent imputation + one-hot encoding for categorical features

## Model selection

The pipeline trains and compares:
- Logistic Regression
- Random Forest (class-weighted)
- HistGradientBoosting (dense input)

The best model is selected using a holdout evaluation with priority:
1. Highest ROC-AUC
2. If tied/invalid, highest F1
3. If still tied, highest accuracy

## Output tables (persisted in DB)

The DS scripts create/update these tables in PostgreSQL:
- `model_runs`
  - Stores run metadata, metrics, model name, selected tag vocabulary, and the serialized model artifact.
- `influencer_predictions`
  - Stores one row per influencer per `model_run_id` with:
    - `predicted_proba` (confidence score)
    - `segment_label` (`low`/`medium`/`high`, quantile-based with fallback thresholds)
    - `is_recommended`
    - `target_high_performer_true` (computed from engagement_rate median for analysis)

## Rerun behavior (idempotency)

Both training and prediction scripts are designed to be rerunnable:
- `model_runs` uses a stable `run_key` (default: `influencer_high_performer_v1`).
  - If a `model_runs` row already exists for that `run_key`, it is updated in place.
- `influencer_predictions` are deleted and re-inserted for the chosen `model_run_id`.

## How to run

From `app/ds/`:

```bash
python train_and_store_model.py
python predict_and_store_model.py
```

Both scripts use the backend DB connection environment variables (e.g. `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`).

