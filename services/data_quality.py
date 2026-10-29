"""Read-only data-quality profiling for V2 ticket and NAS analytics."""

from __future__ import annotations

from typing import Any

import pandas as pd


RESOLVED_STATUSES = {"resolved", "closed", "completed"}
FAILURE_TERMS = ("fail", "error", "unsuccess", "partial")


def _frame(df: pd.DataFrame | None) -> pd.DataFrame:
    return df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame()


def _text(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()


def _count_missing(df: pd.DataFrame, column: str) -> int:
    if column not in df.columns:
        return len(df)
    return int(_text(df[column]).eq("").sum())


def _confidence(total: int, usable: int) -> str:
    if total == 0 or usable == 0:
        return "unavailable"
    ratio = usable / total
    if ratio >= 0.95:
        return "high"
    if ratio >= 0.70:
        return "medium"
    return "low"


def profile_tickets(tickets_df: pd.DataFrame | None) -> dict[str, Any]:
    """Return non-mutating ticket completeness and normalization diagnostics."""
    df = _frame(tickets_df)
    total = len(df)
    if total == 0:
        return {
            "summary": {
                "ticket_count": 0,
                "date_min": None,
                "date_max": None,
                "status_count": 0,
                "category_count": 0,
                "department_count": 0,
            },
            "completeness": pd.DataFrame(
                columns=["metric", "missing_count", "missing_pct", "confidence"]
            ),
            "department_profile": pd.DataFrame(columns=["department", "tickets"]),
            "status_profile": pd.DataFrame(columns=["status", "tickets"]),
            "warnings": ["No ticket data available."],
        }

    date_values = pd.to_datetime(
        df["date"] if "date" in df.columns else pd.Series(index=df.index, dtype=object),
        errors="coerce",
    )
    status_values = _text(df["status"]) if "status" in df.columns else pd.Series("", index=df.index)
    resolved_mask = status_values.str.lower().isin(RESOLVED_STATUSES)
    resolution = pd.to_numeric(
        df["resolution_time"] if "resolution_time" in df.columns else pd.Series(index=df.index),
        errors="coerce",
    )
    resolved_missing_close = (
        int((_text(df["close_time"]).eq("") & resolved_mask).sum())
        if "close_time" in df.columns
        else int(resolved_mask.sum())
    )
    zero_resolution = int((resolution.fillna(0) <= 0).sum())
    checks = [
        ("Missing ticket date", int(date_values.isna().sum())),
        ("Missing start time", _count_missing(df, "start_time")),
        ("Resolved tickets missing close time", resolved_missing_close),
        ("Zero or missing resolution duration", zero_resolution),
        ("Missing department", _count_missing(df, "department")),
        ("Missing category", _count_missing(df, "category")),
        ("Missing technician", _count_missing(df, "attended_by")),
    ]
    completeness = pd.DataFrame(
        [
            {
                "metric": metric,
                "missing_count": missing,
                "missing_pct": round((missing / total) * 100, 1),
                "confidence": _confidence(total, total - missing),
            }
            for metric, missing in checks
        ]
    )
    department = _text(df["department"]) if "department" in df.columns else pd.Series("", index=df.index)
    departments = (
        department.replace("", "(blank)")
        .value_counts()
        .rename_axis("department")
        .reset_index(name="tickets")
    )
    statuses = (
        status_values.replace("", "(blank)")
        .value_counts()
        .rename_axis("status")
        .reset_index(name="tickets")
    )
    warnings: list[str] = []
    if statuses.shape[0] == 1:
        warnings.append("Only one ticket status is present; lifecycle metrics may be misleading.")
    if departments.shape[0] > 25:
        warnings.append("Department values are highly fragmented; apply a mapping before executive reporting.")
    if int(date_values.isna().sum()) > 0:
        warnings.append("Some ticket dates are invalid or missing.")
    if resolved_missing_close > 0:
        warnings.append("Some resolved tickets have no close time.")
    return {
        "summary": {
            "ticket_count": total,
            "date_min": date_values.min().date().isoformat() if date_values.notna().any() else None,
            "date_max": date_values.max().date().isoformat() if date_values.notna().any() else None,
            "status_count": int(statuses.shape[0]),
            "category_count": int(_text(df["category"]).replace("", "(blank)").nunique()) if "category" in df.columns else 0,
            "department_count": int(departments.shape[0]),
        },
        "completeness": completeness,
        "department_profile": departments,
        "status_profile": statuses,
        "warnings": warnings,
    }


def profile_nas(nas_df: pd.DataFrame | None, freshness_days: int = 7) -> dict[str, Any]:
    """Return non-mutating NAS completeness, status, and freshness diagnostics."""
    df = _frame(nas_df)
    total = len(df)
    if total == 0:
        return {
            "summary": {
                "nas_log_count": 0,
                "server_count": 0,
                "failure_count": 0,
                "missing_storage_count": 0,
                "latest_log_date": None,
                "freshness": "unavailable",
            },
            "server_profile": pd.DataFrame(columns=["server_name", "logs", "failures", "latest_date"]),
            "warnings": ["No NAS data available."],
        }

    dates = pd.to_datetime(
        df["date"] if "date" in df.columns else pd.Series(index=df.index, dtype=object),
        errors="coerce",
    )
    status = _text(df["status"]) if "status" in df.columns else pd.Series("", index=df.index)
    failed = status.str.lower().apply(lambda value: any(term in value for term in FAILURE_TERMS))
    storage = pd.to_numeric(
        df["storage_used"] if "storage_used" in df.columns else pd.Series(index=df.index),
        errors="coerce",
    )
    servers = _text(df["server_name"]) if "server_name" in df.columns else pd.Series("", index=df.index)
    profile_source = pd.DataFrame({"server_name": servers.replace("", "(blank)"), "date": dates, "failed": failed})
    server_profile = profile_source.groupby("server_name", as_index=False).agg(
        logs=("server_name", "size"),
        failures=("failed", "sum"),
        latest_date=("date", "max"),
    )
    latest = dates.max() if dates.notna().any() else pd.NaT
    if pd.isna(latest):
        freshness = "unavailable"
    else:
        age_days = (pd.Timestamp.now().normalize() - latest.normalize()).days
        freshness = "fresh" if age_days <= freshness_days else "stale"
    warnings: list[str] = []
    if int(failed.sum()) > 0:
        warnings.append("NAS failure-like statuses require review.")
    if int(storage.isna().sum()) > 0:
        warnings.append("Some NAS logs have missing or invalid storage readings.")
    if freshness == "stale":
        warnings.append("Latest NAS log is older than the freshness threshold.")
    return {
        "summary": {
            "nas_log_count": total,
            "server_count": int(servers.replace("", "(blank)").nunique()),
            "failure_count": int(failed.sum()),
            "missing_storage_count": int(storage.isna().sum()),
            "latest_log_date": latest.date().isoformat() if pd.notna(latest) else None,
            "freshness": freshness,
        },
        "server_profile": server_profile.sort_values("server_name").reset_index(drop=True),
        "warnings": warnings,
    }


def build_data_quality_report(
    tickets_df: pd.DataFrame | None, nas_df: pd.DataFrame | None, freshness_days: int = 7
) -> dict[str, Any]:
    """Build a page-ready, read-only V2 data-quality report."""
    tickets = profile_tickets(tickets_df)
    nas = profile_nas(nas_df, freshness_days=freshness_days)
    return {
        "tickets": tickets,
        "nas": nas,
        "warnings": tickets["warnings"] + nas["warnings"],
    }
