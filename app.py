"""V2 entrypoint — Phase 4 page router + prior smoke tests."""

from __future__ import annotations

import streamlit as st

from config.settings import APP_NAME, APP_VERSION, BUILD_DATE, COMPANY_NAME
from db.sqlite_conn import get_db_connection, init_support_data
from db.supabase_client import is_db_connected
from pages import PAGE_RENDERERS
from services.nas import load_nas_data
from services.tickets import load_tickets, prepare_ticket_view
from ui.theme import inject_scaffold_css


def main() -> None:
    st.set_page_config(page_title=APP_NAME, page_icon="🛠️", layout="wide")
    inject_scaffold_css()

    st.title(f"{APP_NAME}")
    st.caption(f"V2 scaffold · {APP_VERSION} · build {BUILD_DATE} · {COMPANY_NAME}")
    st.info(
        "**Version 2 scaffold — Phase 4 pages.** "
        "Production remains on `script.py` until Phase 5 cutover."
    )

    try:
        conn = get_db_connection()
        init_support_data(conn)
        sqlite_ok = True
    except Exception as e:
        conn = None
        sqlite_ok = False
        st.error(f"SQLite error: {e}")

    c1, c2 = st.columns(2)
    c1.metric("SQLite", "Ready" if sqlite_ok else "Error")
    c2.metric("Supabase", "Connected" if is_db_connected() else "Local mode")

    tickets = load_tickets()
    nas = load_nas_data()
    ticket_view = prepare_ticket_view(tickets)

    # Demo user for scaffold (no login gate yet)
    user = {"display_name": "Amit", "role": "IT Manager", "username": "amit"}

    page_names = list(PAGE_RENDERERS.keys())
    if "v2_page" not in st.session_state:
        st.session_state["v2_page"] = "Home"

    st.sidebar.markdown("### V2 navigation")
    for name in page_names:
        label = f"➤ {name}" if st.session_state["v2_page"] == name else name
        if st.sidebar.button(label, key=f"nav_{name}", use_container_width=True):
            st.session_state["v2_page"] = name
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Tickets: {len(tickets)} · NAS: {len(nas)}")
    st.sidebar.success("Phase 4 page router active")

    current = st.session_state["v2_page"]
    renderer = PAGE_RENDERERS.get(current)
    if renderer is None:
        st.warning(f"No renderer for `{current}`")
        return

    try:
        renderer(
            user=user,
            ticket_df=ticket_view if current != "Home" else tickets,
            nas_df=nas,
            conn=conn,
        )
        st.sidebar.caption(f"Rendered: {current}")
    except Exception as e:
        st.error(f"Page render failed ({current}): {e}")

    with st.expander("Phase checklist"):
        st.markdown(
            """
1. ~~Phase 1 — config + db~~
2. ~~Phase 2 — services/tickets + nas~~
3. ~~Phase 2b — auth + reports~~
4. ~~Phase 3 — ui/~~
5. ~~Phase 4 — pages/~~ (this build)
6. Phase 5 — point Streamlit Cloud to `app.py`
"""
        )


if __name__ == "__main__":
    main()
