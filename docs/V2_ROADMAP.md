# V2 Stabilized Roadmap

Production remains: **main → script.py** through Phases 0–6.

## Phase 0 — Safety cleanup

| Task | Status |
|------|--------|
| Rename pages/ → v2_pages/ | Done |
| Custom router only | Done |
| V2_WRITE_ENABLED = False default | Done |
| Safe ticket/NAS load | Done |
| Router smoke tests | Done |

## Next sequence

1. Authentication + roles
2. Safe operational pages (Tickets / NAS / Data Quality)
3. Management report pages
4. SQLite collaboration (Tasks / Admin / Chat)
5. UAT second Streamlit app
6. Deliberate cutover after UAT sign-off

Do not point production Cloud main file at app.py until Phase 6.
