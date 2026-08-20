"""Unit tests for services.data_quality (V2)."""

from __future__ import annotations

import pandas as pd

from services.data_quality import build_data_quality_report, profile_nas, profile_tickets


def test_empty_ticket_profile_is_safe() -> None:
    report = profile_tickets(pd.DataFrame())
    assert report["summary"]["ticket_count"] == 0
    assert report["completeness"].empty
    assert report["warnings"] == ["No ticket data available."]


def test_ticket_profile_counts_quality_gaps_without_mutating_input() -> None:
    tickets = pd.DataFrame(
        [
            {
                "id": 1,
                "date": "2026-08-01",
                "status": "Resolved",
                "start_time": "2026-08-01 09:00:00",
                "close_time": "",
                "resolution_time": 0,
                "department": "Sales Return",
                "category": "Printer",
                "attended_by": "Amit",
            },
            {
                "id": 2,
                "date": "bad-date",
                "status": "Open",
                "start_time": None,
                "close_time": None,
                "resolution_time": "45",
                "department": "Sales return",
                "category": None,
                "attended_by": None,
            },
        ]
    )
    before_columns = tickets.columns.tolist()
    report = profile_tickets(tickets)
    values = report["completeness"].set_index("metric")["missing_count"]
    assert report["summary"]["ticket_count"] == 2
    assert values["Missing ticket date"] == 1
    assert values["Missing start time"] == 1
    assert values["Resolved tickets missing close time"] == 1
    assert values["Zero or missing resolution duration"] == 1
    assert values["Missing category"] == 1
    assert values["Missing technician"] == 1
    assert before_columns == tickets.columns.tolist()


def test_ticket_profile_detects_single_status_warning() -> None:
    tickets = pd.DataFrame(
        [{"id": 1, "date": "2026-08-01", "status": "Resolved", "department": "IT"}]
    )
    report = profile_tickets(tickets)
    assert any("Only one ticket status" in warning for warning in report["warnings"])


def test_ticket_profile_handles_missing_columns() -> None:
    report = profile_tickets(pd.DataFrame([{"id": 1}]))
    assert report["summary"]["ticket_count"] == 1
    assert report["summary"]["status_count"] == 1
    assert not report["completeness"].empty


def test_empty_nas_profile_is_safe() -> None:
    report = profile_nas(pd.DataFrame())
    assert report["summary"]["nas_log_count"] == 0
    assert report["summary"]["freshness"] == "unavailable"


def test_nas_profile_counts_failures_and_missing_storage() -> None:
    nas = pd.DataFrame(
        [
            {"date": "2026-08-19", "server_name": "HRI", "status": "Success", "storage_used": "42.5"},
            {"date": "2026-08-20", "server_name": "Vega", "status": "Failed", "storage_used": None},
        ]
    )
    report = profile_nas(nas, freshness_days=365)
    assert report["summary"]["nas_log_count"] == 2
    assert report["summary"]["server_count"] == 2
    assert report["summary"]["failure_count"] == 1
    assert report["summary"]["missing_storage_count"] == 1
    assert report["summary"]["freshness"] == "fresh"


def test_nas_profile_detects_stale_log() -> None:
    nas = pd.DataFrame(
        [{"date": "2020-01-01", "server_name": "HRI", "status": "Success", "storage_used": 1}]
    )
    report = profile_nas(nas, freshness_days=7)
    assert report["summary"]["freshness"] == "stale"
    assert any("older than" in warning for warning in report["warnings"])


def test_combined_report_joins_warnings() -> None:
    report = build_data_quality_report(pd.DataFrame(), pd.DataFrame())
    assert len(report["warnings"]) == 2
    assert report["tickets"]["summary"]["ticket_count"] == 0
    assert report["nas"]["summary"]["nas_log_count"] == 0
