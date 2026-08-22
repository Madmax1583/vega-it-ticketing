"""NAS Monitoring page (V2 Phase 4)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

import pandas as pd
import streamlit as st

from config.settings import SERVER_NAMES
from services.nas import compute_nas_changes, save_nas_log
from ui.components import render_kpi_card, render_status_table
from ui.navigation import page_breadcrumb


def render_nas_page(
    user: Optional[dict] = None,
    ticket_df: Optional[pd.DataFrame] = None,
    nas_df: Optional[pd.DataFrame] = None,
    conn: Any = None,
    **kwargs: Any,
) -> None:
    nas_df = nas_df if nas_df is not None else pd.DataFrame()

    st.markdown(
        f'<div class="sticky-topbar"><div class="crumb">{page_breadcrumb("NAS Monitoring")}</div></div>',
        unsafe_allow_html=True,
    )
    st.subheader("NAS Monitoring")

    servers = SERVER_NAMES if SERVER_NAMES else ["HRI", "Vega", "Sery", "Rise"]
    total = len(nas_df)
    fails = int((nas_df["status"].astype(str) == "Failed").sum()) if not nas_df.empty and "status" in nas_df.columns else 0
    success = total - fails

    k1, k2, k3 = st.columns(3)
    with k1:
        render_kpi_card("Total logs", total, "All servers", "🖥")
    with k2:
        render_kpi_card("Success", success, "Completed backups", "✅", tone="success")
    with k3:
        render_kpi_card("Failed", fails, "Needs attention", "⚠", tone="danger" if fails else "success")

    t1, t2 = st.tabs(["Log entry", "Health / deltas"])

    with t1:
        with st.form("v2_nas_form", clear_on_submit=True):
            n1, n2 = st.columns(2)
            log_date = n1.date_input("Backup date", value=datetime.now().date())
            server_name = n2.selectbox("Server", servers)
            n3, n4 = st.columns(2)
            log_status = n3.selectbox("Status", ["Success", "Failed"])
            storage_gb = n4.number_input("Storage used (GB)", min_value=0.0, step=0.0001, format="%.4f")
            remarks = st.text_area("Remarks", height=80)
            if st.form_submit_button("Submit backup log", use_container_width=True):
                try:
                    new_id = save_nas_log(
                        {
                            "date": log_date.strftime("%Y-%m-%d"),
                            "server_name": server_name,
                            "status": log_status,
                            "storage_used": float(storage_gb),
                            "remarks": remarks.strip(),
                        }
                    )
                    st.success(f"NAS log saved. ID: {new_id}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Save failed: {e}")

    with t2:
        if nas_df.empty:
            st.info("No NAS logs loaded.")
        else:
            deltas = compute_nas_changes(nas_df)
            cols = [
                c
                for c in [
                    "id",
                    "date",
                    "server_name",
                    "status",
                    "storage_used",
                    "delta_gb",
                    "change_type",
                    "remarks",
                ]
                if c in deltas.columns or c in nas_df.columns
            ]
            show = deltas if not deltas.empty else nas_df
            safe = [c for c in cols if c in show.columns]
            render_status_table(
                show.sort_values("date", ascending=False).head(20) if "date" in show.columns else show.head(20),
                safe,
                compact=True,
                nas_mode=True,
            )
