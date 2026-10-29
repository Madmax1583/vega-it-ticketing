"""Application settings and constants (V2)."""

from __future__ import annotations

APP_NAME = "Vega & Knitpro IT Operations Dashboard"
APP_VERSION = "2.0.0-dev"
BUILD_DATE = "2026-08-22"
COMPANY_NAME = "Vega Industries Pvt. Ltd."

# Phase 0 safety: block live Ticket/NAS writes until explicitly enabled
V2_WRITE_ENABLED = False

# Session lifetime (hours) for auth_sessions table
SESSION_HOURS = 12

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

# Seed users for SQLite support DB (must_change_password on first login)
DEFAULT_USERS = [
    {"username": "amit", "display_name": "Amit", "role": "IT Manager", "password": "ChangeMe123!"},
    {"username": "satish", "display_name": "Satish", "role": "IT AM", "password": "ChangeMe123!"},
    {"username": "priyanshu", "display_name": "Priyanshu", "role": "IT Executive", "password": "ChangeMe123!"},
    {"username": "ranjan", "display_name": "Ranjan", "role": "IT Executive", "password": "ChangeMe123!"},
    {"username": "manish", "display_name": "Manish", "role": "IT Executive", "password": "ChangeMe123!"},
    {"username": "executive", "display_name": "Executive Viewer", "role": "Executive", "password": "ChangeMe123!"},
]

# Role → allowed page labels (must match PAGE_RENDERERS keys where applicable)
ROLE_PAGES = {
    "IT Manager": [
        "Home",
        "Ticket Operations",
        "NAS Monitoring",
        "Reports",
        "Data Quality",
        "Task Center",
        "Admin Tools",
        "Team Chat",
        "Executive Command Center",
        "Overview",
        "AVP Dashboard",
        "Department Health",
        "Vendor Dashboard",
        "Asset Health",
    ],
    "IT AM": [
        "Home",
        "Ticket Operations",
        "NAS Monitoring",
        "Reports",
        "Data Quality",
        "Task Center",
        "Team Chat",
        "Overview",
    ],
    "IT Executive": [
        "Home",
        "Ticket Operations",
        "NAS Monitoring",
        "Task Center",
        "Team Chat",
    ],
    "Executive": [
        "Home",
        "Executive Command Center",
        "Overview",
        "Reports",
        "AVP Dashboard",
        "Department Health",
    ],
    "AVP": [
        "Home",
        "AVP Dashboard",
        "Reports",
        "Department Health",
        "Vendor Dashboard",
    ],
    "User": ["Home"],
}
