-- Database initialization for Influencer Matching Platform.
-- This file is executed automatically by the Postgres docker image on first startup.

BEGIN;

CREATE TABLE IF NOT EXISTS influencers (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  niche TEXT NOT NULL,
  follower_count INTEGER NOT NULL CHECK (follower_count >= 0),
  engagement_rate NUMERIC(5, 2) NOT NULL CHECK (engagement_rate >= 0 AND engagement_rate <= 100),
  location TEXT NOT NULL,
  content_format_tags TEXT[] NOT NULL DEFAULT '{}'::TEXT[],
  bio TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_influencers_niche ON influencers (niche);
CREATE INDEX IF NOT EXISTS idx_influencers_location ON influencers (location);
CREATE INDEX IF NOT EXISTS idx_influencers_follower_count ON influencers (follower_count);

CREATE TABLE IF NOT EXISTS brands (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  industry TEXT NOT NULL,
  target_audience_description TEXT NOT NULL,
  budget_range TEXT NOT NULL,
  preferred_niche TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_brands_name UNIQUE (name)
);

CREATE INDEX IF NOT EXISTS idx_brands_preferred_niche ON brands (preferred_niche);

-- Model training runs + persisted inference outputs
-- Note: These tables are intentionally lightweight and can be re-written by DS scripts.
CREATE TABLE IF NOT EXISTS model_runs (
  id BIGSERIAL PRIMARY KEY,
  -- Stable identifier so reruns can update the same row
  run_key TEXT NOT NULL UNIQUE,
  model_name TEXT NOT NULL,
  feature_schema_version TEXT NOT NULL,
  target_definition TEXT NOT NULL,
  dataset_size INTEGER NOT NULL,
  metrics_accuracy DOUBLE PRECISION,
  metrics_f1 DOUBLE PRECISION,
  metrics_roc_auc DOUBLE PRECISION,
  target_median_engagement_rate DOUBLE PRECISION NOT NULL,
  top_tags_json TEXT,
  -- Serialized scikit-learn pipeline (joblib/pickle bytes)
  model_artifact BYTEA,
  artifact_hash TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_model_runs_run_key ON model_runs (run_key);

CREATE TABLE IF NOT EXISTS influencer_predictions (
  id BIGSERIAL PRIMARY KEY,
  model_run_id BIGINT NOT NULL,
  influencer_id BIGINT NOT NULL,

  predicted_label SMALLINT NOT NULL CHECK (predicted_label IN (0, 1)),
  predicted_proba DOUBLE PRECISION NOT NULL CHECK (predicted_proba >= 0 AND predicted_proba <= 1),
  confidence_score DOUBLE PRECISION NOT NULL,

  segment_label TEXT NOT NULL,
  is_recommended BOOLEAN NOT NULL,

  -- Stored for analysis/debugging (target is derived from engagement_rate median)
  target_high_performer_true SMALLINT CHECK (target_high_performer_true IN (0, 1)) ,
  engagement_rate NUMERIC(5, 2) CHECK (engagement_rate >= 0 AND engagement_rate <= 100),
  follower_count INTEGER CHECK (follower_count >= 0),
  niche TEXT,
  location TEXT,
  tag_count INTEGER CHECK (tag_count >= 0),
  bio_length INTEGER CHECK (bio_length >= 0),

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  CONSTRAINT uq_influencer_predictions UNIQUE (model_run_id, influencer_id)
);

CREATE INDEX IF NOT EXISTS idx_influencer_predictions_model_run_id ON influencer_predictions (model_run_id);
CREATE INDEX IF NOT EXISTS idx_influencer_predictions_influencer_id ON influencer_predictions (influencer_id);

COMMIT;

