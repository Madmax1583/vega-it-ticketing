"""Read-only ticket and NAS data-quality analytics."""

from __future__ import annotations

from typing import Any, Dict

import pandas as pd


def _empty_ticket_summary() -> Dict[str, Any]:
    return {
        "total_tickets": 0,
        "resolved_tickets": 0,
        "active_tickets": 0,
        "missing_start_time": 0,
        "resolved_missing_close_time": 0,
        "missing_or_zero_resolution_time": 0,
        "missing_department": 0,
        "raw_department_values": 0,
        "metric_confidence": "Low",
        "confidence_note": "No ticket records are available.",
    }


def _series(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        return pd.Series(pd.NA, index=df.index, dtype="object")
    return df[column]


def _blank_mask(series: pd.Series) -> pd.Series:
    return series.isna() | series.astype(str).str.strip().eq("")


def build_metric_confidence_summary(summary: Dict[str, Any]) -> Dict[str, str]:
    """Classify ticket metric confidence from completeness indicators."""
    total = int(summary.get("total_tickets", 0) or 0)
    if total == 0:
        return {"metric_confidence": "Low", "confidence_note": "No ticket records are available."}

    issues = (
        int(summary.get("missing_start_time", 0) or 0)
        + int(summary.get("resolved_missing_close_time", 0) or 0)
        + int(summary.get("missing_or_zero_resolution_time", 0) or 0)
    )
    if issues / total >= 0.25:
        return {
            "metric_confidence": "Moderate",
            "confidence_note": "Demand trends are usable; MTTR, SLA, backlog, and closure-duration metrics are provisional.",
        }
    if issues:
        return {
            "metric_confidence": "High",
            "confidence_note": "Minor timestamp gaps remain; validate exceptions before executive reporting.",
        }
    return {
        "metric_confidence": "High",
        "confidence_note": "Ticket lifecycle fields are complete for the selected data.",
    }


def build_ticket_data_quality_summary(df: pd.DataFrame | None) -> Dict[str, Any]:
    """Return read-only completeness metrics for ticket reporting."""
    if df is None or df.empty:
        return _empty_ticket_summary()

    tickets = df.copy()
    status = _series(tickets, "status").fillna("").astype(str).str.strip()
    resolved = status.eq("Resolved")
    active = status.isin([
        "Open", "Assigned", "In Progress", "Waiting for User",
        "Waiting for Vendor", "On Hold", "On Hold - User Busy", "Reopened",
    ])
    resolution = pd.to_numeric(_series(tickets, "resolution_time"), errors="coerce")
    department = _series(tickets, "department")

    summary = {
        "total_tickets": int(len(tickets)),
        "resolved_tickets": int(resolved.sum()),
        "active_tickets": int(active.sum()),
        "missing_start_time": int(_blank_mask(_series(tickets, "start_time")).sum()),
        "resolved_missing_close_time": int((resolved & _blank_mask(_series(tickets, "close_time"))).sum()),
        "missing_or_zero_resolution_time": int((resolution.isna() | resolution.le(0)).sum()),
        "missing_department": int(_blank_mask(department).sum()),
        "raw_department_values": int(department.dropna().astype(str).str.strip().replace("", pd.NA).dropna().nunique()),
    }
    return {**summary, **build_metric_confidence_summary(summary)}


def build_nas_data_quality_summary(df: pd.DataFrame | None, stale_after_days: int = 2) -> Dict[str, Any]:
    """Return read-only NAS logging coverage and freshness metrics."""
    if df is None or df.empty:
        return {
            "total_nas_logs": 0,
            "servers": 0,
            "failed_logs": 0,
            "missing_storage": 0,
            "latest_log_date": None,
            "stale_servers": 0,
            "metric_confidence": "Low",
            "confidence_note": "No NAS records are available.",
        }

    logs = df.copy()
    dates = pd.to_datetime(_series(logs, "date"), errors="coerce")
    latest_date = dates.max()
    status = _series(logs, "status").fillna("").astype(str).str.strip().str.lower()
    storage = pd.to_numeric(_series(logs, "storage_used"), errors="coerce")
    servers = _series(logs, "server_name").fillna("").astype(str).str.strip()

    stale_servers = 0
    if "server_name" in logs.columns and not pd.isna(latest_date):
        latest_by_server = pd.DataFrame({"server": servers, "date": dates}).groupby("server")["date"].max()
        cutoff = pd.Timestamp.now().normalize() - pd.Timedelta(days=stale_after_days)
        stale_servers = int((latest_by_server < cutoff).sum())

    summary = {
        "total_nas_logs": int(len(logs)),
        "servers": int(servers.replace("", pd.NA).dropna().nunique()),
        "failed_logs": int(status.isin(["failed", "fail", "error", "warning"]).sum()),
        "missing_storage": int(storage.isna().sum()),
        "latest_log_date": None if pd.isna(latest_date) else latest_date.strftime("%Y-%m-%d"),
        "stale_servers": stale_servers,
    }
    note = "NAS completeness is suitable for logging coverage analysis."
    if stale_servers:
        note = f"{stale_servers} server(s) have stale backup-log activity."
    return {**summary, "metric_confidence": "High" if not summary["missing_storage"] else "Moderate", "confidence_note": note}


def build_data_quality_payload(tickets_df: pd.DataFrame | None, nas_df: pd.DataFrame | None) -> Dict[str, Dict[str, Any]]:
    """Return the combined payload for a future Streamlit Data Quality page."""
    return {
        "tickets": build_ticket_data_quality_summary(tickets_df),
        "nas": build_nas_data_quality_summary(nas_df),
    }
