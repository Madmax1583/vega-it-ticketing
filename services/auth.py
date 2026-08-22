"""Authentication helpers (V2 Phase 1).

SQLite-backed users, bcrypt hashing, legacy SHA-256 upgrade path.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional

import bcrypt

from config.settings import ROLE_PAGES, SESSION_HOURS


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, stored: str) -> bool:
    if not stored:
        return False
    stored = str(stored)
    # bcrypt
    if stored.startswith("$2"):
        try:
            return bcrypt.checkpw(plain.encode("utf-8"), stored.encode("utf-8"))
        except Exception:
            return False
    # legacy SHA-256 (hex)
    if len(stored) == 64:
        digest = hashlib.sha256(plain.encode("utf-8")).hexdigest()
        return digest == stored.lower()
    return False


def get_role_pages(role: str) -> list:
    return list(ROLE_PAGES.get(role, ROLE_PAGES.get("User", ["Home"])))


def get_all_users(conn) -> list:
    if conn is None:
        return []
    cur = conn.execute(
        "SELECT id, username, display_name, role, must_change_password FROM users ORDER BY username"
    )
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in rows]


def get_user_by_username(conn, username: str) -> Optional[dict]:
    if conn is None or not username:
        return None
    cur = conn.execute(
        "SELECT id, username, display_name, role, password_hash, must_change_password "
        "FROM users WHERE lower(username) = lower(?)",
        (username.strip(),),
    )
    row = cur.fetchone()
    if not row:
        return None
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, row))


def authenticate_user(conn, username: str, password: str) -> Optional[dict]:
    """Validate credentials. Upgrades legacy SHA-256 hashes to bcrypt on success."""
    user = get_user_by_username(conn, username)
    if not user:
        return None
    stored = user.get("password_hash") or ""
    if not verify_password(password, stored):
        return None
    # Upgrade legacy hash
    if stored and not str(stored).startswith("$2"):
        try:
            new_hash = hash_password(password)
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (new_hash, user["id"]),
            )
            conn.commit()
            user["password_hash"] = new_hash
        except Exception:
            pass
    # Strip hash before returning to session
    safe = {k: v for k, v in user.items() if k != "password_hash"}
    safe["must_change_password"] = bool(safe.get("must_change_password"))
    return safe


def set_first_password(conn, username: str, new_password: str) -> None:
    if conn is None:
        raise RuntimeError("No database connection")
    if len(new_password) < 8:
        raise ValueError("Password must be at least 8 characters")
    user = get_user_by_username(conn, username)
    if not user:
        raise ValueError("User not found")
    new_hash = hash_password(new_password)
    conn.execute(
        "UPDATE users SET password_hash = ?, must_change_password = 0 WHERE id = ?",
        (new_hash, user["id"]),
    )
    conn.commit()


def bcrypt_roundtrip_ok() -> bool:
    h = hash_password("test-password-only")
    return verify_password("test-password-only", h)
