"""V2 entrypoint (scaffold through Phase 3 UI smoke tests)."""

from __future__ import annotations

import streamlit as st

from config.settings import APP_NAME, APP_VERSION, BUILD_DATE, COMPANY_NAME
from db.sqlite_conn import get_db_connection, init_support_data
from db.supabase_client import is_db_connected
from services.auth import get_all_users, get_role_pages, hash_password, verify_password
from services.nas import compute_nas_changes, load_nas_data
from services.reports import build_excel_report, build_technician_performance, build_ticket_exec_metrics
from services.tickets import load_tickets, prepare_ticket_view
from ui.components import render_kpi_card, render_status_table, status_badge_html
from ui.navigation import get_navigation_groups, page_breadcrumb
from ui.theme import inject_scaffold_css


def main() -> None:
    st.set_page_config(page_title=APP_NAME, page_icon="🛠️", layout="wide")
    inject_scaffold_css()

    st.title(f"{APP_NAME}")
    st.caption(f"V2 scaffold · {APP_VERSION} · build {BUILD_DATE} · {COMPANY_NAME}")
    st.info(
        "This is the **Version 2 scaffold** (Phase 3: UI). "
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

    st.markdown("### Phase 2 — tickets + NAS")
    tickets = nas = ticket_view = None
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
        st.error(f"Ticket/NAS smoke test failed: {e}")

    st.markdown("### Phase 2b — auth + reports")
    try:
        sample_hash = hash_password("test-password-only")
        ok = verify_password("test-password-only", sample_hash)
        pages = get_role_pages("IT Manager")
        users_count = len(get_all_users(conn)) if conn is not None else 0
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

    st.markdown("### Phase 3 — UI components")
    try:
        groups = get_navigation_groups("IT Manager")
        crumb = page_breadcrumb("Ticket Operations")
        st.markdown(
            f'<div class="sticky-topbar"><div class="crumb">{crumb}</div>'
            f'<div class="hero-title" style="font-size:20px;margin:0">UI smoke test</div></div>',
            unsafe_allow_html=True,
        )
        k1, k2, k3 = st.columns(3)
        with k1:
            render_kpi_card("Open Tickets", 2, "Sample KPI", "🎫", tone="warning")
        with k2:
            render_kpi_card("Resolved", 1, "Sample KPI", "✅", tone="success")
        with k3:
            render_kpi_card("Nav groups", len(groups), "IT Manager", "📂")
        st.markdown(
            f"**Status chips:** {status_badge_html('Open')} {status_badge_html('Resolved')} "
            f"{status_badge_html('In Progress')} {status_badge_html('On Hold')}",
            unsafe_allow_html=True,
        )
        if ticket_view is not None and not ticket_view.empty:
            cols = [
                c for c in ["System Ticket ID", "date", "user_name", "status", "category", "location"]
                if c in ticket_view.columns
            ]
            st.caption("Status table (local sample tickets)")
            render_status_table(ticket_view.head(5), cols, compact=True)
        st.success("ui/theme.py, ui/components.py, ui/navigation.py OK.")
    except Exception as e:
        st.error(f"UI smoke test failed: {e}")

    st.markdown(
        """
### Roadmap
1. ~~Phase 1 — config + db~~
2. ~~Phase 2 — services/tickets + services/nas~~
3. ~~Phase 2b — services/auth + services/reports~~
4. ~~Phase 3 — ui/~~ (this build)
5. Phase 4 — extract `pages/`
6. Phase 5 — point Streamlit Cloud main file to `app.py`
"""
    )


if __name__ == "__main__":
    main()
