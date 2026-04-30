-- Store DS outputs in Postgres with exact column names.
-- (Milestone 3 DB task: bridge DS artifacts to DB)

BEGIN;

-- 1) ds_model_metrics: DS branch CSV includes `rmse` now; add column and keep upsert compatibility.
ALTER TABLE ds_model_metrics
  ADD COLUMN IF NOT EXISTS rmse NUMERIC;

-- Replace existing upsert function with a v2 signature that includes rmse,
-- and keep a backwards-compatible overload matching the old signature.
DROP FUNCTION IF EXISTS upsert_ds_model_metric(VARCHAR, NUMERIC, NUMERIC, NUMERIC, NUMERIC, TIMESTAMP);

CREATE OR REPLACE FUNCTION upsert_ds_model_metric(
  p_model VARCHAR,
  p_accuracy NUMERIC,
  p_f1 NUMERIC,
  p_precision NUMERIC,
  p_recall NUMERIC,
  p_rmse NUMERIC,
  p_computed_at TIMESTAMP DEFAULT NOW()
) RETURNS VOID AS $$
BEGIN
  INSERT INTO ds_model_metrics (model, accuracy, f1, precision, recall, rmse, computed_at)
  VALUES (p_model, p_accuracy, p_f1, p_precision, p_recall, p_rmse, p_computed_at)
  ON CONFLICT (model) DO UPDATE
  SET accuracy = EXCLUDED.accuracy,
      f1 = EXCLUDED.f1,
      precision = EXCLUDED.precision,
      recall = EXCLUDED.recall,
      rmse = EXCLUDED.rmse,
      computed_at = EXCLUDED.computed_at;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION upsert_ds_model_metric(
  p_model VARCHAR,
  p_accuracy NUMERIC,
  p_f1 NUMERIC,
  p_precision NUMERIC,
  p_recall NUMERIC,
  p_computed_at TIMESTAMP DEFAULT NOW()
) RETURNS VOID AS $$
BEGIN
  PERFORM upsert_ds_model_metric(p_model, p_accuracy, p_f1, p_precision, p_recall, NULL, p_computed_at);
END;
$$ LANGUAGE plpgsql;

-- 2) ds_modeling_dataset: store DS modeling_dataset.csv with exact column names.
CREATE TABLE IF NOT EXISTS ds_modeling_dataset (
  name TEXT NOT NULL,
  niche TEXT NOT NULL,
  follower_count INT NOT NULL CHECK (follower_count >= 0),
  engagement_rate NUMERIC NOT NULL CHECK (engagement_rate >= 0),
  location TEXT NOT NULL,
  campaign_conversions INT NOT NULL CHECK (campaign_conversions >= 0),
  synthetic_data BOOLEAN NOT NULL,
  target_high_performer INT NOT NULL CHECK (target_high_performer IN (0, 1)),
  written_at TIMESTAMP NOT NULL DEFAULT NOW(),
  PRIMARY KEY (name, location)
);

CREATE INDEX IF NOT EXISTS idx_ds_modeling_dataset_niche ON ds_modeling_dataset (niche);
CREATE INDEX IF NOT EXISTS idx_ds_modeling_dataset_location ON ds_modeling_dataset (location);
CREATE INDEX IF NOT EXISTS idx_ds_modeling_dataset_target ON ds_modeling_dataset (target_high_performer);
CREATE INDEX IF NOT EXISTS idx_ds_modeling_dataset_synth ON ds_modeling_dataset (synthetic_data);

COMMIT;

-- Store DS outputs in Postgres with exact column names.
-- (Milestone 3 DB task: bridge DS artifacts to DB)

BEGIN;

-- 1) ds_model_metrics: DS branch CSV includes `rmse` now; add column and keep upsert compatibility.
ALTER TABLE ds_model_metrics
  ADD COLUMN IF NOT EXISTS rmse NUMERIC;

-- Replace existing upsert function with a v2 signature that includes rmse,
-- and keep a backwards-compatible overload matching the old signature.
DROP FUNCTION IF EXISTS upsert_ds_model_metric(VARCHAR, NUMERIC, NUMERIC, NUMERIC, NUMERIC, TIMESTAMP);

CREATE OR REPLACE FUNCTION upsert_ds_model_metric(
  p_model VARCHAR,
  p_accuracy NUMERIC,
  p_f1 NUMERIC,
  p_precision NUMERIC,
  p_recall NUMERIC,
  p_rmse NUMERIC,
  p_computed_at TIMESTAMP DEFAULT NOW()
) RETURNS VOID AS $$
BEGIN
  INSERT INTO ds_model_metrics (model, accuracy, f1, precision, recall, rmse, computed_at)
  VALUES (p_model, p_accuracy, p_f1, p_precision, p_recall, p_rmse, p_computed_at)
  ON CONFLICT (model) DO UPDATE
  SET accuracy = EXCLUDED.accuracy,
      f1 = EXCLUDED.f1,
      precision = EXCLUDED.precision,
      recall = EXCLUDED.recall,
      rmse = EXCLUDED.rmse,
      computed_at = EXCLUDED.computed_at;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION upsert_ds_model_metric(
  p_model VARCHAR,
  p_accuracy NUMERIC,
  p_f1 NUMERIC,
  p_precision NUMERIC,
  p_recall NUMERIC,
  p_computed_at TIMESTAMP DEFAULT NOW()
) RETURNS VOID AS $$
BEGIN
  PERFORM upsert_ds_model_metric(p_model, p_accuracy, p_f1, p_precision, p_recall, NULL, p_computed_at);
END;
$$ LANGUAGE plpgsql;

-- 2) ds_modeling_dataset: store DS modeling_dataset.csv with exact column names.
CREATE TABLE IF NOT EXISTS ds_modeling_dataset (
  name TEXT NOT NULL,
  niche TEXT NOT NULL,
  follower_count INT NOT NULL CHECK (follower_count >= 0),
  engagement_rate NUMERIC NOT NULL CHECK (engagement_rate >= 0),
  location TEXT NOT NULL,
  campaign_conversions INT NOT NULL CHECK (campaign_conversions >= 0),
  synthetic_data BOOLEAN NOT NULL,
  target_high_performer INT NOT NULL CHECK (target_high_performer IN (0, 1)),
  written_at TIMESTAMP NOT NULL DEFAULT NOW(),
  PRIMARY KEY (name, location)
);

CREATE INDEX IF NOT EXISTS idx_ds_modeling_dataset_niche ON ds_modeling_dataset (niche);
CREATE INDEX IF NOT EXISTS idx_ds_modeling_dataset_location ON ds_modeling_dataset (location);
CREATE INDEX IF NOT EXISTS idx_ds_modeling_dataset_target ON ds_modeling_dataset (target_high_performer);
CREATE INDEX IF NOT EXISTS idx_ds_modeling_dataset_synth ON ds_modeling_dataset (synthetic_data);

COMMIT;

