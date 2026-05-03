-- UGC & Product Meeting Platform - ERD aligned schema.
-- Executed automatically by the Postgres docker image on first startup.
--
-- NOTE: This script is intended for local/dev initialization. It drops existing tables
-- (if present) to ensure the schema matches the PM-approved ERD exactly.

BEGIN;

DROP TABLE IF EXISTS ds_modeling_dataset CASCADE;
DROP TABLE IF EXISTS ds_influencer_predictions CASCADE;
DROP TABLE IF EXISTS ds_model_metrics CASCADE;
DROP TABLE IF EXISTS ref_audience_gender CASCADE;
DROP TABLE IF EXISTS ref_audience_age_group CASCADE;
DROP TABLE IF EXISTS ref_contact_status CASCADE;
DROP TABLE IF EXISTS ref_contact_direction CASCADE;
DROP TABLE IF EXISTS past_collaborations CASCADE;
DROP TABLE IF EXISTS contact_requests CASCADE;
DROP TABLE IF EXISTS matches CASCADE;
DROP TABLE IF EXISTS influencers CASCADE;
DROP TABLE IF EXISTS brands CASCADE;

-- Reference tables (lookup tables)
CREATE TABLE ref_contact_direction (
  direction VARCHAR PRIMARY KEY
);

CREATE TABLE ref_contact_status (
  status VARCHAR PRIMARY KEY
);

CREATE TABLE ref_audience_age_group (
  age_group VARCHAR PRIMARY KEY
);

CREATE TABLE ref_audience_gender (
  gender VARCHAR PRIMARY KEY
);

INSERT INTO ref_contact_direction (direction) VALUES
  ('brand_to_influencer'),
  ('influencer_to_brand');

INSERT INTO ref_contact_status (status) VALUES
  ('pending'),
  ('accepted'),
  ('rejected'),
  ('closed');

INSERT INTO ref_audience_age_group (age_group) VALUES
  ('13-17'),
  ('18-24'),
  ('25-34'),
  ('35-44'),
  ('45-54'),
  ('55+');

INSERT INTO ref_audience_gender (gender) VALUES
  ('female'),
  ('male'),
  ('non_binary'),
  ('unknown');

CREATE TABLE brands (
  brand_id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL,
  industry VARCHAR NOT NULL,
  location VARCHAR NOT NULL,
  company_size VARCHAR NOT NULL,
  budget_min INT NOT NULL CHECK (budget_min >= 0),
  budget_max INT NOT NULL CHECK (budget_max >= budget_min),
  target_audience TEXT NOT NULL,
  preferred_niches TEXT NOT NULL,
  email VARCHAR NOT NULL DEFAULT '',
  website VARCHAR NOT NULL DEFAULT '',
  instagram VARCHAR NOT NULL DEFAULT '',
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_brands_name UNIQUE (name)
);

CREATE INDEX idx_brands_industry ON brands (industry);
CREATE INDEX idx_brands_location ON brands (location);

CREATE TABLE influencers (
  influencer_id SERIAL PRIMARY KEY,
  handle VARCHAR NOT NULL,
  full_name VARCHAR NOT NULL,
  niche VARCHAR NOT NULL,
  location VARCHAR NOT NULL,
  follower_count INT NOT NULL CHECK (follower_count >= 0),
  engagement_rate NUMERIC NOT NULL CHECK (engagement_rate >= 0),
  audience_age_group VARCHAR NOT NULL,
  audience_gender VARCHAR NOT NULL,
  content_formats TEXT NOT NULL,
  rate_min INT NOT NULL CHECK (rate_min >= 0),
  rate_max INT NOT NULL CHECK (rate_max >= rate_min),
  bio TEXT,
  email VARCHAR NOT NULL,
  is_synthetic BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_influencers_handle UNIQUE (handle),
  CONSTRAINT uq_influencers_email UNIQUE (email),
  CONSTRAINT fk_influencers_audience_age_group FOREIGN KEY (audience_age_group)
    REFERENCES ref_audience_age_group (age_group),
  CONSTRAINT fk_influencers_audience_gender FOREIGN KEY (audience_gender)
    REFERENCES ref_audience_gender (gender)
);

CREATE INDEX idx_influencers_niche ON influencers (niche);
CREATE INDEX idx_influencers_location ON influencers (location);
CREATE INDEX idx_influencers_handle ON influencers (handle);
CREATE INDEX idx_influencers_email ON influencers (email);

CREATE TABLE matches (
  match_id SERIAL PRIMARY KEY,
  brand_id INT NOT NULL REFERENCES brands (brand_id) ON DELETE CASCADE,
  influencer_id INT NOT NULL REFERENCES influencers (influencer_id) ON DELETE CASCADE,
  total_score INT NOT NULL CHECK (total_score >= 0),
  niche_score INT NOT NULL CHECK (niche_score >= 0),
  audience_score INT NOT NULL CHECK (audience_score >= 0),
  engagement_score INT NOT NULL CHECK (engagement_score >= 0),
  history_score INT NOT NULL CHECK (history_score >= 0),
  computed_at TIMESTAMP NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_matches_pair UNIQUE (brand_id, influencer_id)
);

CREATE INDEX idx_matches_brand_id ON matches (brand_id);
CREATE INDEX idx_matches_influencer_id ON matches (influencer_id);

CREATE TABLE contact_requests (
  request_id SERIAL PRIMARY KEY,
  brand_id INT NOT NULL REFERENCES brands (brand_id) ON DELETE CASCADE,
  influencer_id INT NOT NULL REFERENCES influencers (influencer_id) ON DELETE CASCADE,
  direction VARCHAR NOT NULL REFERENCES ref_contact_direction (direction),
  message TEXT NOT NULL,
  budget_offer VARCHAR,
  contact_email VARCHAR NOT NULL,
  status VARCHAR NOT NULL REFERENCES ref_contact_status (status),
  sent_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_contact_requests_brand_id ON contact_requests (brand_id);
CREATE INDEX idx_contact_requests_influencer_id ON contact_requests (influencer_id);
CREATE INDEX idx_contact_requests_status ON contact_requests (status);
CREATE INDEX idx_contact_requests_sent_at ON contact_requests (sent_at);

CREATE TABLE past_collaborations (
  collab_id SERIAL PRIMARY KEY,
  influencer_id INT NOT NULL REFERENCES influencers (influencer_id) ON DELETE CASCADE,
  brand_name VARCHAR NOT NULL,
  brand_category VARCHAR NOT NULL,
  collab_year SMALLINT NOT NULL CHECK (collab_year >= 1900 AND collab_year <= 2100),
  content_type VARCHAR NOT NULL
);

CREATE INDEX idx_past_collaborations_influencer_id ON past_collaborations (influencer_id);

-- DS outputs (model metrics + predictions)
CREATE TABLE ds_model_metrics (
  model VARCHAR PRIMARY KEY,
  accuracy NUMERIC NOT NULL,
  f1 NUMERIC NOT NULL,
  precision NUMERIC NOT NULL,
  recall NUMERIC NOT NULL,
  rmse NUMERIC,
  computed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE ds_influencer_predictions (
  influencer_id INT NOT NULL REFERENCES influencers (influencer_id) ON DELETE CASCADE,
  model VARCHAR NOT NULL REFERENCES ds_model_metrics (model) ON DELETE CASCADE,
  predicted_label INT,
  predicted_score NUMERIC,
  computed_at TIMESTAMP NOT NULL DEFAULT NOW(),
  PRIMARY KEY (influencer_id, model)
);

CREATE INDEX idx_ds_influencer_predictions_model ON ds_influencer_predictions (model);
CREATE INDEX idx_ds_influencer_predictions_influencer_id ON ds_influencer_predictions (influencer_id);

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

-- DS modeling dataset snapshot (matches DS output columns exactly)
CREATE TABLE ds_modeling_dataset (
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

CREATE INDEX idx_ds_modeling_dataset_niche ON ds_modeling_dataset (niche);
CREATE INDEX idx_ds_modeling_dataset_location ON ds_modeling_dataset (location);
CREATE INDEX idx_ds_modeling_dataset_target ON ds_modeling_dataset (target_high_performer);
CREATE INDEX idx_ds_modeling_dataset_synth ON ds_modeling_dataset (synthetic_data);

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

