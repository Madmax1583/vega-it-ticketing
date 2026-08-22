"""Application settings and constants (V2)."""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------
APP_NAME = "Vega & Knitpro IT Operations Dashboard"
APP_VERSION = "2.0.0-dev"
BUILD_DATE = "2026-08-22"
COMPANY_NAME = "Vega Industries Pvt. Ltd."

# ---------------------------------------------------------------------------
# Safety (Phase 0)
# ---------------------------------------------------------------------------
# When False, Ticket/NAS forms in V2 must not insert/update/delete.
# Set True only for explicit UAT or approved live write tests.
V2_WRITE_ENABLED = False

# ---------------------------------------------------------------------------
# Domain lists (aligned with production script.py)
# ---------------------------------------------------------------------------
TECH_MAP = {
    "Satish": "TECH-01",
    "Priyanshu": "TECH-02",
    "Amit": "TECH-03",
    "Ranjan": "TECH-04",
    "Manish": "TECH-05",
}

OFFICIAL_LOCATIONS = [
    "Sector - 136 Vega",
    "Knitpro 28-29",
    "Sector - 155 Vega",
    "Knitpro - Jaipur",
    "Knitpro 42",
    "Knitpro 72-73",
    "Knitpro 75",
    "Bharat Composite Sector 80",
    "Vega Sector 80",
]

STATUS_OPTIONS = ["Open", "In Progress", "On Hold - User Busy", "Resolved"]

SERVER_NAMES = ["HRI", "Vega", "Sery", "Rise"]

NAS_CAPACITY_MAP = {
    "HRI": 1000.0,
    "Vega": 500.0,
    "Sery": 100.0,
    "Rise": 100.0,
}
