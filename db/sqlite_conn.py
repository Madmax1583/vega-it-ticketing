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


def seed_default_users(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    for username, display_name, role in DEFAULT_USERS:
        cur.execute("SELECT id FROM users WHERE lower(username)=lower(?)", (username,))
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO users (username, display_name, role, password_hash, active, must_change_password) VALUES (?, ?, ?, ?, 1, 1)",
                (username, display_name, role, None),
            )
        cur.execute("SELECT username FROM user_status WHERE lower(username)=lower(?)", (username,))
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
