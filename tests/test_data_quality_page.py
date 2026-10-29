"""Tests for the V2 Data Quality page model without Streamlit rendering."""

from __future__ import annotations

import pandas as pd

from pages.data_quality import page_data


def test_page_data_empty_inputs_are_safe() -> None:
    report = page_data(pd.DataFrame(), pd.DataFrame())
    assert report["tickets"]["summary"]["ticket_count"] == 0
    assert report["nas"]["summary"]["nas_log_count"] == 0
    assert len(report["warnings"]) == 2


def test_page_data_exposes_ticket_and_nas_diagnostics() -> None:
    tickets = pd.DataFrame(
        [
            {
                "id": 1,
                "date": "2026-08-01",
                "status": "Resolved",
                "department": "IT",
                "category": "Printer",
                "start_time": "2026-08-01 09:00",
                "close_time": "2026-08-01 10:00",
                "resolution_time": 60,
                "attended_by": "Amit",
            }
        ]
    )
    nas = pd.DataFrame(
        [
            {
                "date": "2026-08-20",
                "server_name": "HRI",
                "status": "Success",
                "storage_used": 42.0,
            }
        ]
    )
    report = page_data(tickets, nas, freshness_days=365)
    assert report["tickets"]["summary"]["ticket_count"] == 1
    assert report["nas"]["summary"]["server_count"] == 1
    assert report["nas"]["summary"]["freshness"] == "fresh"
    assert "completeness" in report["tickets"]
    assert "server_profile" in report["nas"]
