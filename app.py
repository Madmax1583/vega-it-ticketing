"""V2 scaffold entrypoint.

Production Streamlit Cloud remains on main + script.py until the Phase 5 cutover.
This V2-only router exposes the scaffold status screen and read-only Data Quality page.
"""

from __future__ import annotations

import streamlit as st

from config.settings import APP_NAME, APP_VERSION, BUILD_DATE, COMPANY_NAME
from db.sqlite_conn import get_db_connection, init_support_data
from db.supabase_client import is_db_connected
from pages import data_quality
from services.auth import get_all_users, get_role_pages, hash_password, verify_password
from services.nas import compute_nas_changes, load_nas_data
from services.reports import build_excel_report, build_technician_performance, build_ticket_exec_metrics
from services.tickets import load_tickets, prepare_ticket_view
from ui.css import inject_css


V2_ROLE = "IT Manager"
V2_PAGES = ["V2 Status", "Data Quality"]


def resolve_v2_page(requested_page: str | None) -> str:
    """Resolve a V2 scaffold route without allowing unsupported page names."""
    return str(requested_page) if requested_page in V2_PAGES else "V2 Status"


def _render_sidebar() -> str:
    """Render the V2-only controlled selector."""
    with st.sidebar:
        st.markdown("### V2 Scaffold")
        st.caption("Local validation only — production remains on script.py.")
        current = resolve_v2_page(st.session_state.get("v2_page"))
        selected = st.radio("Navigate", V2_PAGES, index=V2_PAGES.index(current), key="v2_router_selector")
        st.session_state["v2_page"] = selected
        return selected


def render_v2_status() -> None:
    """Retain the Phase 1/2/2b smoke dashboard as a V2 page."""
    st.title(APP_NAME)
    st.caption(f"V2 scaffold · {APP_VERSION} · build {BUILD_DATE} · {COMPANY_NAME}")
    st.info("This is the **Version 2 scaffold**. Production remains on `script.py` until the deliberate Phase 5 cutover.")

    try:
        conn = get_db_connection()
        init_support_data(conn)
        sqlite_status = "Ready"
    except Exception as exc:
        conn = None
        sqlite_status = f"Error: {exc}"

    left, right = st.columns(2)
    left.metric("SQLite support DB", sqlite_status)
    right.metric("Supabase", "Connected" if is_db_connected() else "Not configured / local mode")
    if conn is not None:
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
    except Exception as exc:
        tickets = nas = ticket_view = None
        st.error(f"Ticket/NAS smoke test failed: {exc}")

    st.markdown("### Phase 2b — auth + reports")
    try:
        bcrypt_ok = verify_password("test-password-only", hash_password("test-password-only"))
        users_count = len(get_all_users(conn)) if conn is not None else 0
        a1, a2, a3 = st.columns(3)
        a1.metric("bcrypt round-trip", "OK" if bcrypt_ok else "FAIL")
        a2.metric("IT Manager pages", len(get_role_pages(V2_ROLE)))
        a3.metric("Users in SQLite", users_count)
        if tickets is not None and nas is not None:
            metrics = build_ticket_exec_metrics(ticket_view if ticket_view is not None else tickets)
            tech = build_technician_performance(tickets)
            excel_bytes = build_excel_report(tickets, nas)
            r1, r2, r3 = st.columns(3)
            r1.metric("Pending (exec metrics)", metrics.get("pending", 0))
            r2.metric("Tech rows", len(tech))
            r3.metric("Excel bytes", len(excel_bytes))
            st.download_button("Download sample Excel report", data=excel_bytes, file_name="v2_sample_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.success("services/auth.py and services/reports.py OK.")
    except Exception as exc:
        st.error(f"Auth/reports smoke test failed: {exc}")

    st.markdown("""
### V2 roadmap
1. ~~Phase 1 — config + db~~
2. ~~Phase 2 — tickets + NAS services~~
3. ~~Phase 2b — auth + reports services~~
4. ~~Shared UI foundations + Data Quality page~~
5. Next — extract production-equivalent pages one at a time
6. Later — deliberate production cutover
""")


def main() -> None:
    st.set_page_config(page_title=APP_NAME, page_icon="📊", layout="wide")
    inject_css()
    if _render_sidebar() == "Data Quality":
        data_quality.render()
    else:
        render_v2_status()


if __name__ == "__main__":
    main()
