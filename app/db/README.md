## Database (PostgreSQL) setup

This project uses a PostgreSQL container named `db` (via Docker Compose) and initializes the schema from SQL files in `app/db/init/`.

### What’s included

- **Docker Compose service**: `db` running PostgreSQL with port mapping **5432:5432**
- **Initialization SQL**: `app/db/init/001_create_tables.sql`
- **Python utilities** (used by backend/scripts):
  - `app/backend/db/connection.py`: connection pooling, retry, and health check
  - `app/backend/db/crud.py`: generic insert/select/update/delete helpers
  - `app/backend/db/loader.py`: CSV/JSON loader with row-count + schema-shape validation

### Running the database (and backend)

From `app/backend/`:

```bash
docker compose up --build
```

### Environment variables

The Compose file sets the defaults below (override as needed):

- `POSTGRES_DB=imp`
- `POSTGRES_USER=imp_user`
- `POSTGRES_PASSWORD=imp_password`
- Backend connection vars:
  - `DB_HOST=db`
  - `DB_PORT=5432`
  - `DB_NAME=imp`
  - `DB_USER=imp_user`
  - `DB_PASSWORD=imp_password`

### Loading flat-file data

The loader expects keys that match DB column names (excluding generated columns like primary keys and `created_at`).

Example usage from Python:

```python
from db.loader import load_flat_file

result = load_flat_file(table="influencers", path="path/to/influencers.json")
print(result)
```

### Publishing DS model outputs

The schema includes tables and upsert functions for DS outputs:
- `ds_model_metrics`
- `ds_influencer_predictions`

To publish baseline model metrics from the DS CSV output into Postgres:

```bash
python app/db/tools/publish_ds_metrics.py --csv app/ds/outputs/baseline_model_comparison.csv
```

To publish the DS modeling dataset snapshot into Postgres:

```bash
python app/db/tools/publish_ds_modeling_dataset.py --csv app/ds/outputs/modeling_dataset.csv
```

### Assumptions

- **ERD-aligned schema**: tables/columns match the PM-approved ERD image:
  - `brands`
  - `influencers`
  - `matches`
  - `contact_requests`
  - `past_collaborations`
- **Reference tables** (seeded lookups):
  - `ref_contact_direction`, `ref_contact_status` — FKs from `contact_requests`
  - `ref_audience_age_group`, `ref_audience_gender` — seeded for docs/examples; **`influencers.audience_*` are free-form `VARCHAR`** (migration `0004`, Milestone 3) so APIs can accept display strings
- **`brands`**: `email`, `website`, `instagram` (empty-string defaults until populated)
- **`past_collaborations`**: `campaign_type`, `estimated_reach`, `outcome_tag` (see migration `0004`)
- **DS outputs** are stored in:
  - `ds_model_metrics` (metrics columns match `app/ds/outputs/baseline_model_comparison.csv`)
  - `ds_influencer_predictions` (per-influencer predictions keyed by `(influencer_id, model)`)
- **Upsert mechanism**: use SQL functions to write/overwrite DS results:
  - `upsert_ds_model_metric(...)`
  - `upsert_ds_influencer_prediction(...)`
- **FK load order**: load parent tables before child tables:
  - `brands`, `influencers` → then `matches`, `contact_requests`, `past_collaborations`
- **`content_formats`**: stored as `TEXT` (comma-separated string). The loader will normalize JSON lists into a comma-separated string.

## M4 Validation Notes (Issue #109)

Validated all tables against backend routes and DS scripts:

- `brands` — all columns used by backend endpoints exist ✅
- `influencers` — all columns used by backend and DS scripts exist ✅
- `matches` — UNIQUE(brand_id, influencer_id) confirmed ✅
- `contact_requests` — schema confirmed against backend routes ✅
- `past_collaborations` — campaign_type, estimated_reach, outcome_tag added in M3 ✅
- `ds_model_metrics` — confirmed for DS metric storage ✅
- `ds_influencer_predictions` — confirmed for DS prediction storage ✅
- `ds_modeling_dataset` — confirmed, matches DS output CSV columns exactly ✅

## M4 Stability Notes (Issue #110)

- All upsert functions use ON CONFLICT DO UPDATE — safe for unlimited re-runs ✅
- publish_ds_metrics.py handles null rmse gracefully ✅
- publish_ds_modeling_dataset.py handles bool parsing for CSV inputs ✅
- connect_with_retry() uses exponential backoff — stable under slow DB startup ✅
- All indexes confirmed present for DS and backend query patterns ✅