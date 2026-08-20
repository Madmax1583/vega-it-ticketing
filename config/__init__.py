"""Application configuration package (V2)."""

from config.settings import (
    APP_NAME,
    APP_VERSION,
    BUILD_DATE,
    COMPANY_NAME,
    DEFAULT_USERS,
    OFFICIAL_LOCATIONS,
    SERVER_NAMES,
    SERVER_SHEET_MAP,
    STATUS_OPTIONS,
    TECH_MAP,
)
from config.categories import AI_SUGGESTIONS, CATEGORY_MASTER

__all__ = [
    "APP_NAME",
    "APP_VERSION",
    "BUILD_DATE",
    "COMPANY_NAME",
    "DEFAULT_USERS",
    "OFFICIAL_LOCATIONS",
    "SERVER_NAMES",
    "SERVER_SHEET_MAP",
    "STATUS_OPTIONS",
    "TECH_MAP",
    "CATEGORY_MASTER",
    "AI_SUGGESTIONS",
]
