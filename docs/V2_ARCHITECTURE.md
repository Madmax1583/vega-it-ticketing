# Version 2 Architecture Plan

**Status:** Phase 2b complete (pending local verify)  
**Production:** Remains on `main` + `script.py` until Phase 5 cutover  
**Branch:** `feature/v2-scaffold`

## Package layout

```
config/          App constants
db/              SQLite + Supabase clients
services/
  tickets.py     Ticket CRUD, normalize, categorize, SLA
  nas.py         NAS CRUD, deltas, forecast
  auth.py        bcrypt auth, users, roles
  reports.py     Summaries, MTTR/SLA, Excel export
ui/              (Phase 3)
pages/           (Phase 4)
app.py           Entrypoint / smoke tests
script.py        Production monolith until cutover
```

## Phases

| Phase | Work | Status |
|-------|------|--------|
| 1 | config + db | Done |
| 2 | tickets + nas services | Done |
| 2b | auth + reports services | Done |
| 3 | ui/* | Next |
| 4 | pages/* | Pending |
| 5 | app.py cutover | Pending |

## Local test

```bash
git pull origin feature/v2-scaffold
python -m streamlit run app.py
```

Expect: tickets/NAS counts, bcrypt OK, users count, Excel download button.
"""
