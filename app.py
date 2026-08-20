"""
V2 entrypoint (scaffold only).

Production Streamlit Cloud should keep using script.py until Phase 5 cutover.
This file verifies that config + db packages import cleanly.
"""

from __future__ import annotations

import streamlit as st

from config.settings import APP_NAME, APP_VERSION, BUILD_DATE, COMPANY_NAME
from db.sqlite_conn import get_db_connection, init_support_data
from db.supabase_client import is_db_connected


def main() -> None:
    st.set_page_config(page_title=APP_NAME, page_icon="🛠️", layout="wide")
    st.title(f"{APP_NAME}")
    st.caption(f"V2 scaffold · {APP_VERSION} · build {BUILD_DATE} · {COMPANY_NAME}")

    st.info(
        "This is the **Version 2 scaffold** entrypoint. "
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

    st.markdown(
        """
### Next steps
1. Phase 2 — extract `services/auth.py`, `services/tickets.py`, `services/nas.py`, `services/reports.py`
2. Phase 3 — extract `ui/`
3. Phase 4 — extract `pages/`
4. Phase 5 — point Streamlit Cloud main file to `app.py` (or thin `script.py` shim)

### Optional: local Supabase secrets
Create `.streamlit/secrets.toml` in this project (or `%USERPROFILE%\.streamlit\secrets.toml`):

```toml
[supabase]
url = "https://YOUR_PROJECT.supabase.co"
key = "your-anon-key"
```

Without secrets, the scaffold runs in **local mode** (SQLite only).
"""
    )


if __name__ == "__main__":
    main()
