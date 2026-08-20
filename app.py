"""
V2 entrypoint (scaffold + Phase 2 / 2b service smoke tests).

Production Streamlit Cloud should keep using script.py until Phase 5 cutover.
"""

from __future__ import annotations

import streamlit as st

from config.settings import APP_NAME, APP_VERSION, BUILD_DATE, COMPANY_NAME
from db.sqlite_conn import get_db_connection, init_support_data
from db.supabase_client import is_db_connected
from services.auth import get_all_users, get_role_pages, hash_password, verify_password
from services.nas import compute_nas_changes, load_nas_data
from services.reports import (
    build_excel_report,
    build_technician_performance,
    build_ticket_exec_metrics,
)
from services.tickets import load_tickets, prepare_ticket_view


def main() -> None:
    st.set_page_config(page_title=APP_NAME, page_icon="🛠️", layout="wide")
    st.title(f"{APP_NAME}")
    st.caption(f"V2 scaffold · {APP_VERSION} · build {BUILD_DATE} · {COMPANY_NAME}")

    st.info(
        "This is the **Version 2 scaffold** (Phase 2b: auth + reports). "
        "Production remains on `script.py` until Phase 5 cutover."
    )

    try:
        conn = get_db_connection()
        init_support_data(conn)
        sqlite_status = "Ready"
    except Exception as e:
        conn = None
        sqlite_status = f"Error: {e}"

    try:
        supabase_status = "Connected" if is_db_connected() else "Not configured / local mode"
    except Exception:
        supabase_status = "Not configured / local mode"

    c1, c2 = st.columns(2)
    c1.metric("SQLite support DB", sqlite_status)
    c2.metric("Supabase", supabase_status)

    if sqlite_status == "Ready":
        st.success("config/ and db/ packages imported successfully.")
    else:
        st.error("SQLite init failed — see status above.")

    st.markdown("### Phase 2 — tickets + NAS")
    try:
        tickets = load_tickets()
        nas = load_nas_data()
        ticket_view = prepare_ticket_view(tickets)
        nas_delta = compute_nas_changes(nas)

        m1, m2, m3 = st.columns(3)
        m1.metric("Tickets loaded", len(tickets))
        m2.metric("NAS logs loaded", len(nas))
        m3.metric("NAS delta rows", len(nas_delta))
        st.success("services/tickets.py and services/nas.py OK.")
    except Exception as e:
        tickets = None
        nas = None
        st.error(f"Ticket/NAS smoke test failed: {e}")

    st.markdown("### Phase 2b — auth + reports")
    try:
        sample_hash = hash_password("test-password-only")
        ok = verify_password("test-password-only", sample_hash)
        pages = get_role_pages("IT Manager")
        users_count = 0
        if conn is not None:
            users_count = len(get_all_users(conn))

        a1, a2, a3 = st.columns(3)
        a1.metric("bcrypt round-trip", "OK" if ok else "FAIL")
        a2.metric("IT Manager pages", len(pages))
        a3.metric("Users in SQLite", users_count)

        if tickets is not None and nas is not None:
            metrics = build_ticket_exec_metrics(ticket_view if ticket_view is not None else tickets)
            tech = build_technician_performance(tickets)
            excel_bytes = build_excel_report(tickets, nas)
            r1, r2, r3 = st.columns(3)
            r1.metric("Pending (exec metrics)", metrics.get("pending", 0))
            r2.metric("Tech rows", len(tech))
            r3.metric("Excel bytes", len(excel_bytes))
            st.download_button(
                "Download sample Excel report",
                data=excel_bytes,
                file_name="v2_sample_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        st.success("services/auth.py and services/reports.py OK.")
    except Exception as e:
        st.error(f"Auth/reports smoke test failed: {e}")

    st.markdown(
        """
### Roadmap
1. ~~Phase 1 — config + db~~
2. ~~Phase 2 — services/tickets + services/nas~~
3. ~~Phase 2b — services/auth + services/reports~~ (this build)
4. Phase 3 — extract `ui/`
5. Phase 4 — extract `pages/`
6. Phase 5 — point Streamlit Cloud main file to `app.py`
"""
    )


if __name__ == "__main__":
    main()
