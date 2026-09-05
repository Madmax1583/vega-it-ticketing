"""Reports page (V2 Phase 4)."""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd
import streamlit as st

from services.reports import (
    build_department_summary,
    build_excel_report,
    build_location_summary,
    build_technician_performance,
    build_ticket_exec_metrics,
)
from ui.components import render_kpi_card
from ui.navigation import page_breadcrumb


def render_reports_page(
    user: Optional[dict] = None,
    ticket_df: Optional[pd.DataFrame] = None,
    nas_df: Optional[pd.DataFrame] = None,
    conn: Any = None,
    **kwargs: Any,
) -> None:
    ticket_df = ticket_df if ticket_df is not None else pd.DataFrame()
    nas_df = nas_df if nas_df is not None else pd.DataFrame()

    st.markdown(
        f'<div class="sticky-topbar"><div class="crumb">{page_breadcrumb("Reports")}</div></div>',
        unsafe_allow_html=True,
    )
    st.subheader("Reports")

    metrics = build_ticket_exec_metrics(ticket_df)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Pending", metrics.get("pending", 0), "Open queue", "🎫", tone="warning")
    with k2:
        render_kpi_card("Overdue", metrics.get("overdue", 0), "SLA risk", "🚨", tone="danger")
    with k3:
        render_kpi_card("Avg resolution", metrics.get("avg_resolution", 0), "Minutes", "⏱")
    with k4:
        render_kpi_card("Resolution %", metrics.get("resolution_rate", 0), "Close rate", "🎯", tone="success")

    tabs = st.tabs(["Technician", "Department", "Location", "Excel export"])

    with tabs[0]:
        frame = build_technician_performance(ticket_df)
        if frame.empty:
            st.info("No technician data.")
        else:
            st.dataframe(frame, use_container_width=True, hide_index=True)

    with tabs[1]:
        frame = build_department_summary(ticket_df)
        if frame.empty:
            st.info("No department data.")
        else:
            st.dataframe(frame, use_container_width=True, hide_index=True)

    with tabs[2]:
        frame = build_location_summary(ticket_df)
        if frame.empty:
            st.info("No location data.")
        else:
            st.dataframe(frame, use_container_width=True, hide_index=True)

    with tabs[3]:
        try:
            blob = build_excel_report(ticket_df, nas_df)
            st.download_button(
                "Download multi-sheet Excel report",
                data=blob,
                file_name="vega_knitpro_v2_reports.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
            )
            st.caption(f"Workbook size: {len(blob):,} bytes")
        except Exception as e:
            st.error(f"Excel build failed: {e}")
