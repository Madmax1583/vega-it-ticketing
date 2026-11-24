"""Database access layer for Vega Ticketing.

This package is the local Cloudflare D1 / SQLite migration scaffold.
"""

from .local_database import LocalDatabase

__all__ = ["LocalDatabase"]
