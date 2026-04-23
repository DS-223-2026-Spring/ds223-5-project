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

The loader expects keys that match DB column names (excluding generated columns like `id`, `created_at`).

Example usage from Python:

```python
from db.loader import load_flat_file

result = load_flat_file(table="influencers", path="path/to/influencers.json")
print(result)
```

### Assumptions

- **ERD not present in repo**: schema was inferred from existing FastAPI Pydantic schemas:
  - `app/backend/schemas/influencer.py`
  - `app/backend/schemas/brand.py`
- `content_format_tags` is stored as `TEXT[]` in PostgreSQL.

