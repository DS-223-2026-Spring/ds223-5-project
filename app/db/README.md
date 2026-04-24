## Database (PostgreSQL) setup

This project uses a PostgreSQL container named `db` (via Docker Compose) and initializes the schema from SQL files in `app/db/init/`.

### What’s included

- **Docker Compose service**: `db` running PostgreSQL with port mapping **5432:5432**
- **Initialization SQL**: `app/db/init/001_create_tables.sql`
- **Python utilities** (used by backend/scripts):
  - `app/backend/db/connection.py`: connection pooling, retry, and health check
  - `app/backend/db/crud.py`: generic insert/select/update/delete helpers
  - `app/backend/db/loader.py`: CSV/JSON loader with row-count + schema-shape validation

### Running the database (and backend)

From `app/backend/`:

```bash
docker compose up --build
```

### Environment variables

The Compose file sets the defaults below (override as needed):

- `POSTGRES_DB=imp`
- `POSTGRES_USER=imp_user`
- `POSTGRES_PASSWORD=imp_password`
- Backend connection vars:
  - `DB_HOST=db`
  - `DB_PORT=5432`
  - `DB_NAME=imp`
  - `DB_USER=imp_user`
  - `DB_PASSWORD=imp_password`

### Loading flat-file data

The loader expects keys that match DB column names (excluding generated columns like primary keys and `created_at`).

Example usage from Python:

```python
from db.loader import load_flat_file

result = load_flat_file(table="influencers", path="path/to/influencers.json")
print(result)
```

### Assumptions

- **ERD-aligned schema**: tables/columns match the PM-approved ERD image:
  - `brands`
  - `influencers`
  - `matches`
  - `contact_requests`
  - `past_collaborations`
- **FK load order**: load parent tables before child tables:
  - `brands`, `influencers` → then `matches`, `contact_requests`, `past_collaborations`
- **`content_formats`**: stored as `TEXT` (comma-separated string). The loader will normalize JSON lists into a comma-separated string.

