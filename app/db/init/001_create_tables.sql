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

COMMIT;

