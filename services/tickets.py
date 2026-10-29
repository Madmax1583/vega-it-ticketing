"""
Ticket domain service (V2 Phase 2).

Extracted from script.py — load/save/normalize/categorize/SLA helpers.
Uses Supabase when configured; otherwise session_state local fallback.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

import pandas as pd
import streamlit as st

from db.supabase_client import get_supabase_client, is_db_connected, table_exists

TICKET_COLUMNS = [
    "id",
    "date",
    "user_name",
    "department",
    "complaint",
    "location",
    "attended_by",
    "status",
    "category",
    "start_time",
    "close_time",
    "resolution_time",
    "remarks",
]


def _ensure_local_tickets() -> None:
    if "local_tickets" not in st.session_state:
        st.session_state.local_tickets = pd.DataFrame(
            [
                {
                    "id": 1,
                    "date": "2026-07-01",
                    "user_name": "Amit Sharma",
                    "department": "Production",
                    "complaint": "CCTV camera in main corridor is flickering",
                    "location": "Sector - 136 Vega",
                    "attended_by": "Satish",
                    "status": "In Progress",
                    "category": "CCTV/Camera",
                    "start_time": "2026-07-01 10:15:00",
                    "close_time": None,
                    "resolution_time": 0,
                    "remarks": "POE check in progress",
                },
                {
                    "id": 2,
                    "date": "2026-07-03",
                    "user_name": "Sunita Rao",
                    "department": "Finance",
                    "complaint": "Desktop showing blue screen after update",
                    "location": "Knitpro 28-29",
                    "attended_by": "Priyanshu",
                    "status": "Open",
                    "category": "Laptop/Hardware",
                    "start_time": None,
                    "close_time": None,
                    "resolution_time": 0,
                    "remarks": "",
                },
                {
                    "id": 3,
                    "date": "2026-07-05",
                    "user_name": "Rajesh Kumar",
                    "department": "HR",
                    "complaint": "Office printer offline and queue is stuck",
                    "location": "Sector - 155 Vega",
                    "attended_by": "Amit",
                    "status": "Resolved",
                    "category": "Printer",
                    "start_time": "2026-07-05 10:00:00",
                    "close_time": "2026-07-05 10:35:00",
                    "resolution_time": 35,
                    "remarks": "Spooler restarted and queue flushed",
                },
            ]
        )


def format_ticket_number(ticket_id: Any, location_str: Any) -> str:
    try:
        clean_id = int(float(ticket_id))
        loc = str(location_str).lower() if pd.notna(location_str) else ""
        if "vega" in loc or "136" in loc or "155" in loc:
            prefix = "VEGA"
        elif "knitpro" in loc or "jaipur" in loc:
            prefix = "KP"
        else:
            prefix = "IT"
        return f"{prefix}-2026-{clean_id:04d}"
    except Exception:
        return f"IT-2026-{ticket_id}"


def normalize_category(value: Any) -> str:
    s = str(value).strip().lower().replace("&", "/")
    mapping = {
        "cctv/camera": "CCTVCamera",
        "cctv camera": "CCTVCamera",
        "camera": "CCTVCamera",
        "cctvcamera": "CCTVCamera",
        "laptop/hardware": "LaptopHardware",
        "laptop hardware": "LaptopHardware",
        "laptophardware": "LaptopHardware",
        "desktop": "LaptopHardware",
        "email/outlook": "EmailOutlook",
        "email outlook": "EmailOutlook",
        "emailoutlook": "EmailOutlook",
        "printer": "Printer",
        "sap": "SAP",
        "network": "Network",
        "server/ups": "ServerUPS",
        "server ups": "ServerUPS",
        "serverups": "ServerUPS",
        "other": "Other",
    }
    if s in mapping:
        return mapping[s]
    if pd.notna(value) and str(value).strip():
        return str(value).strip()
    return "Other"


def auto_categorize(complaint: Any) -> str:
    text = str(complaint).lower()
    if any(k in text for k in ["cctv", "camera", "nvr"]):
        return "CCTVCamera"
    if any(k in text for k in ["laptop", "desktop", "keyboard", "touchpad", "battery", "screen", "hardware", "monitor"]):
        return "LaptopHardware"
    if any(k in text for k in ["outlook", "email", "mail", "pst", "ost"]):
        return "EmailOutlook"
    if any(k in text for k in ["printer", "scanner", "cartridge", "print"]):
        return "Printer"
    if any(k in text for k in ["sap", "erp"]):
        return "SAP"
    if any(k in text for k in ["network", "wifi", "internet", "vpn", "ping", "ip", "router", "switch", "lan"]):
        return "Network"
    if any(k in text for k in ["server", "ups", "rack", "dns", "domain", "backup"]):
        return "ServerUPS"
    return "Other"


def normalize_ticket_df(df: Optional[pd.DataFrame]) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=TICKET_COLUMNS)
    out = df.copy()
    for col in TICKET_COLUMNS:
        if col not in out.columns:
            out[col] = None
    out["id"] = pd.to_numeric(out["id"], errors="coerce").fillna(0).astype(int)
    out["resolution_time"] = pd.to_numeric(out["resolution_time"], errors="coerce").fillna(0).astype(int)
    out["remarks"] = out["remarks"].fillna("").astype(str)
    out["status"] = out["status"].fillna("").astype(str)
    out["category"] = out["category"].fillna("").astype(str).map(normalize_category)
    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    return out[TICKET_COLUMNS]


def get_next_ticket_id(df: pd.DataFrame) -> int:
    if df.empty or "id" not in df.columns:
        return 1
    return int(pd.to_numeric(df["id"], errors="coerce").fillna(0).max()) + 1


def prepare_ticket_view(df: pd.DataFrame) -> pd.DataFrame:
    view = df.copy()
    if not view.empty:
        view["System Ticket ID"] = view.apply(
            lambda r: format_ticket_number(r["id"], r["location"]), axis=1
        )
        view["date_parsed"] = pd.to_datetime(view["date"], errors="coerce")
    return view


def filtered_tickets(
    df: pd.DataFrame,
    site_filter: str = "All",
    status_filter: str = "All",
    tech_filter: str = "All",
) -> pd.DataFrame:
    out = df.copy()
    if out.empty:
        return out
    if site_filter != "All":
        out = out[out["location"] == site_filter]
    if status_filter != "All":
        out = out[out["status"] == status_filter]
    if tech_filter != "All":
        out = out[out["attended_by"] == tech_filter]
    return out


def load_tickets() -> pd.DataFrame:
    if is_db_connected():
        client = get_supabase_client()
        try:
            response = client.table("tickets").select("*").execute()
            return normalize_ticket_df(pd.DataFrame(response.data) if response.data else pd.DataFrame())
        except Exception:
            pass
    _ensure_local_tickets()
    return normalize_ticket_df(st.session_state.local_tickets)


def save_ticket(new_row: dict) -> Optional[int]:
    row = dict(new_row)
    if "category" in row:
        row["category"] = normalize_category(row["category"])

    if is_db_connected():
        client = get_supabase_client()
        response = client.table("tickets").insert(row).execute()
        if response.data and "id" in response.data[0]:
            return int(response.data[0]["id"])
        return None

    _ensure_local_tickets()
    current = st.session_state.local_tickets.copy()
    row["id"] = get_next_ticket_id(current)
    st.session_state.local_tickets = pd.concat([current, pd.DataFrame([row])], ignore_index=True)
    return int(row["id"])


def update_ticket(ticket_id: int, payload: dict) -> None:
    clean = dict(payload)
    if "category" in clean:
        clean["category"] = normalize_category(clean["category"])

    if is_db_connected():
        client = get_supabase_client()
        client.table("tickets").update(clean).eq("id", int(ticket_id)).execute()
        return

    _ensure_local_tickets()
    idx = st.session_state.local_tickets[st.session_state.local_tickets["id"] == int(ticket_id)].index
    for key, value in clean.items():
        st.session_state.local_tickets.loc[idx, key] = value


def delete_ticket(ticket_id: int) -> None:
    if is_db_connected():
        client = get_supabase_client()
        client.table("tickets").delete().eq("id", int(ticket_id)).execute()
        return

    _ensure_local_tickets()
    st.session_state.local_tickets = st.session_state.local_tickets[
        st.session_state.local_tickets["id"] != int(ticket_id)
    ].reset_index(drop=True)


def add_priority_and_sla(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if out.empty:
        return out

    if "priority" not in out.columns:

        def infer_priority(x: Any) -> str:
            t = str(x).lower()
            if any(k in t for k in ["server", "sap", "network down", "critical", "vpn down", "firewall", "switch"]):
                return "Critical"
            if any(k in t for k in ["printer", "email", "outlook", "cctv", "camera", "access", "attendance"]):
                return "High"
            return "Medium"

        out["priority"] = out.get("complaint", "").apply(infer_priority)

    out["date_parsed"] = pd.to_datetime(out.get("date"), errors="coerce")
    out["start_time_parsed"] = (
        pd.to_datetime(out.get("start_time"), errors="coerce") if "start_time" in out.columns else pd.NaT
    )
    out["close_time_parsed"] = (
        pd.to_datetime(out.get("close_time"), errors="coerce") if "close_time" in out.columns else pd.NaT
    )
    out["resolution_time"] = pd.to_numeric(out.get("resolution_time"), errors="coerce")
    now = pd.Timestamp.now()
    open_mask = out.get("status", pd.Series(dtype=str)).astype(str).isin(
        ["Open", "In Progress", "On Hold - User Busy", "On Hold"]
    )

    created_ts = out["date_parsed"]
    response_anchor = out["start_time_parsed"]
    close_anchor = out["close_time_parsed"]

    age_start = response_anchor.combine_first(created_ts)
    age_hours = ((now - age_start).dt.total_seconds() / 3600).where(open_mask)
    out["age_hours"] = age_hours.fillna(0).round(1)

    resolved_duration = (close_anchor - response_anchor).dt.total_seconds() / 60
    fallback_resolution = pd.to_numeric(out["resolution_time"], errors="coerce")
    out["actual_resolution_min"] = resolved_duration.where(resolved_duration > 0).fillna(fallback_resolution)

    frt_duration = (response_anchor - created_ts).dt.total_seconds() / 60
    out["frt_min"] = frt_duration.where(frt_duration >= 0)

    sla_hours = out["priority"].map({"Critical": 2, "High": 4, "Medium": 8, "Low": 12}).fillna(8)
    out["sla_hours"] = sla_hours
    resolution_clock_hours = (close_anchor.fillna(now) - created_ts).dt.total_seconds() / 3600
    out["sla_breach"] = resolution_clock_hours > out["sla_hours"]
    out["sla_badge"] = out["sla_breach"].map({True: "BREACH", False: "OK"})
    out["response_available"] = out["frt_min"].notna()
    out["resolution_available"] = out["actual_resolution_min"].notna() & (out["actual_resolution_min"] > 0)
    return out
