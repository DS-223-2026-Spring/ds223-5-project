-- Issue #73 (constraints/indexes/reference tables)
-- Issue #M3 DS addition (store model outputs/predictions + upsert mechanism)

BEGIN;

-- Reference tables (lookup tables) used by application workflows.
-- Using VARCHAR primary keys so existing ERD column types remain unchanged.
CREATE TABLE IF NOT EXISTS ref_contact_direction (
  direction VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS ref_contact_status (
  status VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS ref_audience_age_group (
  age_group VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS ref_audience_gender (
  gender VARCHAR PRIMARY KEY
);

-- Seed common reference values (idempotent).
INSERT INTO ref_contact_direction (direction) VALUES
  ('brand_to_influencer'),
  ('influencer_to_brand')
ON CONFLICT DO NOTHING;

INSERT INTO ref_contact_status (status) VALUES
  ('pending'),
  ('accepted'),
  ('rejected'),
  ('closed')
ON CONFLICT DO NOTHING;

-- Enforce referential integrity via FKs (keep ERD columns as-is).
ALTER TABLE contact_requests
  ADD CONSTRAINT fk_contact_requests_direction
  FOREIGN KEY (direction) REFERENCES ref_contact_direction (direction);

ALTER TABLE contact_requests
  ADD CONSTRAINT fk_contact_requests_status
  FOREIGN KEY (status) REFERENCES ref_contact_status (status);

ALTER TABLE influencers
  ADD CONSTRAINT fk_influencers_audience_age_group
  FOREIGN KEY (audience_age_group) REFERENCES ref_audience_age_group (age_group);

ALTER TABLE influencers
  ADD CONSTRAINT fk_influencers_audience_gender
  FOREIGN KEY (audience_gender) REFERENCES ref_audience_gender (gender);

-- Helpful indexes for frequent filtering.
CREATE INDEX IF NOT EXISTS idx_influencers_handle ON influencers (handle);
CREATE INDEX IF NOT EXISTS idx_influencers_email ON influencers (email);
CREATE INDEX IF NOT EXISTS idx_matches_computed_at ON matches (computed_at);
CREATE INDEX IF NOT EXISTS idx_contact_requests_sent_at ON contact_requests (sent_at);

-- DS outputs: model metrics and per-influencer predictions.
-- Column names match DS output fields in `app/ds/outputs/baseline_model_comparison.csv`.
CREATE TABLE IF NOT EXISTS ds_model_metrics (
  model VARCHAR PRIMARY KEY,
  accuracy NUMERIC NOT NULL,
  f1 NUMERIC NOT NULL,
  precision NUMERIC NOT NULL,
  recall NUMERIC NOT NULL,
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

CREATE INDEX IF NOT EXISTS idx_ds_influencer_predictions_model ON ds_influencer_predictions (model);

-- Upsert functions so DS/backend can write/overwrite results safely.
CREATE OR REPLACE FUNCTION upsert_ds_model_metric(
  p_model VARCHAR,
  p_accuracy NUMERIC,
  p_f1 NUMERIC,
  p_precision NUMERIC,
  p_recall NUMERIC,
  p_computed_at TIMESTAMP DEFAULT NOW()
) RETURNS VOID AS $$
BEGIN
  INSERT INTO ds_model_metrics (model, accuracy, f1, precision, recall, computed_at)
  VALUES (p_model, p_accuracy, p_f1, p_precision, p_recall, p_computed_at)
  ON CONFLICT (model) DO UPDATE
  SET accuracy = EXCLUDED.accuracy,
      f1 = EXCLUDED.f1,
      precision = EXCLUDED.precision,
      recall = EXCLUDED.recall,
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

