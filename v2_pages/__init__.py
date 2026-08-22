"""
V2 page renderers (Phase 0: renamed from pages/ to avoid Streamlit
auto-discovery of multipage apps outside the custom router).
"""

from v2_pages.home import render_home_page
from v2_pages.nas import render_nas_page
from v2_pages.reports import render_reports_page
from v2_pages.tickets import render_tickets_page

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
