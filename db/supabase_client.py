"""Supabase client helpers (tickets + NAS)."""

from __future__ import annotations

from typing import Any, Optional

import streamlit as st

try:
    from supabase import create_client
except Exception:  # pragma: no cover
    create_client = None  # type: ignore


@st.cache_resource
def init_supabase() -> Any:
    if create_client is None:
        return None
    if "supabase" not in st.secrets:
        return None
    url = st.secrets["supabase"].get("url", "")
    key = st.secrets["supabase"].get("key", "")
    if not url or not key:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None


def get_supabase_client() -> Any:
    return init_supabase()


def is_db_connected() -> bool:
    return get_supabase_client() is not None


def table_exists(name: str) -> bool:
    client = get_supabase_client()
    if client is None:
        return False
    try:
        client.table(name).select("id", count="exact").limit(1).execute()
        return True
    except Exception:
        return False
