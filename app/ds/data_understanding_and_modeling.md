# Data Understanding and Modeling Notes

## Available data
The current DS workflow uses influencer-level records with:
- `name`
- `niche`
- `follower_count`
- `engagement_rate`
- `location`
- `campaign_conversions`
- `synthetic_data` (explicit label indicating simulated rows)

## Missing fields and quality issues
- Missing richer campaign outcomes such as spend, revenue, and ROI.
- No temporal fields (post cadence, growth trends, seasonality).
- Limited real records can bias baseline model quality.
- Free-text categories (`niche`, `location`) may become inconsistent over time.

## Modeling opportunities
- Predict high-performing creators before campaign launch.
- Add ranking/regression models for expected conversions or ROI.
- Use segment models by niche and geography for personalization.

## Synthetic data labeling
- Synthetic records are explicitly marked with `synthetic_data = True`.
- Real seed rows are marked with `synthetic_data = False`.
- Synthetic records are generated only to support baseline model training stability.

## Feature set
- Numeric features: `follower_count`, `engagement_rate`, `campaign_conversions`
- Categorical features: `niche`, `location`
- Metadata field: `synthetic_data` (tracking data provenance)

## Target variable definition
- `target_high_performer` is defined as:
  - `1` if `engagement_rate >= median(engagement_rate)`
  - `0` otherwise

This is a practical proxy target for initial classification while richer business
labels are unavailable.

## Baseline model assumptions
- Engagement rate is treated as an early proxy for creator performance.
- Synthetic data roughly reflects plausible production ranges.
- Baseline metrics (`accuracy`, `F1`, `RMSE`) are for initial comparison, not
  production deployment decisions.
