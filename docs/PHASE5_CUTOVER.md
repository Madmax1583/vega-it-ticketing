# Phase 5 — Production cutover plan

**Status:** Prepared — NOT executed
**Rule:** Do not change Streamlit Cloud main file until the checklist below is green.

## Why not switch today?

| Area | Production script.py | V2 app.py (Phase 4) |
|------|----------------------|---------------------|
| Login / first password | Full | Demo user only |
| Ticket Operations | Full workflow | Simplified log + update |
| NAS Monitoring | Full tabs | Simplified |
| Reports | Advanced management pack | Core summaries + Excel |
| Task Center | Yes | Not extracted |
| Admin Tools | Yes | Not extracted |
| Team Chat | Yes | Not extracted |
| Executive / AVP / Vendor / Assets | Yes | Not extracted |

Switching Cloud to app.py **now** would drop those screens for live users.

## Recommended path

### Option A — Stay on script.py (recommended until parity)

1. Keep Streamlit Cloud Main file = script.py
2. Keep developing on feature/v2-scaffold
3. Extract remaining pages (login, tasks, admin, chat)
4. Local-test full flows
5. Then cut over

### Option B — Dual run (UAT app)

1. Deploy a second Streamlit app from feature/v2-scaffold pointed at app.py for UAT only
2. Keep production URL on script.py
3. Cut over only after UAT sign-off

### Option C — Full cutover (only when ready)

1. Merge feature/v2-scaffold into main via PR
2. Streamlit Cloud → Settings → Main file → app.py
3. Confirm secrets (supabase.url, supabase.key)
4. Smoke-test public URL
5. If broken: set Main file back to script.py immediately

## Pre-cutover checklist

- [ ] Login + first password setup works on V2
- [ ] Ticket create / update / delete works against live Supabase
- [ ] NAS log create / delete works
- [ ] Reports Excel opens correctly
- [ ] Role-based pages match production roles
- [ ] Task Center, Admin, Chat available OR explicitly deferred with management OK
- [ ] Secrets present on Streamlit Cloud
- [ ] Rollback owner assigned (who reverts Main file)

## Rollback (under 2 minutes)

1. Streamlit Cloud → your app → Settings → General
2. Main file path → script.py
3. Save / reboot if needed
4. Confirm old UI loads

## Git safety

Prefer PR: feature/v2-scaffold → main
Do not force-push main.

Tag production before merge:

```
git checkout main
git pull
git tag pre-v2-cutover-YYYYMMDD
git push origin pre-v2-cutover-YYYYMMDD
```

## Decision log

| Date | Decision | By |
|------|----------|----|
| 2026-08-22 | Phase 5 docs only; Cloud stays on script.py | V2 scaffold |
