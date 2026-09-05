"""SQLite connection and support-table bootstrap (V2)."""

from __future__ import annotations

import sqlite3

from config.settings import DEFAULT_USERS
from db.schema import (
    ASSET_REGISTRY_TABLE_SQL,
    AUTH_SESSIONS_TABLE_SQL,
    CHAT_MESSAGES_TABLE_SQL,
    CHAT_THREADS_TABLE_SQL,
    COMMENTS_TABLE_SQL,
    NOTIFICATIONS_TABLE_SQL,
    TASKS_TABLE_SQL,
    USER_STATUS_TABLE_SQL,
    USERS_TABLE_SQL,
    VENDOR_TABLE_SQL,
)

DB_PATH = "it_ops.db"


def get_db_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_support_tables(conn: sqlite3.Connection) -> None:
    conn.execute(USERS_TABLE_SQL)
    conn.execute(TASKS_TABLE_SQL)
    conn.execute(COMMENTS_TABLE_SQL)
    conn.execute(NOTIFICATIONS_TABLE_SQL)
    conn.execute(VENDOR_TABLE_SQL)
    conn.execute(CHAT_THREADS_TABLE_SQL)
    conn.execute(CHAT_MESSAGES_TABLE_SQL)
    conn.execute(USER_STATUS_TABLE_SQL)
    conn.execute(AUTH_SESSIONS_TABLE_SQL)
    try:
        conn.execute("ALTER TABLE chat_messages ADD COLUMN linked_ticket_id INTEGER")
    except Exception:
        pass
    conn.commit()


def ensure_enterprise_extension_tables(conn: sqlite3.Connection) -> None:
    try:
        conn.execute(ASSET_REGISTRY_TABLE_SQL)
        conn.commit()
    except Exception:
        pass


def _normalize_seed_user(entry) -> tuple:
    """Accept dict or (username, display_name, role[, password]) tuple."""
    if isinstance(entry, dict):
        username = str(entry.get("username", "")).strip()
        display_name = str(entry.get("display_name") or username).strip()
        role = str(entry.get("role") or "User").strip()
        password = entry.get("password") or "ChangeMe123!"
        return username, display_name, role, password
    if isinstance(entry, (list, tuple)):
        if len(entry) >= 4:
            return str(entry[0]), str(entry[1]), str(entry[2]), str(entry[3])
        if len(entry) == 3:
            return str(entry[0]), str(entry[1]), str(entry[2]), "ChangeMe123!"
    raise ValueError(f"Invalid DEFAULT_USERS entry: {entry!r}")


def seed_default_users(conn: sqlite3.Connection) -> None:
    from services.auth import hash_password

    cur = conn.cursor()
    for entry in DEFAULT_USERS:
        username, display_name, role, password = _normalize_seed_user(entry)
        if not username:
            continue
        cur.execute("SELECT id FROM users WHERE lower(username)=lower(?)", (username,))
        if cur.fetchone() is None:
            pw_hash = hash_password(password)
            cur.execute(
                "INSERT INTO users (username, display_name, role, password_hash, active, must_change_password) "
                "VALUES (?, ?, ?, ?, 1, 1)",
                (username, display_name, role, pw_hash),
            )
        cur.execute(
            "SELECT username FROM user_status WHERE lower(username)=lower(?)",
            (username,),
        )
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO user_status (username, display_name, status) VALUES (?, ?, ?)",
                (username, display_name, "Available"),
            )
    conn.commit()


def init_support_data(conn: sqlite3.Connection) -> None:
    ensure_support_tables(conn)
    ensure_enterprise_extension_tables(conn)
    seed_default_users(conn)
