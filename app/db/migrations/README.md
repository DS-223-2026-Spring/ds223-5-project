## SQL migrations (no migration framework)

This project does not currently use Alembic/Flyway/etc. For Milestone 3, database changes are captured as plain SQL scripts in this folder.

### How to apply

Run migrations in numeric order against the target database.

Example with `psql`:

```bash
psql "$DATABASE_URL" -f app/db/migrations/0001_recreate_core_tables_per_erd.sql
psql "$DATABASE_URL" -f app/db/migrations/0002_add_reference_tables_constraints_and_ds_outputs.sql
```

### Notes

- These scripts are intended for **local/dev** usage.
- Some migrations may be **destructive** (drop/recreate) to guarantee alignment with the PM-approved ERD.
- Migrations are tagged by issue intent:
  - `0001_*`: Issue #72 (core ERD tables)
  - `0002_*`: Issue #73 + DS outputs tables/functions for Milestone 3

