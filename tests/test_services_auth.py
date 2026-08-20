"""Unit tests for services.auth (V2 Phase 2c)."""

from __future__ import annotations

import hashlib

from services.auth import (
    get_role_pages,
    hash_password,
    normalize_user_record,
    verify_password,
)


def test_bcrypt_round_trip() -> None:
    stored = hash_password("secret-pass")
    assert stored.startswith(("$2a$", "$2b$", "$2y$"))
    assert verify_password("secret-pass", stored) is True
    assert verify_password("wrong-pass", stored) is False


def test_empty_hash_is_rejected() -> None:
    assert verify_password("secret-pass", "") is False
    assert verify_password("secret-pass", None) is False  # type: ignore[arg-type]


def test_legacy_sha256_verifies_without_upgrade() -> None:
    legacy = hashlib.sha256("secret-pass".encode("utf-8")).hexdigest()
    assert verify_password("secret-pass", legacy) is True
    assert verify_password("wrong-pass", legacy) is False


def test_it_manager_has_admin_tools() -> None:
    pages = get_role_pages("IT Manager")
    assert len(pages) == 13
    assert "Admin Tools" in pages
    assert "Ticket Operations" in pages


def test_avp_does_not_see_admin_tools() -> None:
    pages = get_role_pages("AVP")
    assert "Admin Tools" not in pages
    assert "AVP Dashboard" in pages


def test_default_role_pages_are_limited() -> None:
    pages = get_role_pages("IT Executive")
    assert pages == [
        "Home",
        "Overview",
        "Ticket Operations",
        "NAS Monitoring",
        "Task Center",
        "Team Chat",
    ]


def test_normalize_user_record_maps_supabase_keys() -> None:
    rec = normalize_user_record(
        {
            "id": 1,
            "username": "amit",
            "displayname": "Amit",
            "role": "IT Manager",
            "passwordhash": "hash",
            "active": True,
            "mustchangepassword": False,
        }
    )
    assert rec is not None
    assert rec["username"] == "amit"
    assert rec["display_name"] == "Amit"
    assert rec["password_hash"] == "hash"
    assert rec["active"] == 1
    assert rec["must_change_password"] == 0


def test_normalize_user_record_none() -> None:
    assert normalize_user_record(None) is None
