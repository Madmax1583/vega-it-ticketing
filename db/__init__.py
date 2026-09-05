"""Database access package (SQLite auth/ops + Supabase tickets/NAS)."""

from db.sqlite_conn import (
    get_db_connection,
    ensure_support_tables,
    ensure_enterprise_extension_tables,
    init_support_data,
    seed_default_users,
)
from db.supabase_client import init_supabase, get_supabase_client, is_db_connected, table_exists

__all__ = [
    "get_db_connection",
    "ensure_support_tables",
    "ensure_enterprise_extension_tables",
    "init_support_data",
    "seed_default_users",
    "init_supabase",
    "get_supabase_client",
    "is_db_connected",
    "table_exists",
]
