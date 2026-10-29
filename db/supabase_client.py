"""Supabase client helpers (tickets + NAS)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

try:
    from supabase import create_client
except Exception:  # pragma: no cover
    create_client = None  # type: ignore


def _secrets_file_exists() -> bool:
    """True only if a secrets.toml is present (do not call st.secrets first)."""
    candidates = [
        Path.cwd() / ".streamlit" / "secrets.toml",
        Path.home() / ".streamlit" / "secrets.toml",
    ]
    # Also check project-relative when cwd differs
    try:
        here = Path(__file__).resolve().parent.parent
        candidates.append(here / ".streamlit" / "secrets.toml")
    except Exception:
        pass
    return any(p.is_file() for p in candidates)


def _get_supabase_credentials() -> tuple[str, str]:
    """Read url/key from secrets; empty if no file or keys missing."""
    if not _secrets_file_exists():
        return "", ""
    try:
        if "supabase" not in st.secrets:
            return "", ""
        block = st.secrets["supabase"]
        url = str(block.get("url", "") or "").strip()
        key = str(block.get("key", "") or "").strip()
        return url, key
    except Exception:
        return "", ""


@st.cache_resource
def init_supabase() -> Any:
    if create_client is None:
        return None
    url, key = _get_supabase_credentials()
    if not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None


def get_supabase_client() -> Any:
    return init_supabase()


def is_db_connected() -> bool:
    try:
        return get_supabase_client() is not None
    except Exception:
        return False


def table_exists(name: str) -> bool:
    client = get_supabase_client()
    if client is None:
        return False
    try:
        client.table(name).select("id", count="exact").limit(1).execute()
        return True
    except Exception:
        return False
