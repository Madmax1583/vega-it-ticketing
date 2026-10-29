"""
NAS backup domain service (V2 Phase 2).

Extracted from script.py — load/save/normalize/delta/forecast helpers.
"""

from __future__ import annotations

from typing import Any, Optional, Tuple

import pandas as pd
import streamlit as st

from config.settings import NAS_CAPACITY_MAP, SERVER_NAMES
from db.supabase_client import get_supabase_client, is_db_connected, table_exists

NAS_COLUMNS = ["id", "date", "server_name", "status", "storage_used", "remarks"]


def _ensure_local_nas() -> None:
    if "local_nas" not in st.session_state:
        st.session_state.local_nas = pd.DataFrame(
            [
                {"id": 1, "date": "2026-07-11", "server_name": "HRI", "status": "Success", "storage_used": 43.3975, "remarks": "Daily backup completed."},
                {"id": 2, "date": "2026-07-12", "server_name": "HRI", "status": "Success", "storage_used": 43.3985, "remarks": "Daily backup completed."},
                {"id": 3, "date": "2026-07-13", "server_name": "HRI", "status": "Failed", "storage_used": 43.3985, "remarks": "Handshake timeout."},
                {"id": 4, "date": "2026-07-13", "server_name": "Vega", "status": "Success", "storage_used": 236.1529, "remarks": "Backup completed."},
                {"id": 5, "date": "2026-07-15", "server_name": "Sery", "status": "Success", "storage_used": 4.2406, "remarks": "Incremental snapshot success."},
                {"id": 6, "date": "2026-07-15", "server_name": "Rise", "status": "Success", "storage_used": 6.4914, "remarks": "Replication completed."},
            ]
        )


def normalize_nas_status(value: Any) -> str:
    s = str(value).strip().lower()
    if s in {"success", "ok", "passed", "pass", "complete", "completed"}:
        return "Success"
    if s in {"failed", "fail", "error", "warning", "warn", "partial", "warning / partial"}:
        return "Failed"
    return "Failed"


def normalize_nas_df(df: Optional[pd.DataFrame]) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=NAS_COLUMNS)
    out = df.copy()
    for col in NAS_COLUMNS:
        if col not in out.columns:
            out[col] = None
    out["id"] = pd.to_numeric(out["id"], errors="coerce").fillna(0).astype(int)
    out["storage_used"] = pd.to_numeric(out["storage_used"], errors="coerce").fillna(0.0)
    out["remarks"] = out["remarks"].fillna("").astype(str)
    out["server_name"] = out["server_name"].fillna("").astype(str)
    out["status"] = out["status"].fillna("").astype(str).str.strip().map(normalize_nas_status)
    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    return out[NAS_COLUMNS]


def get_next_nas_id(df: pd.DataFrame) -> int:
    if df.empty or "id" not in df.columns:
        return 1
    return int(pd.to_numeric(df["id"], errors="coerce").fillna(0).max()) + 1


def filtered_nas(df: pd.DataFrame, server_filter: str = "All") -> pd.DataFrame:
    out = df.copy()
    if out.empty:
        return out
    if server_filter != "All":
        out = out[out["server_name"] == server_filter]
    return out


def compute_nas_changes(df: Optional[pd.DataFrame]) -> pd.DataFrame:
    empty_cols = [
        "id", "date", "server_name", "status", "storage_used",
        "delta_gb", "delta_pct", "change_label", "change_type", "remarks",
    ]
    if df is None or df.empty:
        return pd.DataFrame(columns=empty_cols)
    out = normalize_nas_df(df).copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out = out.dropna(subset=["date"]).sort_values(["server_name", "date"])
    out["delta_gb"] = out.groupby("server_name")["storage_used"].diff().fillna(0.0)
    prev = out.groupby("server_name")["storage_used"].shift(1)
    out["delta_pct"] = ((out["storage_used"] - prev) / prev.replace(0, pd.NA) * 100).fillna(0.0)
    out["change_label"] = out["delta_gb"].apply(
        lambda x: f"+{x:.4f} GB" if x > 0 else (f"{x:.4f} GB" if x < 0 else "0.0000 GB")
    )
    out["change_type"] = out["delta_gb"].apply(
        lambda x: "Increment" if x > 0 else ("Decrement" if x < 0 else "No Change")
    )
    return out


def build_nas_reports(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    d = compute_nas_changes(df)
    if d.empty:
        empty = pd.DataFrame()
        return empty, empty, empty
    d["month"] = d["date"].dt.strftime("%Y-%m")
    master = d[[c for c in ["id", "date", "server_name", "status", "storage_used", "delta_gb", "delta_pct", "change_type", "remarks"] if c in d.columns]].copy()
    monthly = d.groupby(["month", "server_name"], as_index=False).agg(
        logs=("server_name", "size"),
        avg_storage=("storage_used", "mean"),
        min_storage=("storage_used", "min"),
        max_storage=("storage_used", "max"),
        total_increment=("delta_gb", lambda s: s[s > 0].sum()),
        total_decrement=("delta_gb", lambda s: abs(s[s < 0].sum())),
        failures=("status", lambda s: (s == "Failed").sum()),
    )
    serverwise = d.groupby("server_name", as_index=False).agg(
        logs=("server_name", "size"),
        latest_date=("date", "max"),
        latest_storage=("storage_used", "last"),
        total_increment=("delta_gb", lambda s: s[s > 0].sum()),
        total_decrement=("delta_gb", lambda s: abs(s[s < 0].sum())),
        failures=("status", lambda s: (s == "Failed").sum()),
    )
    return master, monthly, serverwise


def build_storage_forecast(df: pd.DataFrame) -> pd.DataFrame:
    x = normalize_nas_df(df).copy()
    if x.empty:
        return pd.DataFrame()
    x["date"] = pd.to_datetime(x["date"], errors="coerce")
    x = x.dropna(subset=["date"]).sort_values(["server_name", "date"])
    capacity_map = dict(NAS_CAPACITY_MAP)
    rows = []
    for server, g in x.groupby("server_name"):
        if len(g) < 2:
            continue
        day_index = (g["date"] - g["date"].min()).dt.days.astype(float)
        y = pd.to_numeric(g["storage_used"], errors="coerce").fillna(0).astype(float)
        capacity = float(capacity_map.get(server, max(y.max() * 1.25, 100.0)))
        try:
            import numpy as np

            slope, intercept = np.polyfit(day_index, y, 1)
            latest_storage = float(y.iloc[-1])
            utilization_pct = round((latest_storage / capacity) * 100, 2) if capacity > 0 else 0.0
            days_to_full = None
            if slope > 0 and latest_storage < capacity:
                days_to_full = round((capacity - latest_storage) / slope, 1)
            forecast_7 = round(latest_storage + slope * 7, 2)
            forecast_30 = round(latest_storage + slope * 30, 2)
            forecast_90 = round(latest_storage + slope * 90, 2)
            backup_success = round((g["status"].astype(str).eq("Success").mean()) * 100, 1)
            util_score = max(0, 100 - utilization_pct)
            growth_score = max(0, 100 - min(max(slope, 0) * 20, 100))
            horizon_score = 100 if days_to_full is None else max(0, min((days_to_full / 180) * 100, 100))
            health_score = round(
                util_score * 0.35 + growth_score * 0.25 + horizon_score * 0.25 + backup_success * 0.15, 1
            )
            rows.append(
                {
                    "server_name": server,
                    "capacity_gb": round(capacity, 2),
                    "latest_storage": round(latest_storage, 4),
                    "utilization_pct": utilization_pct,
                    "daily_growth_est": round(float(slope), 4),
                    "forecast_7d": forecast_7,
                    "forecast_30d": forecast_30,
                    "forecast_90d": forecast_90,
                    "projected_days_to_full": days_to_full,
                    "backup_success_pct": backup_success,
                    "nas_health_score": health_score,
                }
            )
        except Exception:
            pass
    return pd.DataFrame(rows)


def load_nas_data() -> pd.DataFrame:
    if is_db_connected():
        client = get_supabase_client()
        try:
            if table_exists("nasbackups"):
                response = client.table("nasbackups").select("*").execute()
                return normalize_nas_df(pd.DataFrame(response.data) if response.data else pd.DataFrame())
            if table_exists("nas_backups"):
                response = client.table("nas_backups").select("*").execute()
                return normalize_nas_df(pd.DataFrame(response.data) if response.data else pd.DataFrame())
        except Exception:
            pass
    _ensure_local_nas()
    return normalize_nas_df(st.session_state.local_nas)


def save_nas_log(new_row: dict) -> Optional[int]:
    row = dict(new_row)
    if is_db_connected():
        client = get_supabase_client()
        # Prefer nas_backups naming used in production schema docs
        target = "nas_backups" if table_exists("nas_backups") else ("nasbackups" if table_exists("nasbackups") else "nas_backups")
        response = client.table(target).insert(row).execute()
        if response.data and "id" in response.data[0]:
            return int(response.data[0]["id"])
        return None

    _ensure_local_nas()
    current = st.session_state.local_nas.copy()
    row["id"] = get_next_nas_id(current)
    st.session_state.local_nas = pd.concat([current, pd.DataFrame([row])], ignore_index=True)
    return int(row["id"])


def delete_nas_log(log_id: int) -> None:
    if is_db_connected():
        client = get_supabase_client()
        target = "nasbackups" if table_exists("nasbackups") else ("nas_backups" if table_exists("nas_backups") else None)
        if target:
            client.table(target).delete().eq("id", int(log_id)).execute()
        return

    _ensure_local_nas()
    st.session_state.local_nas = st.session_state.local_nas[
        st.session_state.local_nas["id"] != int(log_id)
    ].reset_index(drop=True)
