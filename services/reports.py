"""
Reporting domain service (V2 Phase 2b).

Ticket/NAS summary builders, MTTR/SLA, aging, scorecards, MoM, Excel export.
Depends on services.tickets (SLA) and services.nas (deltas/forecast).
"""

from __future__ import annotations

import io
from typing import Any, Optional

import pandas as pd

from services.nas import build_nas_reports, build_storage_forecast, compute_nas_changes, normalize_nas_df
from services.tickets import add_priority_and_sla, prepare_ticket_view


def current_period_ticket_df(df: pd.DataFrame, freq: str = "Daily") -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    x = df.copy()
    x["date_parsed"] = pd.to_datetime(x.get("date"), errors="coerce")
    x = x.dropna(subset=["date_parsed"])
    if x.empty:
        return pd.DataFrame()
    today = pd.Timestamp.now().normalize()
    if freq == "Monthly":
        x = x[x["date_parsed"].dt.to_period("M") == today.to_period("M")]
    elif freq == "Weekly":
        iso = today.isocalendar()
        x = x[
            (x["date_parsed"].dt.isocalendar().year == iso.year)
            & (x["date_parsed"].dt.isocalendar().week == iso.week)
        ]
    else:
        start = today - pd.Timedelta(days=29)
        x = x[x["date_parsed"] >= start]
    return x


def build_ticket_exec_metrics(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        return {
            "today_open": 0,
            "today_closed": 0,
            "pending": 0,
            "overdue": 0,
            "avg_resolution": 0,
            "resolution_rate": 0.0,
            "avg_frt": 0.0,
        }
    x = add_priority_and_sla(df)
    today = pd.Timestamp.now().normalize()
    x["date_parsed"] = pd.to_datetime(x.get("date"), errors="coerce")
    x["close_time_parsed"] = (
        pd.to_datetime(x.get("close_time"), errors="coerce") if "close_time" in x.columns else pd.NaT
    )
    pending_mask = x["status"].astype(str).isin(["Open", "In Progress", "On Hold - User Busy", "On Hold"])
    resolved_mask = x["status"].astype(str) == "Resolved"
    today_open_mask = x["date_parsed"].dt.normalize() == today
    today_closed_mask = x["close_time_parsed"].dt.normalize() == today
    overdue_mask = pending_mask & x["sla_breach"].fillna(False)
    resolved_df = x[resolved_mask & x["resolution_available"].fillna(False)]
    total = len(x)
    resolved = int(resolved_mask.sum())
    avg_frt = (
        round(x.loc[x["response_available"].fillna(False), "frt_min"].mean(), 1)
        if x["response_available"].fillna(False).any()
        else 0.0
    )
    return {
        "today_open": int((today_open_mask & pending_mask).sum()),
        "today_closed": int(today_closed_mask.sum()),
        "pending": int(pending_mask.sum()),
        "overdue": int(overdue_mask.sum()),
        "avg_resolution": round(resolved_df["actual_resolution_min"].mean(), 1) if not resolved_df.empty else 0,
        "resolution_rate": round((resolved / total) * 100, 1) if total else 0.0,
        "avg_frt": avg_frt,
    }


def build_department_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    out = df.groupby("department", as_index=False).agg(
        Tickets=("id", "size"),
        Resolved=("status", lambda s: (s == "Resolved").sum()),
    )
    out["Pending"] = out["Tickets"] - out["Resolved"]
    return out.sort_values(["Tickets", "Resolved"], ascending=[False, False])


def build_location_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    out = df.groupby("location", as_index=False).agg(
        Tickets=("id", "size"),
        Resolved=("status", lambda s: (s == "Resolved").sum()),
    )
    out["Pending"] = out["Tickets"] - out["Resolved"]
    return out.sort_values(["Tickets", "Resolved"], ascending=[False, False])


def build_technician_performance(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    x = df.copy()
    x["resolution_time"] = pd.to_numeric(x.get("resolution_time"), errors="coerce").fillna(0)
    out = x.groupby("attended_by", as_index=False).agg(
        Assigned=("id", "size"),
        Resolved=("status", lambda s: (s == "Resolved").sum()),
        Avg_Resolution_Min=(
            "resolution_time",
            lambda s: int(s[s > 0].mean()) if (s > 0).any() else 0,
        ),
    )
    out["Pending"] = out["Assigned"] - out["Resolved"]
    out["Resolution_%"] = ((out["Resolved"] / out["Assigned"]) * 100).round(1)
    return out.sort_values(["Assigned", "Resolved"], ascending=[False, False])


def build_repeat_issue_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    x = df.copy()
    x["complaint_norm"] = x["complaint"].fillna("").astype(str).str.strip().str.lower()
    x = x[x["complaint_norm"] != ""]
    if x.empty:
        return pd.DataFrame()
    out = x.groupby(["category", "complaint_norm"], as_index=False).agg(
        Tickets=("id", "size"), Last_Seen=("date", "max")
    )
    out = out[out["Tickets"] > 1].sort_values(["Tickets", "Last_Seen"], ascending=[False, False])
    return out.rename(columns={"complaint_norm": "Complaint Pattern"}).head(10)


def build_mttr_sla_summary(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    x = add_priority_and_sla(df)
    if x.empty or group_col not in x.columns:
        return pd.DataFrame()
    x["resolution_time"] = pd.to_numeric(x.get("resolution_time"), errors="coerce").fillna(0)
    return x.groupby(group_col, as_index=False).agg(
        Tickets=("id", "size"),
        Resolved=("status", lambda s: (s.astype(str) == "Resolved").sum()),
        MTTR_Min=("resolution_time", lambda s: round(s[s > 0].mean(), 1) if (s > 0).any() else 0),
        FRT_Min=("frt_min", lambda s: round(pd.Series(s).dropna().mean(), 1) if pd.Series(s).dropna().shape[0] else 0),
        SLA_Breach_Rate=("sla_breach", lambda s: round(pd.Series(s).fillna(False).mean() * 100, 1)),
    )


def build_ticket_aging_analysis(df: pd.DataFrame) -> dict:
    x = add_priority_and_sla(df)
    empty = {
        "aging_table": pd.DataFrame(),
        "most_aged": pd.DataFrame(),
        "avg_pending_age": 0,
        "oldest_ticket": pd.DataFrame(),
        "trend": pd.DataFrame(),
    }
    if x.empty:
        return empty
    p = x[x["status"].astype(str).isin(["Open", "In Progress", "On Hold - User Busy", "On Hold"])].copy()
    if p.empty:
        return empty
    p["age_days"] = (p["age_hours"] / 24).fillna(0)
    bins = [-1, 1, 3, 7, 15, 100000]
    labels = ["0-1 Days", "2-3 Days", "4-7 Days", "8-15 Days", "15+ Days"]
    p["aging_bucket"] = pd.cut(p["age_days"], bins=bins, labels=labels)
    aging = p.groupby("aging_bucket", as_index=False).agg(Tickets=("id", "size")).fillna(0)
    return {
        "aging_table": aging,
        "most_aged": p.sort_values("age_days", ascending=False).head(20),
        "avg_pending_age": round(p["age_days"].mean(), 1),
        "oldest_ticket": p.sort_values("age_days", ascending=False).head(1),
        "trend": pd.DataFrame(),
    }


def build_technician_scorecard(df: pd.DataFrame) -> pd.DataFrame:
    x = add_priority_and_sla(df)
    perf = build_technician_performance(x)
    if perf.empty:
        return pd.DataFrame()
    frt = x.groupby("attended_by", as_index=False).agg(
        Avg_FRT=("frt_min", lambda s: round(pd.Series(s).dropna().mean(), 1) if pd.Series(s).dropna().shape[0] else 0),
        SLA_Compliance=("sla_breach", lambda s: round((1 - pd.Series(s).fillna(False).mean()) * 100, 1)),
        Critical_Handled=("priority", lambda s: int(pd.Series(s).astype(str).eq("Critical").sum())),
        Ticket_Load=("id", "size"),
    )
    out = perf.merge(frt, on="attended_by", how="left")
    max_mttr = max(out["Avg_Resolution_Min"].max(), 1)
    max_pending = max(out["Pending"].max(), 1)
    max_frt = max(out["Avg_FRT"].max(), 1)
    max_critical = max(out["Critical_Handled"].max(), 1)
    out["Utilization_%"] = ((out["Assigned"] / max(out["Assigned"].sum(), 1)) * 100).round(1)
    out["Score"] = (
        out["Resolution_%"] * 0.25
        + out["SLA_Compliance"] * 0.20
        + ((1 - (out["Avg_Resolution_Min"] / max_mttr)) * 100).clip(lower=0) * 0.15
        + ((1 - (out["Avg_FRT"] / max_frt)) * 100).clip(lower=0) * 0.10
        + ((1 - (out["Pending"] / max_pending)) * 100).clip(lower=0) * 0.10
        + ((out["Critical_Handled"] / max_critical) * 100).clip(lower=0) * 0.10
        + out["Utilization_%"] * 0.10
    ).round(1)
    return out.sort_values("Score", ascending=False)


def build_month_over_month_comparison(df: pd.DataFrame) -> pd.DataFrame:
    x = add_priority_and_sla(df)
    if x.empty:
        return pd.DataFrame()
    x["_month"] = pd.to_datetime(x["date"], errors="coerce").dt.to_period("M").astype(str)
    months = sorted([m for m in x["_month"].dropna().unique().tolist() if m and m != "NaT"])
    if len(months) < 2:
        return pd.DataFrame()
    prev_m, cur_m = months[-2], months[-1]
    prev = x[x["_month"] == prev_m]
    cur = x[x["_month"] == cur_m]

    def _safe_pct(num: float, den: float) -> float:
        return round((num / den) * 100, 1) if den else 0.0

    def _metrics(d: pd.DataFrame) -> dict:
        total = len(d)
        resolved_mask = d["status"].astype(str).eq("Resolved")
        pending_mask = d["status"].astype(str).isin(["Open", "In Progress", "On Hold - User Busy", "On Hold"])
        breach_mask = d.get("sla_breach", pd.Series(dtype=bool)).fillna(False)
        return {
            "Ticket Volume": total,
            "Resolution Rate": _safe_pct(int(resolved_mask.sum()), total),
            "SLA %": round((1 - breach_mask.mean()) * 100, 1) if total else 0.0,
            "Pending": int(pending_mask.sum()),
        }

    p = _metrics(prev)
    c = _metrics(cur)
    rows = []
    for metric, prev_v in p.items():
        cur_v = c.get(metric, 0)
        var = round(cur_v - prev_v, 1)
        var_pct = round((var / prev_v) * 100, 1) if prev_v not in [0, 0.0] else None
        rows.append([metric, prev_m, cur_m, prev_v, cur_v, var, var_pct])
    return pd.DataFrame(
        rows,
        columns=[
            "Metric",
            "Previous_Month_Label",
            "Current_Month_Label",
            "Previous_Month",
            "Current_Month",
            "Variance",
            "Variance_%",
        ],
    )


def build_department_health(df: pd.DataFrame) -> pd.DataFrame:
    x = add_priority_and_sla(df)
    if x.empty:
        return pd.DataFrame()
    out = x.groupby("department", as_index=False).agg(
        Tickets=("id", "size"),
        Resolved=("status", lambda s: (s.astype(str) == "Resolved").sum()),
        Pending=(
            "status",
            lambda s: s.astype(str).isin(["Open", "In Progress", "On Hold - User Busy", "On Hold"]).sum(),
        ),
        MTTR=(
            "actual_resolution_min",
            lambda s: round(pd.to_numeric(s, errors="coerce").dropna().mean(), 1)
            if pd.to_numeric(s, errors="coerce").dropna().shape[0]
            else 0,
        ),
        SLA_Breach=("sla_breach", lambda s: round(pd.Series(s).fillna(False).mean() * 100, 1)),
    )
    total = max(out["Tickets"].sum(), 1)
    out["SLA_%"] = (100 - out["SLA_Breach"]).round(1)
    out["Load_%"] = ((out["Tickets"] / total) * 100).round(1)
    return out.sort_values("Tickets", ascending=False)


def build_detailed_ticket_exports(df: pd.DataFrame) -> dict:
    x = prepare_ticket_view(df)
    x = x.drop(columns=[c for c in ["date_parsed"] if c in x.columns])
    resolved = (
        x[x["status"].astype(str) == "Resolved"].copy()
        if not x.empty and "status" in x.columns
        else pd.DataFrame()
    )
    pending = (
        x[x["status"].astype(str).isin(["Open", "In Progress", "On Hold - User Busy", "On Hold"])].copy()
        if not x.empty and "status" in x.columns
        else pd.DataFrame()
    )
    return {
        "Master Tickets": x,
        "Resolved Tickets": resolved,
        "Pending Tickets": pending,
        "Ticket Technician": build_technician_performance(df),
        "Ticket Location": build_location_summary(df),
        "Ticket Department": build_department_summary(df),
        "Repeat Issues": build_repeat_issue_summary(df),
    }


def build_excel_report(tickets_df: pd.DataFrame, nas_df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        detailed = build_detailed_ticket_exports(tickets_df)
        for name, frame in detailed.items():
            if frame is not None and not frame.empty:
                frame.to_excel(writer, sheet_name=name[:31], index=False)
        nas_delta = compute_nas_changes(nas_df)
        nas_forecast = build_storage_forecast(nas_df)
        master, monthly, serverwise = build_nas_reports(nas_df)
        for name, frame in {
            "NAS Raw Logs": normalize_nas_df(nas_df),
            "NAS Deltas": nas_delta,
            "NAS Monthly": monthly,
            "NAS Server Summary": serverwise,
            "NAS Forecast": nas_forecast,
        }.items():
            if frame is not None and not frame.empty:
                frame.to_excel(writer, sheet_name=name[:31], index=False)
        tech = build_technician_scorecard(tickets_df)
        if tech is not None and not tech.empty:
            tech.to_excel(writer, sheet_name="Technician Scorecard", index=False)
        aging = build_ticket_aging_analysis(tickets_df).get("aging_table", pd.DataFrame())
        if aging is not None and not aging.empty:
            aging.to_excel(writer, sheet_name="Ticket Aging", index=False)
    return output.getvalue()
