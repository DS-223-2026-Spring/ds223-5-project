## SQL migrations (no migration framework)

This project does not currently use Alembic/Flyway/etc. For Milestone 3, database changes are captured as plain SQL scripts in this folder.

### How to apply

Run migrations in numeric order against the target database.

### Notes

- These scripts are intended for **local/dev** usage.
- Some migrations may be **destructive** (drop/recreate) to guarantee alignment with the PM-approved ERD.

