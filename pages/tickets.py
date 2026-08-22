"""Ticket Operations page (V2 Phase 4)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

import pandas as pd
import streamlit as st

from config.settings import OFFICIAL_LOCATIONS, STATUS_OPTIONS, TECH_MAP
from services.tickets import (
    auto_categorize,
    format_ticket_number,
    prepare_ticket_view,
    save_ticket,
    update_ticket,
)
from ui.components import render_status_table
from ui.navigation import page_breadcrumb


def render_tickets_page(
    user: Optional[dict] = None,
    ticket_df: Optional[pd.DataFrame] = None,
    nas_df: Optional[pd.DataFrame] = None,
    conn: Any = None,
    **kwargs: Any,
) -> None:
    ticket_df = ticket_df if ticket_df is not None else pd.DataFrame()
    view = prepare_ticket_view(ticket_df)

    st.markdown(
        f'<div class="sticky-topbar"><div class="crumb">{page_breadcrumb("Ticket Operations")}</div></div>',
        unsafe_allow_html=True,
    )
    st.subheader("Ticket Operations")

    left, right = st.columns([1.05, 1.2], gap="large")

    with left:
        st.markdown("### Log new ticket")
        with st.form("v2_new_ticket_form", clear_on_submit=True):
            a1, a2 = st.columns(2)
            user_name = a1.text_input("User name")
            tech_keys = list(TECH_MAP.keys()) if TECH_MAP else ["Satish", "Priyanshu", "Amit", "Ranjan", "Manish"]
            attended_by = a2.selectbox("Technician", tech_keys)
            b1, b2 = st.columns(2)
            department = b1.text_input("Department")
            status = b2.selectbox("Initial status", STATUS_OPTIONS if STATUS_OPTIONS else ["Open", "In Progress", "Resolved"])
            locations = OFFICIAL_LOCATIONS if OFFICIAL_LOCATIONS else [
                "Sector - 136 Vega",
                "Knitpro 28-29",
                "Sector - 155 Vega",
            ]
            location = st.selectbox("Location", locations)
            ticket_date = st.date_input("Ticket date", value=datetime.now().date())
            complaint = st.text_area("Complaint description", height=100)
            suggested = auto_categorize(complaint) if complaint.strip() else "Other"
            st.caption(f"Suggested category: **{suggested}**")
            remarks = st.text_area("Technician remarks", height=80)
            submitted = st.form_submit_button("Submit ticket", use_container_width=True)
            if submitted:
                if not user_name.strip() or not department.strip() or not complaint.strip():
                    st.error("Please fill user name, department, and complaint.")
                else:
                    date_str = ticket_date.strftime("%Y-%m-%d")
                    row = {
                        "date": date_str,
                        "user_name": user_name.strip(),
                        "department": department.strip(),
                        "complaint": complaint.strip(),
                        "location": location,
                        "attended_by": attended_by,
                        "status": status,
                        "category": suggested,
                        "remarks": remarks.strip(),
                        "start_time": None,
                        "close_time": None,
                        "resolution_time": 0,
                    }
                    try:
                        new_id = save_ticket(row)
                        st.success(f"Ticket saved: {format_ticket_number(new_id, location)}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Save failed: {e}")

    with right:
        st.markdown("### Active queue")
        if view.empty:
            st.info("No tickets loaded.")
        else:
            cols = [
                c
                for c in [
                    "System Ticket ID",
                    "date",
                    "user_name",
                    "department",
                    "location",
                    "category",
                    "attended_by",
                    "status",
                ]
                if c in view.columns
            ]
            render_status_table(view.sort_values("id", ascending=False).head(15), cols, compact=True)

            st.markdown("### Update ticket")
            options = {
                f"{r['System Ticket ID']} | {r['user_name']} | {r['status']}": int(r["id"])
                for _, r in view.iterrows()
            }
            if options:
                label = st.selectbox("Select ticket", list(options.keys()))
                tid = options[label]
                row = view[view["id"] == tid].iloc[0]
                statuses = STATUS_OPTIONS if STATUS_OPTIONS else ["Open", "In Progress", "On Hold - User Busy", "Resolved"]
                idx = statuses.index(row["status"]) if row["status"] in statuses else 0
                new_status = st.selectbox("New status", statuses, index=idx)
                new_remarks = st.text_area("Remarks", value=str(row.get("remarks", "")))
                if st.button("Save changes"):
                    try:
                        payload = {"status": new_status, "remarks": new_remarks.strip()}
                        if new_status == "Resolved" and not row.get("close_time"):
                            payload["close_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        update_ticket(tid, payload)
                        st.success("Ticket updated.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Update failed: {e}")
