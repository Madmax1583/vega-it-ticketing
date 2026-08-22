"""Data Quality page (V2) — read-only.

Uses services.data_quality.profile_tickets / profile_nas / build_data_quality_report.
"""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd
import streamlit as st

from services.data_quality import build_data_quality_report
from ui.components import render_kpi_card
from ui.navigation import page_breadcrumb


def render_data_quality_page(
    user: Optional[dict] = None,
    ticket_df: Optional[pd.DataFrame] = None,
    nas_df: Optional[pd.DataFrame] = None,
    conn: Any = None,
    **kwargs: Any,
) -> None:
    ticket_df = ticket_df if ticket_df is not None else pd.DataFrame()
    nas_df = nas_df if nas_df is not None else pd.DataFrame()

    st.markdown(
        f'<div class="sticky-topbar"><div class="crumb">{page_breadcrumb("Data Quality")}</div></div>',
        unsafe_allow_html=True,
    )
    st.subheader("Data Quality")
    st.caption("Read-only profiling. No writes to Supabase or SQLite.")

    report = build_data_quality_report(ticket_df, nas_df)
    tickets = report.get("tickets", {})
    nas = report.get("nas", {})
    warnings = report.get("warnings", [])

    t_sum = tickets.get("summary", {})
    n_sum = nas.get("summary", {})

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Tickets", t_sum.get("ticket_count", 0), "All records", "🎫")
    with k2:
        render_kpi_card("Statuses", t_sum.get("status_count", 0), "Distinct status values", "📋")
    with k3:
        render_kpi_card("Departments", t_sum.get("department_count", 0), "Distinct departments", "🧩")
    with k4:
        render_kpi_card(
            "NAS freshness",
            n_sum.get("freshness", "n/a"),
            f"Latest: {n_sum.get('latest_log_date') or '—'}",
            "🖥",
            tone="warning" if n_sum.get("freshness") == "stale" else "success",
        )

    if warnings:
        st.markdown("#### Warnings")
        for w in warnings:
            st.warning(w)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Ticket completeness")
        comp = tickets.get("completeness")
        if isinstance(comp, pd.DataFrame) and not comp.empty:
            st.dataframe(comp, use_container_width=True, hide_index=True)
        else:
            st.info("No completeness metrics (empty ticket set).")

        st.markdown("#### Status profile")
        status_df = tickets.get("status_profile")
        if isinstance(status_df, pd.DataFrame) and not status_df.empty:
            st.dataframe(status_df, use_container_width=True, hide_index=True)
        else:
            st.caption("No status profile.")

    with c2:
        st.markdown("#### Department profile")
        dept_df = tickets.get("department_profile")
        if isinstance(dept_df, pd.DataFrame) and not dept_df.empty:
            st.dataframe(dept_df, use_container_width=True, hide_index=True)
        else:
            st.caption("No department profile.")

        st.markdown("#### NAS server profile")
        server_df = nas.get("server_profile")
        if isinstance(server_df, pd.DataFrame) and not server_df.empty:
            st.dataframe(server_df, use_container_width=True, hide_index=True)
        else:
            st.caption("No NAS server profile.")

    st.caption(
        "Use this view to flag lifecycle, department, timestamp, and NAS freshness issues "
        "before operational cutover."
    )
