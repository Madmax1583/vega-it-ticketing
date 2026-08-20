"""Supabase client helpers (tickets + NAS)."""

from __future__ import annotations

from typing import Any

import streamlit as st

try:
    from supabase import create_client
except Exception:  # pragma: no cover
    create_client = None  # type: ignore


def _secrets_available() -> bool:
    """Return True if Streamlit secrets can be read (file may be missing)."""
    try:
        _ = st.secrets
        return True
    except Exception:
        return False


def _get_supabase_credentials() -> tuple[str, str]:
    """Read url/key from secrets; empty strings if missing."""
    if not _secrets_available():
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
