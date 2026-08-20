# Version 2 Architecture Plan

**Status:** Phase 2 in progress  
**Production:** Remains on `main` + `script.py` until Phase 5 cutover  
**Branch:** `feature/v2-scaffold`

## Goal

Split the monolith `script.py` (~193 KB) into packages without changing production behavior.

## Hybrid data model (unchanged)

| Store | Owns |
|-------|------|
| SQLite (`it_ops.db`) | Auth users, tasks, comments, notifications, vendor follow-ups, chat, user status, assets, auth sessions |
| Supabase | Tickets, NAS backups (and optional cloud users table) |

## Package layout

```
config/          App constants, categories, AI suggestions
db/              SQLite connection/schema + Supabase client
services/        Business logic
  tickets.py     Ticket CRUD, normalize, categorize, SLA
  nas.py         NAS CRUD, deltas, forecast
ui/              CSS, components, navigation, search (Phase 3)
pages/           One renderer per major screen (Phase 4)
app.py           Entrypoint / smoke tests
script.py        Production monolith until cutover
```

## Phases

| Phase | Work | Status |
|-------|------|--------|
| 0 | Tag baseline on main | Manual |
| 1 | config + db packages | Done |
| 2 | services/tickets + services/nas | Done |
| 2b | services/auth + services/reports | Next |
| 3 | ui/* extract | Pending |
| 4 | pages/* extract | Pending |
| 5 | app.py cutover + Streamlit Cloud path | Pending |

## Rules

1. Do not point Streamlit Cloud at this branch until Phase 5.
2. Keep feature parity with current production.
3. Prefer import-and-reuse over copy-paste when thinning `script.py`.
4. Smoke-test after each phase: login, ticket list, NAS, one report export.

## Local test

```bash
git checkout feature/v2-scaffold
python -m streamlit run app.py
```

Expect: SQLite Ready, services smoke metrics for tickets/NAS counts.
"""
