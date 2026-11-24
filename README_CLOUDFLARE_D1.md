# Cloudflare D1 local migration

This branch contains the initial local scaffold for migrating Vega Ticketing
from Supabase PostgreSQL to Cloudflare D1.

## Current status

- The application still uses Supabase in `main`.
- This branch does **not** change the live application.
- The D1 schema is an initial scaffold and must be aligned with the actual
  Supabase tables before production migration.
- Local development uses SQLite through `db/local_database.py`.

## Files

- `migrations/d1_schema.sql`: Initial SQLite/D1 schema.
- `db/local_database.py`: Local SQLite database adapter.
- `tests/test_local_database.py`: Basic adapter tests.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest
```

## Create a local database

```python
from db.local_database import LocalDatabase

database = LocalDatabase("data/vega_ticketing_local.db")
database.initialize("migrations/d1_schema.sql")
```

## Next steps

1. Inspect the live Supabase schema after restoring the project.
2. Replace this scaffold schema with the exact production table definitions.
3. Add a D1-compatible database adapter.
4. Replace Supabase calls in the application with the database service layer.
5. Test locally with sample data.
6. Export and convert Supabase PostgreSQL data only when ready for staging.
7. Import converted data into a staging D1 database.
8. Validate before populating production D1.

## Important

Cloudflare D1 uses SQLite semantics. PostgreSQL data cannot be imported
directly into D1; it must be converted to SQLite-compatible SQL first.
