"""
Auth domain service (V2 Phase 2b).

Password hashing (bcrypt + legacy SHA256 upgrade), user lookup,
password set, and role-based page maps.
SQLite is the primary auth store; Supabase users table is optional.
"""

from __future__ import annotations

import hashlib
from typing import Any, Optional

import bcrypt
import pandas as pd

from db.supabase_client import get_supabase_client, is_db_connected, table_exists

DEFAULT_USERS = [
    ("amit", "Amit", "IT Manager"),
    ("satish", "Satish", "IT AM"),
    ("ranjan", "Ranjan", "Sr. Executive"),
    ("priyanshu", "Priyanshu", "IT Executive"),
    ("manish", "Manish", "IT Executive"),
    ("satender", "Mr. Satender Vashisht", "AVP"),
]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(
    password: str,
    stored_hash: str,
    conn: Any = None,
    username: Optional[str] = None,
) -> bool:
    if not stored_hash:
        return False
    try:
        stored_hash = str(stored_hash)
        if stored_hash.startswith(("$2a$", "$2b$", "$2y$")):
            return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
        legacy_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        if legacy_hash == stored_hash:
            if conn is not None and username:
                upgraded = hash_password(password)
                conn.execute(
                    "UPDATE users SET password_hash=?, updated_at=CURRENT_TIMESTAMP WHERE lower(username)=lower(?)",
                    (upgraded, username),
                )
                conn.commit()
            return True
    except Exception:
        return False
    return False


def normalize_user_record(user: Optional[dict]) -> Optional[dict]:
    if not user:
        return None

    def as_flag(value: Any, default: bool = False) -> int:
        if value is None:
            return 1 if default else 0
        if isinstance(value, bool):
            return 1 if value else 0
        s = str(value).strip().lower()
        if s in {"1", "true", "yes", "y", "active"}:
            return 1
        if s in {"0", "false", "no", "n", "inactive"}:
            return 0
        return 1 if default else 0

    active_val = user.get("active", user.get("is_active", True))
    must_change_val = user.get(
        "mustchangepassword",
        user.get("must_change_password", user.get("must_change", False)),
    )
    return {
        "id": user.get("id"),
        "username": str(user.get("username", user.get("user_name", ""))).strip(),
        "display_name": (
            user.get("displayname")
            or user.get("display_name")
            or user.get("name")
            or str(user.get("username", user.get("user_name", ""))).strip().title()
        ),
        "role": user.get("role", "User"),
        "password_hash": user.get("passwordhash") or user.get("password_hash") or user.get("password"),
        "active": as_flag(active_val, default=True),
        "must_change_password": as_flag(must_change_val, default=False),
    }


def get_user_by_username_sqlite(conn: Any, username: str) -> Optional[dict]:
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, display_name, role, password_hash, active, must_change_password "
        "FROM users WHERE lower(username)=lower(?)",
        (username,),
    )
    row = cur.fetchone()
    if not row:
        return None
    return {k: row[k] for k in row.keys()}


def get_user_by_username(conn: Any, username: str) -> Optional[dict]:
    clean = str(username).strip()
    if is_db_connected() and table_exists("users"):
        client = get_supabase_client()
        try:
            response = client.table("users").select("*").ilike("username", clean).limit(1).execute()
            if response.data:
                return normalize_user_record(response.data[0])
        except Exception:
            try:
                response = client.table("users").select("*").ilike("user_name", clean).limit(1).execute()
                if response.data:
                    return normalize_user_record(response.data[0])
            except Exception:
                pass
    return get_user_by_username_sqlite(conn, clean)


def set_user_password_sqlite(conn: Any, username: str, new_password: str, require_change: int = 0) -> None:
    conn.execute(
        "UPDATE users SET password_hash=?, must_change_password=?, updated_at=CURRENT_TIMESTAMP WHERE lower(username)=lower(?)",
        (hash_password(new_password), int(require_change), username),
    )
    conn.commit()


def set_user_password(conn: Any, username: str, new_password: str, require_change: int = 0) -> None:
    clean = str(username).strip()
    payload = {
        "passwordhash": hash_password(new_password),
        "mustchangepassword": bool(require_change),
    }
    if is_db_connected() and table_exists("users"):
        client = get_supabase_client()
        try:
            client.table("users").update(payload).ilike("username", clean).execute()
            return
        except Exception:
            try:
                client.table("users").update(payload).ilike("user_name", clean).execute()
                return
            except Exception:
                pass
    set_user_password_sqlite(conn, clean, new_password, require_change=require_change)


def authenticate_user(conn: Any, username: str, password: str) -> Optional[dict]:
    user = get_user_by_username(conn, username)
    if not user or int(user.get("active", 0) or 0) != 1:
        return None
    stored_hash = user.get("password_hash")
    if not stored_hash:
        return None
    if verify_password(password, stored_hash, conn=conn, username=username):
        return get_user_by_username(conn, username) or user
    return None


def get_all_users(conn: Any) -> pd.DataFrame:
    if is_db_connected() and table_exists("users"):
        client = get_supabase_client()
        try:
            rows = client.table("users").select("*").execute()
            data = rows.data or []
            return pd.DataFrame([normalize_user_record(r) for r in data if normalize_user_record(r)])
        except Exception:
            pass
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, display_name, role, password_hash, active, must_change_password FROM users ORDER BY username"
    )
    rows = cur.fetchall()
    return pd.DataFrame([{k: row[k] for k in row.keys()} for row in rows])


def get_role_pages(role: str) -> list[str]:
    if role == "IT Manager":
        return [
            "Home", "Executive Command Center", "Overview", "Ticket Operations",
            "NAS Monitoring", "Reports", "Task Center", "Admin Tools", "AVP Dashboard",
            "Team Chat", "Vendor Dashboard", "Department Health", "Asset Health",
        ]
    if role == "IT AM":
        return [
            "Home", "Executive Command Center", "Overview", "Ticket Operations",
            "NAS Monitoring", "Reports", "Task Center", "Team Chat",
            "Vendor Dashboard", "Department Health", "Asset Health",
        ]
    if role == "AVP":
        return [
            "Home", "Executive Command Center", "Overview", "AVP Dashboard",
            "Reports", "Task Center", "Team Chat", "Vendor Dashboard",
            "Department Health", "Asset Health",
        ]
    return ["Home", "Overview", "Ticket Operations", "NAS Monitoring", "Task Center", "Team Chat"]


def seed_default_users(conn: Any) -> None:
    cur = conn.cursor()
    for username, display_name, role in DEFAULT_USERS:
        cur.execute("SELECT id FROM users WHERE lower(username)=lower(?)", (username,))
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO users (username, display_name, role, password_hash, active, must_change_password) VALUES (?, ?, ?, ?, 1, 1)",
                (username, display_name, role, None),
            )
        try:
            cur.execute("SELECT username FROM user_status WHERE lower(username)=lower(?)", (username,))
            if cur.fetchone() is None:
                cur.execute(
                    "INSERT INTO user_status (username, display_name, status) VALUES (?, ?, ?)",
                    (username, display_name, "Available"),
                )
        except Exception:
            pass
    conn.commit()
