"""
V2 entrypoint (scaffold + Phase 2 service smoke tests).

Production Streamlit Cloud should keep using script.py until Phase 5 cutover.
"""

from __future__ import annotations

import streamlit as st

from config.settings import APP_NAME, APP_VERSION, BUILD_DATE, COMPANY_NAME
from db.sqlite_conn import get_db_connection, init_support_data
from db.supabase_client import is_db_connected
from services.nas import compute_nas_changes, load_nas_data
from services.tickets import load_tickets, prepare_ticket_view


def main() -> None:
    st.set_page_config(page_title=APP_NAME, page_icon="🛠️", layout="wide")
    st.title(f"{APP_NAME}")
    st.caption(f"V2 scaffold · {APP_VERSION} · build {BUILD_DATE} · {COMPANY_NAME}")

    st.info(
        "This is the **Version 2 scaffold** entrypoint (Phase 2 services enabled). "
        "Production remains on `script.py` until Phase 5 cutover."
    )

    try:
        conn = get_db_connection()
        init_support_data(conn)
        sqlite_status = "Ready"
    except Exception as e:
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

    st.markdown("### Phase 2 — service smoke test")
    try:
        tickets = load_tickets()
        nas = load_nas_data()
        ticket_view = prepare_ticket_view(tickets)
        nas_delta = compute_nas_changes(nas)

        m1, m2, m3 = st.columns(3)
        m1.metric("Tickets loaded", len(tickets))
        m2.metric("NAS logs loaded", len(nas))
        m3.metric("NAS delta rows", len(nas_delta))

        st.success("services/tickets.py and services/nas.py loaded OK.")

        with st.expander("Sample tickets (local or Supabase)"):
            if ticket_view.empty:
                st.caption("No tickets.")
            else:
                cols = [c for c in ["System Ticket ID", "date", "user_name", "status", "category", "location"] if c in ticket_view.columns]
                st.dataframe(ticket_view[cols].head(10), use_container_width=True)

        with st.expander("Sample NAS logs"):
            if nas.empty:
                st.caption("No NAS logs.")
            else:
                st.dataframe(nas.head(10), use_container_width=True)
    except Exception as e:
        st.error(f"Service smoke test failed: {e}")

    st.markdown(
        """
### Roadmap
1. ~~Phase 1 — config + db~~
2. ~~Phase 2 — services/tickets + services/nas~~ (this build)
3. Phase 2b — services/auth.py + services/reports.py
4. Phase 3 — extract `ui/`
5. Phase 4 — extract `pages/`
6. Phase 5 — point Streamlit Cloud main file to `app.py`

Without `.streamlit/secrets.toml`, ticket/NAS data uses **local sample rows** in session state.
"""
    )


if __name__ == "__main__":
    main()
