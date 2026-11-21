"""Shared timezone utilities for Vega IT Ticketing.

Canonical storage rule:
- Store timestamps in UTC (timezone-aware) wherever the database supports it.
- Display timestamps in Asia/Kolkata (IST) for Indian users.

Do not manually add or subtract 5 hours 30 minutes in application code.
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
UTC = timezone.utc


def now_utc() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(UTC)


def now_ist() -> datetime:
    """Return the current timezone-aware IST timestamp."""
    return datetime.now(IST)


def to_ist(value: datetime) -> datetime:
    """Convert a datetime value to IST. Naive values are treated as UTC."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(IST)


def format_ist(value: datetime) -> str:
    """Format a datetime value for display in IST."""
    return to_ist(value).strftime("%d-%b-%Y %I:%M:%S %p IST")


def ist_date(value: datetime) -> str:
    """Return the IST calendar date in ISO format for reporting/filtering."""
    return to_ist(value).date().isoformat()
