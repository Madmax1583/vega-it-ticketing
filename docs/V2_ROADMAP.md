# V2 Stabilized Roadmap

Production remains: **main → script.py** through Phases 0–6.

## Phase 0 — Safety cleanup
Done: `v2_pages/`, write guard, safe loads, router tests.

## Phase 1 — Authentication and roles
Done: login, first password, logout, role-filtered nav.

## Phase 2 — Safe operational pages (current)

| Task | Status |
|------|--------|
| Ticket create/update validation | Done |
| Start/close times + resolution duration | Done |
| NAS validation + safe banner | Done |
| Data Quality read-only | Done |
| `V2_WRITE_ENABLED = False` default | Done |

**Exit:** Forms reviewable; buttons disabled in safe mode; enable writes only for UAT.

To enable writes for approved UAT only:

```python
# config/settings.py
V2_WRITE_ENABLED = True
```

## Phase 3 — Management report pages
Home polish, Executive, Reports depth, AVP, Dept Health, Vendor, Assets.

## Phase 4 — SQLite collaboration
Tasks, Admin, Chat, notifications, vendor follow-ups.

## Phase 5 — UAT second Streamlit app

## Phase 6 — Cutover after UAT sign-off
"""
