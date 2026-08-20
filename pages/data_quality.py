"""Read-only V2 Data Quality page renderer.

This page is intentionally not wired into app.py yet. It can be imported by the
future custom router after page-level smoke testing.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from services.data_quality import build_data_quality_report
from services.nas import load_nas_data
from services.tickets import load_tickets
from ui.components import render_empty_state, render_kpi, render_status_badge, render_warnings


def page_data(
    tickets_df: pd.DataFrame | None, nas_df: pd.DataFrame | None, freshness_days: int = 7
) -> dict[str, Any]:
    """Prepare the page model without Streamlit side effects; useful for testing."""
    return build_data_quality_report(tickets_df, nas_df, freshness_days=freshness_days)


def _table_or_empty(frame: pd.DataFrame, message: str) -> None:
    if frame is None or frame.empty:
        render_empty_state(message)
    else:
        st.dataframe(frame, use_container_width=True, hide_index=True)


def render(
    tickets_df: pd.DataFrame | None = None,
    nas_df: pd.DataFrame | None = None,
    freshness_days: int = 7,
) -> None:
    """Render the read-only Data Quality view.

    Callers may inject dataframes for a controlled page test; otherwise the
    existing V2 ticket and NAS loaders are used.
    """
    tickets = load_tickets() if tickets_df is None else tickets_df
    nas = load_nas_data() if nas_df is None else nas_df
    report = page_data(tickets, nas, freshness_days=freshness_days)
    ticket_summary = report["tickets"]["summary"]
    nas_summary = report["nas"]["summary"]

    st.title("Data Quality")
    st.caption("Read-only diagnostics for ticket and NAS reporting confidence.")
    render_warnings(report["warnings"])

    st.subheader("Coverage")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Tickets", ticket_summary["ticket_count"])
    with c2:
        render_kpi("Departments", ticket_summary["department_count"])
    with c3:
        render_kpi("NAS logs", nas_summary["nas_log_count"])
    with c4:
        render_kpi("NAS servers", nas_summary["server_count"])

    st.subheader("Ticket quality")
    t1, t2, t3 = st.columns(3)
    with t1:
        render_kpi("Ticket date range", f"{ticket_summary['date_min'] or '—'} to {ticket_summary['date_max'] or '—'}")
    with t2:
        render_kpi("Ticket statuses", ticket_summary["status_count"])
    with t3:
        render_kpi("Ticket categories", ticket_summary["category_count"])
    _table_or_empty(report["tickets"]["completeness"], "No ticket quality checks available.")

    left, right = st.columns(2)
    with left:
        st.markdown("#### Raw department profile")
        _table_or_empty(report["tickets"]["department_profile"], "No department values available.")
    with right:
        st.markdown("#### Status profile")
        _table_or_empty(report["tickets"]["status_profile"], "No ticket status values available.")

    st.subheader("NAS quality")
    n1, n2, n3, n4 = st.columns(4)
    with n1:
        render_kpi("Failure-like logs", nas_summary["failure_count"])
    with n2:
        render_kpi("Missing storage", nas_summary["missing_storage_count"])
    with n3:
        render_kpi("Latest NAS log", nas_summary["latest_log_date"])
    with n4:
        render_status_badge(nas_summary["freshness"])
    _table_or_empty(report["nas"]["server_profile"], "No NAS server profile available.")

    with st.expander("Metric guidance"):
        st.markdown(
            "- **High confidence**: at least 95% of records have the required value.\n"
            "- **Medium confidence**: 70% to 94.9% of records have the required value.\n"
            "- **Low confidence**: fewer than 70% of records have the required value.\n"
            "- **Unavailable**: no relevant records or usable values are available."
        )
