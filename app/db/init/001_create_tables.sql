-- UGC & Product Meeting Platform - ERD aligned schema.
-- Executed automatically by the Postgres docker image on first startup.
--
-- NOTE: This script is intended for local/dev initialization. It drops existing tables
-- (if present) to ensure the schema matches the PM-approved ERD exactly.

BEGIN;

DROP TABLE IF EXISTS past_collaborations CASCADE;
DROP TABLE IF EXISTS contact_requests CASCADE;
DROP TABLE IF EXISTS matches CASCADE;
DROP TABLE IF EXISTS influencers CASCADE;
DROP TABLE IF EXISTS brands CASCADE;

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
  CONSTRAINT uq_influencers_email UNIQUE (email)
);

CREATE INDEX idx_influencers_niche ON influencers (niche);
CREATE INDEX idx_influencers_location ON influencers (location);

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
  direction VARCHAR NOT NULL,
  message TEXT NOT NULL,
  budget_offer VARCHAR,
  contact_email VARCHAR NOT NULL,
  status VARCHAR NOT NULL,
  sent_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_contact_requests_brand_id ON contact_requests (brand_id);
CREATE INDEX idx_contact_requests_influencer_id ON contact_requests (influencer_id);
CREATE INDEX idx_contact_requests_status ON contact_requests (status);

CREATE TABLE past_collaborations (
  collab_id SERIAL PRIMARY KEY,
  influencer_id INT NOT NULL REFERENCES influencers (influencer_id) ON DELETE CASCADE,
  brand_name VARCHAR NOT NULL,
  brand_category VARCHAR NOT NULL,
  collab_year SMALLINT NOT NULL CHECK (collab_year >= 1900 AND collab_year <= 2100),
  content_type VARCHAR NOT NULL
);

CREATE INDEX idx_past_collaborations_influencer_id ON past_collaborations (influencer_id);

COMMIT;

