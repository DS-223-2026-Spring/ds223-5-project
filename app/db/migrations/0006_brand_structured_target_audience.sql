-- Structured target demographics for brands (parity with influencer audience_* fields).

ALTER TABLE brands
  ADD COLUMN IF NOT EXISTS target_audience_age_group VARCHAR NOT NULL DEFAULT '18-24';

ALTER TABLE brands
  ADD COLUMN IF NOT EXISTS target_audience_gender VARCHAR NOT NULL DEFAULT 'female';

ALTER TABLE brands
  ALTER COLUMN target_audience DROP NOT NULL;

ALTER TABLE brands
  ALTER COLUMN target_audience SET DEFAULT '';
