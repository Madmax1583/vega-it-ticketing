# Version 2 Architecture Plan

**Status:** In progress (scaffold branch only)  
**Production:** Remains on `main` + `script.py` until Phase 5 cutover  
**Branch:** `feature/v2-scaffold`

## Goal

Split the monolith `script.py` (~193 KB) into packages without changing behavior.

## Hybrid data model (unchanged)

| Store | Owns |
|-------|------|
| SQLite (`it_ops.db`) | Auth users, tasks, comments, notifications, vendor follow-ups, chat, user status, assets, auth sessions |
| Supabase | Tickets, NAS backups (and optional cloud users table) |

## Package layout

```
config/          App constants, categories, AI suggestions
db/              SQLite connection/schema + Supabase client
services/        Business logic (auth, tickets, nas, reports, ...)
ui/              CSS, components, navigation, search
pages/           One renderer per major screen
app.py           Entrypoint (Phase 5)
script.py        Production monolith until cutover
```

## Phases

| Phase | Work | Status |
|-------|------|--------|
| 0 | Tag baseline on main | Manual |
| 1 | config + db packages | This branch |
| 2 | services/* extract | Next |
| 3 | ui/* extract | Pending |
| 4 | pages/* extract | Pending |
| 5 | app.py cutover + Streamlit Cloud path | Pending |

## Rules

1. Do not point Streamlit Cloud at this branch until Phase 5.
2. Keep feature parity with current production.
3. Prefer import-and-reuse over copy-paste when thinning `script.py`.
4. Smoke-test after each phase: login, ticket list, NAS, one report export.

## Smoke checklist (every phase)

- [ ] Login / first password setup
- [ ] Home loads KPIs
- [ ] Create or view ticket
- [ ] NAS health tab
- [ ] Reports Excel or CSV download
- [ ] Logout
