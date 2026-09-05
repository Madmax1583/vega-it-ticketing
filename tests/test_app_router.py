"""Tests for V2-only scaffold route resolution."""

from __future__ import annotations

from app import V2_PAGES, resolve_v2_page


def test_v2_pages_are_explicit() -> None:
    assert V2_PAGES == ["V2 Status", "Data Quality"]


def test_router_accepts_known_pages() -> None:
    assert resolve_v2_page("V2 Status") == "V2 Status"
    assert resolve_v2_page("Data Quality") == "Data Quality"


def test_router_falls_back_for_unknown_page() -> None:
    assert resolve_v2_page("Admin Tools") == "V2 Status"
    assert resolve_v2_page(None) == "V2 Status"
