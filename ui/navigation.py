"""Navigation helpers (V2 Phase 3)."""

from __future__ import annotations

from services.auth import get_role_pages


def get_navigation_groups(role: str) -> dict:
    pages = get_role_pages(role)
    groups = {
        "Dashboard": ["Home", "Executive Command Center", "Overview"],
        "Operations": ["Ticket Operations", "Task Center", "Team Chat"],
        "Analytics": ["Reports", "AVP Dashboard", "Department Health", "Vendor Dashboard"],
        "Infrastructure": ["NAS Monitoring", "Asset Health"],
        "Administration": ["Admin Tools"],
    }
    return {
        group: [p for p in plist if p in pages]
        for group, plist in groups.items()
        if any(p in pages for p in plist)
    }


def page_breadcrumb(page: str) -> str:
    mapping = {
        "Home": "Home",
        "Executive Command Center": "Home > Dashboard > Executive Command Center",
        "Overview": "Home > Dashboard > Overview",
        "Ticket Operations": "Home > Operations > Ticket Operations",
        "Task Center": "Home > Operations > Task Center",
        "Team Chat": "Home > Operations > Team Chat",
        "Reports": "Home > Analytics > Reports",
        "AVP Dashboard": "Home > Analytics > AVP Dashboard",
        "Department Health": "Home > Analytics > Department Health",
        "Vendor Dashboard": "Home > Analytics > Vendor Dashboard",
        "NAS Monitoring": "Home > Infrastructure > NAS Monitoring",
        "Asset Health": "Home > Infrastructure > Asset Health",
        "Admin Tools": "Home > Administration > Admin Tools",
    }
    return mapping.get(page, f"Home > {page}")
