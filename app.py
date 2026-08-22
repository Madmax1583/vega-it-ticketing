"""V2 entrypoint — Phase 0 safety + custom page router.

Production Streamlit Cloud must remain on script.py until Phase 6 cutover.
"""

from __future__ import annotations

import streamlit as st

from config.settings import APP_NAME, APP_VERSION, BUILD_DATE, COMPANY_NAME, V2_WRITE_ENABLED
from db.sqlite_conn import get_db_connection, init_support_data
from db.supabase_client import is_db_connected
from ui.theme import inject_scaffold_css
from v2_pages import PAGE_RENDERERS


def _safe_load_tickets():
    try:
        from services.tickets import load_tickets, prepare_ticket_view

        return prepare_ticket_view(load_tickets()), None
    except Exception as e:
        import pandas as pd

        return pd.DataFrame(), str(e)


def _safe_load_nas():
    try:
        from services.nas import load_nas_data

        return load_nas_data(), None
    except Exception as e:
        import pandas as pd

        return pd.DataFrame(), str(e)


def main() -> None:
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="🛠️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_scaffold_css()

    st.title(f"{APP_NAME}")
    st.caption(f"V2 · {APP_VERSION} · build {BUILD_DATE} · {COMPANY_NAME}")

    if not V2_WRITE_ENABLED:
        st.sidebar.warning("Writes DISABLED (safe mode)")
    else:
        st.sidebar.error("Writes ENABLED — live data at risk")

    st.info(
        "**V2 development build.** Production remains on `script.py`. "
        "Custom sidebar only — Streamlit multipage auto-nav is not used."
    )

    try:
        conn = get_db_connection()
        init_support_data(conn)
        sqlite_ok = True
    except Exception as e:
        conn = None
        sqlite_ok = False
        st.error(f"SQLite error: {e}")

    c1, c2, c3 = st.columns(3)
    c1.metric("SQLite", "Ready" if sqlite_ok else "Error")
    c2.metric("Supabase", "Connected" if is_db_connected() else "Local mode")
    c3.metric("Write guard", "OFF (safe)" if not V2_WRITE_ENABLED else "ON")

    tickets, t_err = _safe_load_tickets()
    nas, n_err = _safe_load_nas()
    if t_err:
        st.warning(f"Tickets load issue (showing empty): {t_err}")
    if n_err:
        st.warning(f"NAS load issue (showing empty): {n_err}")

    user = {"display_name": "Amit", "role": "IT Manager", "username": "amit"}

    page_names = list(PAGE_RENDERERS.keys())
    if "v2_page" not in st.session_state or st.session_state["v2_page"] not in page_names:
        st.session_state["v2_page"] = "Home"

    st.sidebar.markdown("### V2 navigation")
    for name in page_names:
        label = f"➤ {name}" if st.session_state["v2_page"] == name else name
        if st.sidebar.button(label, key=f"nav_{name}", use_container_width=True):
            st.session_state["v2_page"] = name
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Tickets: {len(tickets)} · NAS: {len(nas)}")
    st.sidebar.caption("Router: v2_pages")

    current = st.session_state["v2_page"]
    renderer = PAGE_RENDERERS.get(current)
    if renderer is None:
        st.warning(f"No renderer for `{current}`")
        return

    try:
        renderer(user=user, ticket_df=tickets, nas_df=nas, conn=conn)
    except Exception as e:
        st.error(f"Page render failed ({current}): {e}")

    with st.expander("Roadmap (stabilized plan)"):
        st.markdown(
            """
0. ~~V2 safety cleanup~~ (this build)
1. Authentication + roles
2. Safe operational pages (Tickets / NAS / Data Quality)
3. Management report pages
4. SQLite collaboration (Tasks / Admin / Chat)
5. UAT deployment (second Streamlit app)
6. Deliberate cutover — only after UAT sign-off
"""
        )


if __name__ == "__main__":
    main()
