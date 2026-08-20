"""
Central application settings for Vega IT Operations (V2).

Extracted from script.py — values must stay in sync with production until cutover.
"""

APP_NAME = "Vega & Knitpro IT Operations Dashboard"
APP_VERSION = "2.0.0-dev"
BUILD_DATE = "2026-08-20"
COMPANY_NAME = "Vega Industries Pvt. Ltd."

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

STATUS_OPTIONS = [
    "Open",
    "In Progress",
    "On Hold - User Busy",
    "Resolved",
]

SERVER_NAMES = ["HRI", "Vega", "Sery", "Rise"]

SERVER_SHEET_MAP = {
    "HRI": "Sheet 1",
    "Vega": "Sheet 2",
    "Sery": "Sheet 3",
    "Rise": "Sheet 4",
}

# NAS capacity assumptions used by forecast helpers (GB)
NAS_CAPACITY_MAP = {
    "HRI": 1000.0,
    "Vega": 500.0,
    "Sery": 100.0,
    "Rise": 100.0,
}

DEFAULT_USERS = [
    ("amit", "Amit", "IT Manager"),
    ("satish", "Satish", "IT AM"),
    ("ranjan", "Ranjan", "Sr. Executive"),
    ("priyanshu", "Priyanshu", "IT Executive"),
    ("manish", "Manish", "IT Executive"),
    ("satender", "Mr. Satender Vashisht", "AVP"),
]

# Role -> allowed page labels (must match production get_role_pages)
ROLE_PAGES = {
    "IT Manager": [
        "Home",
        "Executive Command Center",
        "Overview",
        "Ticket Operations",
        "NAS Monitoring",
        "Reports",
        "Task Center",
        "Admin Tools",
        "AVP Dashboard",
        "Team Chat",
        "Vendor Dashboard",
        "Department Health",
        "Asset Health",
    ],
    "IT AM": [
        "Home",
        "Executive Command Center",
        "Overview",
        "Ticket Operations",
        "NAS Monitoring",
        "Reports",
        "Task Center",
        "Team Chat",
        "Vendor Dashboard",
        "Department Health",
        "Asset Health",
    ],
    "AVP": [
        "Home",
        "Executive Command Center",
        "Overview",
        "AVP Dashboard",
        "Reports",
        "Task Center",
        "Team Chat",
        "Vendor Dashboard",
        "Department Health",
        "Asset Health",
    ],
    "default": [
        "Home",
        "Overview",
        "Ticket Operations",
        "NAS Monitoring",
        "Task Center",
        "Team Chat",
    ],
}

NAVIGATION_GROUPS = {
    "📊 Dashboard": ["Home", "Executive Command Center", "Overview"],
    "🎫 Operations": ["Ticket Operations", "Task Center", "Team Chat"],
    "📈 Analytics": ["Reports", "AVP Dashboard", "Department Health", "Vendor Dashboard"],
    "🖥 Infrastructure": ["NAS Monitoring", "Asset Health"],
    "⚙ Administration": ["Admin Tools"],
}
