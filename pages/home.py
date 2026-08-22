"""Home / welcome page (V2 Phase 4)."""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd
import streamlit as st

from services.reports import build_ticket_exec_metrics
from services.tickets import prepare_ticket_view
from ui.components import render_info_feed, render_kpi_card
from ui.navigation import page_breadcrumb


def render_home_page(
    user: Optional[dict] = None,
    ticket_df: Optional[pd.DataFrame] = None,
    nas_df: Optional[pd.DataFrame] = None,
    conn: Any = None,
    **kwargs: Any,
) -> None:
    user = user or {"display_name": "Guest", "role": "User"}
    ticket_df = ticket_df if ticket_df is not None else pd.DataFrame()
    nas_df = nas_df if nas_df is not None else pd.DataFrame()

    today = pd.Timestamp.now()
    st.markdown(
        f'<div class="sticky-topbar"><div class="crumb">{page_breadcrumb("Home")}</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""<div class="app-hero" style="padding:18px;border-radius:16px;border:1px solid rgba(96,165,250,.24);
        background:linear-gradient(135deg,rgba(59,130,246,.18),rgba(15,23,42,.96));margin-bottom:16px;">
        <div class="eyebrow" style="color:#94a3b8;font-size:12px;text-transform:uppercase;">Welcome</div>
        <div class="hero-title" style="font-size:28px;font-weight:800;color:white;">
        Welcome {user.get("display_name", "User")}</div>
        <div class="hero-sub" style="color:#94a3b8;">
        Today: {today.strftime("%d %b %Y")} · Role: {user.get("role", "User")}
        </div></div>""",
        unsafe_allow_html=True,
    )

    metrics = build_ticket_exec_metrics(ticket_df)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Pending", metrics.get("pending", 0), "Open backlog", "🎫", tone="warning")
    with k2:
        render_kpi_card("Closed today", metrics.get("today_closed", 0), "Resolved today", "✅", tone="success")
    with k3:
        render_kpi_card("Resolution %", metrics.get("resolution_rate", 0), "Close rate", "🎯")
    with k4:
        render_kpi_card("NAS logs", len(nas_df), "Backup entries", "🖥")

    st.markdown("#### Quick actions")
    qa = st.columns(4)
    targets = [
        ("Ticket Operations", "Ticket Operations"),
        ("NAS Monitoring", "NAS Monitoring"),
        ("Reports", "Reports"),
        ("Home", "Home"),
    ]
    for col, (label, page) in zip(qa, targets):
        with col:
            if st.button(label, key=f"home_nav_{page}", use_container_width=True):
                st.session_state["v2_page"] = page
                st.rerun()

    recent = prepare_ticket_view(ticket_df)
    if not recent.empty:
        recent = recent.sort_values("id", ascending=False).head(6)
    left, right = st.columns(2)
    with left:
        render_info_feed(
            "Recent tickets",
            recent if not recent.empty else None,
            ["complaint", "status", "location", "date"],
        )
    with right:
        render_info_feed(
            "Recent NAS activity",
            nas_df.sort_values("id", ascending=False).head(6) if not nas_df.empty else None,
            ["server_name", "status", "storage_used", "date"],
        )
