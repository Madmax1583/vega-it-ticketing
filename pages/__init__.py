"""Page renderers (Phase 4)."""

from pages.home import render_home_page
from pages.nas import render_nas_page
from pages.reports import render_reports_page
from pages.tickets import render_tickets_page

PAGE_RENDERERS = {
    "Home": render_home_page,
    "Ticket Operations": render_tickets_page,
    "NAS Monitoring": render_nas_page,
    "Reports": render_reports_page,
}

__all__ = [
    "PAGE_RENDERERS",
    "render_home_page",
    "render_tickets_page",
    "render_nas_page",
    "render_reports_page",
]
