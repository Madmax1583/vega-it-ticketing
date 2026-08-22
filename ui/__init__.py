"""Shared UI layer (Phase 3)."""

from ui.components import (
    render_info_feed,
    render_kpi_card,
    render_nas_status,
    render_status_table,
    status_badge_html,
)
from ui.navigation import get_navigation_groups, page_breadcrumb
from ui.theme import inject_enterprise_ui_css, inject_scaffold_css

__all__ = [
    "inject_enterprise_ui_css",
    "inject_scaffold_css",
    "status_badge_html",
    "render_nas_status",
    "render_status_table",
    "render_kpi_card",
    "render_info_feed",
    "get_navigation_groups",
    "page_breadcrumb",
]
