"""Reusable UI components (V2 Phase 3)."""

from __future__ import annotations

from typing import Iterable, Optional

import pandas as pd
import streamlit as st


def status_badge_html(status: object) -> str:
    s = str(status).strip().lower()
    if s == "resolved":
        return '<span class="status-chip status-resolved">Resolved</span>'
    if s == "in progress":
        return '<span class="status-chip status-progress">In Progress</span>'
    if s in {"on hold - user busy", "on hold"}:
        return '<span class="status-chip status-hold">On Hold</span>'
    return '<span class="status-chip status-open">Open</span>'


def render_nas_status(status: object) -> str:
    if str(status).strip() == "Success":
        return '<span class="status-chip status-resolved">Success</span>'
    return '<span class="status-chip status-open">Failed</span>'


def render_status_table(
    df: pd.DataFrame,
    columns: Iterable[str],
    compact: bool = False,
    nas_mode: bool = False,
) -> None:
    if df is None or df.empty:
        st.info("No records found.")
        return
    show_df = df.copy()
    if "status" in show_df.columns:
        show_df["status"] = show_df["status"].apply(
            render_nas_status if nas_mode else status_badge_html
        )
    safe_columns = [c for c in columns if c in show_df.columns]
    if not safe_columns:
        st.warning("No matching columns to display.")
        return
    styled = show_df[safe_columns].to_html(escape=False, index=False)
    css_class = "table-scroll compact-table" if compact else "table-scroll"
    st.markdown(f'<div class="{css_class}">{styled}</div>', unsafe_allow_html=True)


def render_kpi_card(
    title: str,
    value: object,
    subtitle: str = "",
    icon: str = "📊",
    trend: Optional[str] = None,
    tone: str = "primary",
) -> None:
    trend_cls = (
        "trend-up"
        if tone == "success"
        else ("trend-warn" if tone == "warning" else ("trend-down" if tone == "danger" else ""))
    )
    trend_html = f'<div class="kpi-sub {trend_cls}">{trend}</div>' if trend else ""
    st.markdown(
        f"""<div class="kpi-card">
        <div class="kpi-top">
            <div>
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{value}</div>
            </div>
            <div class="kpi-icon">{icon}</div>
        </div>
        <div class="kpi-sub">{subtitle}</div>
        {trend_html}
        </div>""",
        unsafe_allow_html=True,
    )


def render_info_feed(title: str, rows: Optional[pd.DataFrame], fields: list) -> None:
    st.markdown(
        f'<div class="panel"><div class="panel-title">{title}</div>',
        unsafe_allow_html=True,
    )
    if rows is None or len(rows) == 0:
        st.info("No recent activity available.")
    else:
        for _, row in rows.iterrows():
            primary = " · ".join(
                [str(row.get(f, "")) for f in fields[:2] if str(row.get(f, "")) not in ["", "nan"]]
            )
            meta = " · ".join(
                [str(row.get(f, "")) for f in fields[2:] if str(row.get(f, "")) not in ["", "nan"]]
            )
            st.markdown(
                f'<div class="feed-item"><div class="feed-title">{primary}</div>'
                f'<div class="feed-meta">{meta}</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)
