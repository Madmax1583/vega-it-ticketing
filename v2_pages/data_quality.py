"""Data Quality page (V2) — read-only."""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd
import streamlit as st

from services.data_quality import (
    compute_data_quality_metrics,
    compute_department_fragmentation,
    compute_resolution_time_anomalies,
    load_ticket_data_for_quality,
)
from ui.components import render_kpi_card, render_status_table
from ui.navigation import page_breadcrumb


def render_data_quality_page(
    user: Optional[dict] = None,
    ticket_df: Optional[pd.DataFrame] = None,
    nas_df: Optional[pd.DataFrame] = None,
    conn: Any = None,
    **kwargs: Any,
) -> None:
    ticket_df = ticket_df if ticket_df is not None else pd.DataFrame()

    st.markdown(
        f'<div class="sticky-topbar"><div class="crumb">{page_breadcrumb("Data Quality")}</div></div>',
        unsafe_allow_html=True,
    )
    st.subheader("Data Quality")

    if ticket_df.empty:
        st.info("No ticket data loaded.")
        return

    metrics = compute_data_quality_metrics(ticket_df)
    dept_frag = compute_department_fragmentation(ticket_df)
    time_anomalies = compute_resolution_time_anomalies(ticket_df)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Total tickets", len(ticket_df), "All records", "🎫")
    with k2:
        render_kpi_card("Resolved %", metrics.get("resolved_pct", 0), "All tickets", "✅", tone="success")
    with k3:
        render_kpi_card("Dept fragmentation", dept_frag.get("fragmentation_score", 0), "Lower is better", "🧩", tone="warning" if dept_frag.get("fragmentation_score", 0) > 50 else "success")
    with k4:
        render_kpi_card("Time anomalies", len(time_anomalies), "Needs review", "⏱", tone="danger" if len(time_anomalies) else "success")

    st.markdown("#### Department fragmentation")
    if dept_frag.get("departments"):
        frag_df = pd.DataFrame(dept_frag["departments"])
        st.dataframe(frag_df.sort_values("ticket_count", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.caption("No department fragmentation detected.")

    st.markdown("#### Resolution time anomalies")
    if time_anomalies:
        anomaly_df = pd.DataFrame(time_anomalies)
        cols = [c for c in ["id", "user_name", "status", "resolution_time", "flag_reason"] if c in anomaly_df.columns]
        render_status_table(anomaly_df[cols].head(20), cols, compact=True)
    else:
        st.caption("No resolution-time anomalies detected.")

    st.caption(
        "Data Quality is read-only. Use this view to identify tickets that need cleanup "
        "before cutover to V2."
    )
