"""Role-aware navigation helpers for the V2 custom router."""

from __future__ import annotations

from collections.abc import Iterable

from services.auth import get_role_pages


PAGE_GROUPS = {
    "Workspace": ["Home", "Overview", "Ticket Operations", "NAS Monitoring", "Task Center", "Team Chat"],
    "Analytics": ["Executive Command Center", "Reports", "AVP Dashboard", "Department Health", "Asset Health"],
    "Administration": ["Admin Tools", "Vendor Dashboard"],
}


def allowed_pages(role: str) -> list[str]:
    """Return the role's allowed pages in their source-of-truth order."""
    return list(get_role_pages(role))


def grouped_pages(role: str) -> dict[str, list[str]]:
    """Return non-empty navigation groups filtered to a role's permissions."""
    allowed = set(allowed_pages(role))
    groups: dict[str, list[str]] = {}
    for group, pages in PAGE_GROUPS.items():
        visible = [page for page in pages if page in allowed]
        if visible:
            groups[group] = visible
    uncategorized = [page for page in allowed_pages(role) if not any(page in pages for pages in PAGE_GROUPS.values())]
    if uncategorized:
        groups["Other"] = uncategorized
    return groups


def resolve_page(requested_page: str | None, role: str, fallback: str = "Home") -> str:
    """Return an allowed page, preventing stale/unauthorized page selections."""
    allowed = allowed_pages(role)
    if requested_page in allowed:
        return str(requested_page)
    if fallback in allowed:
        return fallback
    return allowed[0] if allowed else fallback


def flat_pages(groups: dict[str, Iterable[str]]) -> list[str]:
    """Flatten navigation groups without duplicates while keeping order."""
    seen: set[str] = set()
    result: list[str] = []
    for pages in groups.values():
        for page in pages:
            if page not in seen:
                seen.add(page)
                result.append(page)
    return result
