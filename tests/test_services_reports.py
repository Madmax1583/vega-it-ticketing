"""Unit tests for services.reports (V2 Phase 2c)."""

from __future__ import annotations

import pandas as pd

from services.reports import (
    build_department_summary,
    build_excel_report,
    build_technician_performance,
    build_ticket_aging_analysis,
    build_ticket_exec_metrics,
)


def _sample_tickets() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "id": 1,
                "date": "2026-07-01",
                "user_name": "Amit",
                "department": "IT",
                "complaint": "CCTV camera flickering",
                "location": "Sector - 136 Vega",
                "attended_by": "Satish",
                "status": "Open",
                "category": "CCTV/Camera",
                "start_time": "2026-07-01 10:15:00",
                "close_time": None,
                "resolution_time": 0,
                "remarks": "",
            },
            {
                "id": 2,
                "date": "2026-07-05",
                "user_name": "Rajesh",
                "department": "HR",
                "complaint": "Office printer offline",
                "location": "Sector - 155 Vega",
                "attended_by": "Amit",
                "status": "Resolved",
                "category": "Printer",
                "start_time": "2026-07-05 10:00:00",
                "close_time": "2026-07-05 10:35:00",
                "resolution_time": 35,
                "remarks": "fixed",
            },
        ]
    )


def _sample_nas() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"id": 1, "date": "2026-07-11", "server_name": "HRI", "status": "Success", "storage_used": 43.0, "remarks": "ok"},
            {"id": 2, "date": "2026-07-12", "server_name": "HRI", "status": "Success", "storage_used": 44.0, "remarks": "ok"},
        ]
    )


def test_exec_metrics_empty() -> None:
    metrics = build_ticket_exec_metrics(pd.DataFrame())
    assert metrics["pending"] == 0
    assert metrics["today_open"] == 0
    assert metrics["resolution_rate"] == 0.0


def test_exec_metrics_counts_pending() -> None:
    metrics = build_ticket_exec_metrics(_sample_tickets())
    assert metrics["pending"] == 1
    assert metrics["resolution_rate"] == 50.0


def test_department_summary_empty() -> None:
    assert build_department_summary(pd.DataFrame()).empty


def test_department_summary_groups() -> None:
    out = build_department_summary(_sample_tickets())
    assert set(out["department"]) == {"IT", "HR"}


def test_technician_performance_empty() -> None:
    assert build_technician_performance(pd.DataFrame()).empty


def test_aging_empty_and_resolved_only() -> None:
    empty = build_ticket_aging_analysis(pd.DataFrame())
    assert empty["aging_table"].empty
    resolved_only = _sample_tickets()
    resolved_only["status"] = "Resolved"
    out = build_ticket_aging_analysis(resolved_only)
    assert out["aging_table"].empty


def test_aging_pending_does_not_raise() -> None:
    out = build_ticket_aging_analysis(_sample_tickets())
    assert "aging_table" in out
    assert out["avg_pending_age"] >= 0


def test_excel_empty_returns_xlsx_bytes() -> None:
    data = build_excel_report(pd.DataFrame(), pd.DataFrame())
    assert isinstance(data, (bytes, bytearray))
    assert data[:2] == b"PK"


def test_excel_sample_returns_xlsx_bytes() -> None:
    data = build_excel_report(_sample_tickets(), _sample_nas())
    assert isinstance(data, (bytes, bytearray))
    assert data[:2] == b"PK"
    assert len(data) > 2000
