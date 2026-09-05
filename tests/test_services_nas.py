"""Unit tests for services.nas (V2 Phase 2c)."""

from __future__ import annotations

import pandas as pd

from services.nas import (
    build_nas_reports,
    compute_nas_changes,
    normalize_nas_df,
    normalize_nas_status,
)


def test_normalize_nas_status() -> None:
    assert normalize_nas_status("success") == "Success"
    assert normalize_nas_status("OK") == "Success"
    assert normalize_nas_status("failed") == "Failed"
    assert normalize_nas_status("timeout") == "Failed"


def test_normalize_nas_df_empty() -> None:
    out = normalize_nas_df(pd.DataFrame())
    assert out.empty
    assert list(out.columns) == ["id", "date", "server_name", "status", "storage_used", "remarks"]


def test_normalize_nas_df_coerces_types() -> None:
    raw = pd.DataFrame(
        [
            {
                "id": "2",
                "date": "2026-07-12",
                "server_name": "HRI",
                "status": "ok",
                "storage_used": "43.5",
                "remarks": None,
            }
        ]
    )
    out = normalize_nas_df(raw)
    assert int(out.iloc[0]["id"]) == 2
    assert out.iloc[0]["status"] == "Success"
    assert float(out.iloc[0]["storage_used"]) == 43.5
    assert out.iloc[0]["remarks"] == ""


def test_compute_nas_changes_empty() -> None:
    out = compute_nas_changes(pd.DataFrame())
    assert out.empty
    assert "delta_gb" in out.columns


def test_compute_nas_changes_increment() -> None:
    df = pd.DataFrame(
        [
            {"id": 1, "date": "2026-07-11", "server_name": "HRI", "status": "Success", "storage_used": 40.0, "remarks": ""},
            {"id": 2, "date": "2026-07-12", "server_name": "HRI", "status": "Success", "storage_used": 42.0, "remarks": ""},
        ]
    )
    out = compute_nas_changes(df).sort_values("id")
    second = out.iloc[1]
    assert float(second["delta_gb"]) == 2.0
    assert second["change_type"] == "Increment"


def test_build_nas_reports_empty() -> None:
    master, monthly, serverwise = build_nas_reports(pd.DataFrame())
    assert master.empty
    assert monthly.empty
    assert serverwise.empty
