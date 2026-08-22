"""Ticket Operations (V2 Phase 2) — validation + write guard."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

import pandas as pd
import streamlit as st

from config.settings import OFFICIAL_LOCATIONS, STATUS_OPTIONS, TECH_MAP, V2_WRITE_ENABLED
from services.tickets import (
    auto_categorize,
    format_ticket_number,
    prepare_ticket_view,
    save_ticket,
    update_ticket,
)
from ui.components import render_status_table
from ui.navigation import page_breadcrumb


def _write_banner() -> None:
    if V2_WRITE_ENABLED:
        st.error(
            "**LIVE WRITE MODE** — Ticket create/update will write to the configured database."
        )
    else:
        st.warning(
            "**Safe mode** — Create / update / delete are disabled (`V2_WRITE_ENABLED = False`). "
            "Forms are available for review only."
        )


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
    _write_banner()

    left, right = st.columns([1.05, 1.2], gap="large")

    with left:
        st.markdown("### Log new ticket")
        with st.form("v2_new_ticket_form", clear_on_submit=True):
            a1, a2 = st.columns(2)
            user_name = a1.text_input("User name *")
            tech_keys = list(TECH_MAP.keys()) if TECH_MAP else ["Satish", "Priyanshu", "Amit"]
            attended_by = a2.selectbox("Technician *", tech_keys)
            b1, b2 = st.columns(2)
            department = b1.text_input("Department *")
            status = b2.selectbox(
                "Initial status",
                STATUS_OPTIONS if STATUS_OPTIONS else ["Open", "In Progress", "Resolved"],
            )
            locations = OFFICIAL_LOCATIONS or ["Sector - 136 Vega", "Knitpro 28-29"]
            location = st.selectbox("Location *", locations)
            ticket_date = st.date_input("Ticket date", value=datetime.now().date())
            c1, c2 = st.columns(2)
            start_t = c1.time_input("Start time", value=datetime.now().time().replace(second=0, microsecond=0))
            close_t = c2.time_input("Close time (if Resolved)", value=None)
            complaint = st.text_area("Complaint description *", height=100)
            suggested = auto_categorize(complaint) if complaint and complaint.strip() else "Other"
            st.caption(f"Suggested category: **{suggested}**")
            remarks = st.text_area("Technician remarks", height=80)
            submitted = st.form_submit_button(
                "Submit ticket" if V2_WRITE_ENABLED else "Submit ticket (disabled)",
                use_container_width=True,
                disabled=not V2_WRITE_ENABLED,
            )
            if submitted and V2_WRITE_ENABLED:
                errors = []
                if not (user_name or "").strip():
                    errors.append("User name is required.")
                if not (department or "").strip():
                    errors.append("Department is required.")
                if not (complaint or "").strip():
                    errors.append("Complaint is required.")
                if status == "Resolved" and close_t is None:
                    errors.append("Close time is required when status is Resolved.")
                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    date_str = ticket_date.strftime("%Y-%m-%d")
                    start_val = f"{date_str} {start_t.strftime('%H:%M:%S')}"
                    close_val = None
                    duration_mins = 0
                    if status == "Resolved" and close_t is not None:
                        close_val = f"{date_str} {close_t.strftime('%H:%M:%S')}"
                        try:
                            duration_mins = max(
                                1,
                                int(
                                    (
                                        datetime.combine(ticket_date, close_t)
                                        - datetime.combine(ticket_date, start_t)
                                    ).total_seconds()
                                    / 60
                                ),
                            )
                        except Exception:
                            duration_mins = 1
                    row = {
                        "date": date_str,
                        "user_name": user_name.strip(),
                        "department": department.strip(),
                        "complaint": complaint.strip(),
                        "location": location,
                        "attended_by": attended_by,
                        "status": status,
                        "category": suggested,
                        "remarks": (remarks or "").strip(),
                        "start_time": start_val,
                        "close_time": close_val,
                        "resolution_time": duration_mins,
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
            render_status_table(
                view.sort_values("id", ascending=False).head(20), cols, compact=True
            )

            st.markdown("### Update ticket")
            options = {
                f"{r.get('System Ticket ID', r.get('id'))} | {r.get('user_name')} | {r.get('status')}": int(
                    r["id"]
                )
                for _, r in view.iterrows()
                if pd.notna(r.get("id"))
            }
            if options:
                label = st.selectbox("Select ticket", list(options.keys()))
                tid = options[label]
                row = view[view["id"] == tid].iloc[0]
                statuses = STATUS_OPTIONS or [
                    "Open",
                    "In Progress",
                    "On Hold - User Busy",
                    "Resolved",
                ]
                idx = statuses.index(row["status"]) if row["status"] in statuses else 0
                new_status = st.selectbox("New status", statuses, index=idx)
                new_remarks = st.text_area("Remarks", value=str(row.get("remarks", "") or ""))
                if st.button(
                    "Save changes" if V2_WRITE_ENABLED else "Save changes (disabled)",
                    disabled=not V2_WRITE_ENABLED,
                ):
                    if not V2_WRITE_ENABLED:
                        st.warning("Writes disabled.")
                    else:
                        try:
                            payload = {
                                "status": new_status,
                                "remarks": new_remarks.strip(),
                            }
                            if new_status == "Resolved" and not row.get("close_time"):
                                payload["close_time"] = datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                            update_ticket(tid, payload)
                            st.success("Ticket updated.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Update failed: {e}")
