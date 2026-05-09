-- Migration 0005: M4 validation — confirm DS output tables exist and are stable
-- Issue #108: DS output tables confirmed for prediction storage
-- Issue #109: Schema validated against backend and DS usage
-- Issue #110: Stability confirmed — upserts handle re-runs safely

BEGIN;

-- Issue #108: Ensure DS output tables exist (already created in init, confirmed here)
CREATE TABLE IF NOT EXISTS ds_model_metrics (
  model VARCHAR PRIMARY KEY,
  accuracy NUMERIC NOT NULL,
  f1 NUMERIC NOT NULL,
  precision NUMERIC NOT NULL,
  recall NUMERIC NOT NULL,
  rmse NUMERIC,
  computed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ds_influencer_predictions (
  influencer_id INT NOT NULL REFERENCES influencers (influencer_id) ON DELETE CASCADE,
  model VARCHAR NOT NULL REFERENCES ds_model_metrics (model) ON DELETE CASCADE,
  predicted_label INT,
  predicted_score NUMERIC,
  computed_at TIMESTAMP NOT NULL DEFAULT NOW(),
  PRIMARY KEY (influencer_id, model)
);

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

-- Issue #109: Ensure all indexes exist for backend and DS query patterns
CREATE INDEX IF NOT EXISTS idx_ds_influencer_predictions_model
  ON ds_influencer_predictions (model);
CREATE INDEX IF NOT EXISTS idx_ds_influencer_predictions_influencer_id
  ON ds_influencer_predictions (influencer_id);
CREATE INDEX IF NOT EXISTS idx_ds_modeling_dataset_niche
  ON ds_modeling_dataset (niche);
CREATE INDEX IF NOT EXISTS idx_ds_modeling_dataset_location
  ON ds_modeling_dataset (location);
CREATE INDEX IF NOT EXISTS idx_ds_modeling_dataset_target
  ON ds_modeling_dataset (target_high_performer);
CREATE INDEX IF NOT EXISTS idx_ds_modeling_dataset_synth
  ON ds_modeling_dataset (synthetic_data);

-- Issue #110: Re-create upsert functions safely (OR REPLACE = stable re-runs)
CREATE OR REPLACE FUNCTION upsert_ds_model_metric(
  p_model VARCHAR,
  p_accuracy NUMERIC,
  p_f1 NUMERIC,
  p_precision NUMERIC,
  p_recall NUMERIC,
  p_rmse NUMERIC DEFAULT NULL,
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

CREATE OR REPLACE FUNCTION upsert_ds_influencer_prediction(
  p_influencer_id INT,
  p_model VARCHAR,
  p_predicted_label INT,
  p_predicted_score NUMERIC,
  p_computed_at TIMESTAMP DEFAULT NOW()
) RETURNS VOID AS $$
BEGIN
  INSERT INTO ds_influencer_predictions (
    influencer_id, model, predicted_label, predicted_score, computed_at
  )
  VALUES (p_influencer_id, p_model, p_predicted_label, p_predicted_score, p_computed_at)
  ON CONFLICT (influencer_id, model) DO UPDATE
  SET predicted_label = EXCLUDED.predicted_label,
      predicted_score = EXCLUDED.predicted_score,
      computed_at = EXCLUDED.computed_at;
END;
$$ LANGUAGE plpgsql;

COMMIT;