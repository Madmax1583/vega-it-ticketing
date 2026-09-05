"""Unit tests for services.tickets (V2 Phase 2c)."""

from __future__ import annotations

import pandas as pd

from services.tickets import (
    add_priority_and_sla,
    auto_categorize,
    format_ticket_number,
    normalize_category,
    normalize_ticket_df,
    prepare_ticket_view,
)


def test_format_ticket_number_vega() -> None:
    assert format_ticket_number(12, "Sector - 136 Vega") == "VEGA-2026-0012"


def test_format_ticket_number_knitpro() -> None:
    assert format_ticket_number(7, "Knitpro 28-29") == "KP-2026-0007"


def test_auto_categorize_keywords() -> None:
    assert auto_categorize("CCTV camera flickering") == "CCTVCamera"
    assert auto_categorize("Outlook not opening") == "EmailOutlook"
    assert auto_categorize("Printer queue stuck") == "Printer"
    assert auto_categorize("unknown issue") == "Other"


def test_normalize_category_aliases() -> None:
    assert normalize_category("CCTV/Camera") == "CCTVCamera"
    assert normalize_category("laptop hardware") == "LaptopHardware"
    assert normalize_category("") == "Other"


def test_normalize_ticket_df_empty() -> None:
    out = normalize_ticket_df(pd.DataFrame())
    assert out.empty
    assert "id" in out.columns
    assert "complaint" in out.columns


def test_normalize_ticket_df_fills_missing_columns() -> None:
    raw = pd.DataFrame([{"id": "4", "complaint": "wifi down", "status": None}])
    out = normalize_ticket_df(raw)
    assert int(out.iloc[0]["id"]) == 4
    assert out.iloc[0]["status"] == ""
    assert out.iloc[0]["resolution_time"] == 0


def test_prepare_ticket_view_adds_system_id() -> None:
    df = pd.DataFrame(
        [
            {
                "id": 3,
                "date": "2026-07-05",
                "location": "Sector - 155 Vega",
                "status": "Resolved",
            }
        ]
    )
    view = prepare_ticket_view(df)
    assert view.iloc[0]["System Ticket ID"] == "VEGA-2026-0003"


def test_add_priority_and_sla_on_empty() -> None:
    out = add_priority_and_sla(pd.DataFrame())
    assert out.empty


def test_add_priority_and_sla_sets_flags() -> None:
    df = pd.DataFrame(
        [
            {
                "id": 1,
                "date": "2026-07-01",
                "complaint": "SAP is down",
                "status": "Open",
                "start_time": "2026-07-01 10:00:00",
                "close_time": None,
                "resolution_time": 0,
            }
        ]
    )
    out = add_priority_and_sla(df)
    assert out.iloc[0]["priority"] == "Critical"
    assert "sla_breach" in out.columns
    assert "age_hours" in out.columns
