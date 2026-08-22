"""V2 entrypoint — Phase 0 safety + Phase 1 auth/role router.

Production Streamlit Cloud must remain on script.py until Phase 6 cutover.
"""

from __future__ import annotations

import streamlit as st

from config.settings import (
    APP_NAME,
    APP_VERSION,
    BUILD_DATE,
    COMPANY_NAME,
    ROLE_PAGES,
    V2_WRITE_ENABLED,
)
from db.sqlite_conn import get_db_connection, init_support_data
from db.supabase_client import is_db_connected
from services.auth import (
    authenticate_user,
    get_role_pages,
    hash_password,
    set_first_password,
    verify_password,
)
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


def _ensure_session_keys() -> None:
    defaults = {
        "authenticated": False,
        "user": None,
        "must_change_password": False,
        "v2_page": "Home",
        "auth_error": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _render_login(conn) -> None:
    st.markdown("### 🔐 Sign in")
    st.caption("V2 local auth (SQLite). Production app remains on script.py.")
    with st.form("v2_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
        if submitted:
            if not username.strip() or not password:
                st.session_state["auth_error"] = "Enter username and password."
            else:
                try:
                    user = authenticate_user(conn, username.strip(), password)
                    if user is None:
                        st.session_state["auth_error"] = "Invalid username or password."
                    else:
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = user
                        st.session_state["must_change_password"] = bool(
                            user.get("must_change_password")
                        )
                        st.session_state["auth_error"] = ""
                        st.session_state["v2_page"] = "Home"
                        st.rerun()
                except Exception as e:
                    st.session_state["auth_error"] = f"Login error: {e}"
    if st.session_state.get("auth_error"):
        st.error(st.session_state["auth_error"])
    st.info("Default seed password for new users: `ChangeMe123!` (change on first login).")


def _render_first_password(conn) -> None:
    user = st.session_state.get("user") or {}
    st.markdown("### 🔑 Set a new password")
    st.caption(f"Account: **{user.get('username')}** — first login requires a password change.")
    with st.form("v2_first_password"):
        p1 = st.text_input("New password", type="password")
        p2 = st.text_input("Confirm password", type="password")
        ok = st.form_submit_button("Save password", type="primary")
        if ok:
            if len(p1) < 8:
                st.error("Password must be at least 8 characters.")
            elif p1 != p2:
                st.error("Passwords do not match.")
            else:
                try:
                    set_first_password(conn, user.get("username"), p1)
                    st.session_state["must_change_password"] = False
                    if st.session_state.get("user"):
                        st.session_state["user"]["must_change_password"] = False
                    st.success("Password updated. Continue to the dashboard.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not update password: {e}")


def _allowed_pages(role: str) -> list:
    """Intersection of role map and pages that actually have renderers."""
    role_list = get_role_pages(role) if role else ROLE_PAGES.get("User", ["Home"])
    available = set(PAGE_RENDERERS.keys())
    pages = [p for p in role_list if p in available]
    if not pages:
        pages = [p for p in ["Home"] if p in available] or list(available)[:1]
    return pages


def main() -> None:
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="🛠️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_scaffold_css()
    _ensure_session_keys()

    st.title(f"{APP_NAME}")
    st.caption(f"V2 · {APP_VERSION} · build {BUILD_DATE} · {COMPANY_NAME}")

    try:
        conn = get_db_connection()
        init_support_data(conn)
        sqlite_ok = True
    except Exception as e:
        conn = None
        sqlite_ok = False
        st.error(f"SQLite error: {e}")
        st.stop()

    if not V2_WRITE_ENABLED:
        st.sidebar.warning("Writes DISABLED (safe mode)")
    else:
        st.sidebar.error("Writes ENABLED — live data at risk")

    # ---- Auth gate ----
    if not st.session_state["authenticated"]:
        c1, c2, c3 = st.columns(3)
        c1.metric("SQLite", "Ready" if sqlite_ok else "Error")
        c2.metric("Supabase", "Connected" if is_db_connected() else "Local mode")
        c3.metric("Write guard", "OFF (safe)" if not V2_WRITE_ENABLED else "ON")
        _render_login(conn)
        return

    if st.session_state.get("must_change_password"):
        _render_first_password(conn)
        return

    user = st.session_state.get("user") or {}
    role = user.get("role", "User")
    allowed = _allowed_pages(role)

    st.sidebar.markdown(f"**{user.get('display_name', user.get('username', 'User'))}**")
    st.sidebar.caption(f"Role: {role}")
    if st.sidebar.button("Log out", use_container_width=True):
        for k in ["authenticated", "user", "must_change_password", "auth_error"]:
            st.session_state[k] = False if k == "authenticated" else (None if k == "user" else False if k == "must_change_password" else "")
        st.session_state["authenticated"] = False
        st.session_state["user"] = None
        st.session_state["must_change_password"] = False
        st.session_state["v2_page"] = "Home"
        st.rerun()

    st.sidebar.markdown("### Navigation")
    if st.session_state["v2_page"] not in allowed:
        st.session_state["v2_page"] = allowed[0]

    for name in allowed:
        label = f"➤ {name}" if st.session_state["v2_page"] == name else name
        if st.sidebar.button(label, key=f"nav_{name}", use_container_width=True):
            st.session_state["v2_page"] = name
            st.rerun()

    tickets, t_err = _safe_load_tickets()
    nas, n_err = _safe_load_nas()
    if t_err:
        st.warning(f"Tickets load issue (showing empty): {t_err}")
    if n_err:
        st.warning(f"NAS load issue (showing empty): {n_err}")

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Tickets: {len(tickets)} · NAS: {len(nas)}")
    st.sidebar.caption("Phase 1: auth + role router")

    current = st.session_state["v2_page"]
    if current not in allowed:
        st.error("You do not have access to this page.")
        return

    renderer = PAGE_RENDERERS.get(current)
    if renderer is None:
        st.warning(f"Page `{current}` is allowed for your role but not implemented in V2 yet.")
        return

    try:
        renderer(user=user, ticket_df=tickets, nas_df=nas, conn=conn)
    except Exception as e:
        st.error(f"Page render failed ({current}): {e}")

    with st.expander("Roadmap"):
        st.markdown(
            """
0. ~~Safety cleanup~~
1. ~~Authentication + roles~~ (this build)
2. Safe operational pages
3. Management report pages
4. SQLite collaboration
5. UAT deployment
6. Cutover after UAT sign-off
"""
        )


if __name__ == "__main__":
    main()
