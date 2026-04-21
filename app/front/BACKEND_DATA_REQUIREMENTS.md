# Frontend ↔ Backend Data Requirements

## Page 1: Create Carousels
- **POST** `/carousels/` — Create a new carousel with variants
  - Request: carousel name, list of variant labels/content
  - Response: carousel ID, creation status

## Page 2: Interaction
- **GET** `/carousels/{id}` — Fetch carousel and its variants
- **GET** `/carousels/{id}/recommend` — Get the bandit model's recommended variant
- **POST** `/interactions/` — Log a user interaction (click/impression)
  - Request: carousel ID, variant ID, interaction type (click/skip)

## Page 3: Analytics
- **GET** `/analytics/carousels` — Summary stats per carousel
- **GET** `/analytics/carousels/{id}/performance` — Time-series performance data
  - Response: timestamps, CTR per variant, reward history, arm selection counts

## Notes
- Endpoint names may be aligned to backend conventions after API contract review.
- Authentication, pagination, and error schema requirements are pending definition.
