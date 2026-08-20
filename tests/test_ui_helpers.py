"""Tests for pure V2 UI helper behavior."""

from __future__ import annotations

from ui.components import badge_class, format_metric, status_tone
from ui.navigation import allowed_pages, flat_pages, grouped_pages, resolve_page


def test_status_tones() -> None:
    assert status_tone("Resolved") == "success"
    assert status_tone("Failed") == "danger"
    assert status_tone("In Progress") == "warning"
    assert status_tone("unknown") == "neutral"


def test_badge_class_has_safe_default() -> None:
    assert badge_class("success") == "v2-badge-success"
    assert badge_class("unexpected") == "v2-badge-neutral"


def test_format_metric() -> None:
    assert format_metric(1234) == "1,234"
    assert format_metric(12.34, "%") == "12.3%"
    assert format_metric(None) == "—"
    assert format_metric("") == "—"


def test_it_manager_navigation_is_grouped() -> None:
    groups = grouped_pages("IT Manager")
    assert "Workspace" in groups
    assert "Analytics" in groups
    assert "Admin Tools" in groups["Administration"]


def test_avp_navigation_excludes_admin_tools() -> None:
    pages = allowed_pages("AVP")
    assert "Admin Tools" not in pages
    assert resolve_page("Admin Tools", "AVP") == "Home"


def test_resolve_page_accepts_allowed_page() -> None:
    assert resolve_page("Reports", "IT Manager") == "Reports"


def test_flat_pages_removes_duplicates() -> None:
    assert flat_pages({"A": ["Home", "Reports"], "B": ["Reports", "Admin"]}) == ["Home", "Reports", "Admin"]
