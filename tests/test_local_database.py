"""Tests for the local SQLite/D1 development adapter."""

from pathlib import Path

import pytest

from db.local_database import LocalDatabase


@pytest.fixture()
def database(tmp_path: Path) -> LocalDatabase:
    database = LocalDatabase(tmp_path / "test_ticketing.db")
    database.initialize("migrations/d1_schema.sql")
    return database


def test_initialize_creates_tables(database: LocalDatabase) -> None:
    tables = database.fetch_all(
        "SELECT name FROM sqlite_schema WHERE type = 'table' ORDER BY name"
    )
    table_names = {row["name"] for row in tables}

    assert "tickets" in table_names
    assert "users" in table_names
    assert "ticket_comments" in table_names
    assert "ticket_attachments" in table_names


def test_create_and_list_ticket(database: LocalDatabase) -> None:
    ticket_id = database.create_ticket(
        title="Test login issue",
        description="User cannot sign in",
        category="Access",
        priority="High",
        created_by="tester@example.com",
        ticket_date="2026-11-24",
        start_time="10:00",
        close_time="11:00",
    )

    tickets = database.list_tickets()

    assert ticket_id > 0
    assert len(tickets) == 1
    assert tickets[0]["title"] == "Test login issue"
    assert tickets[0]["status"] == "Open"


def test_update_ticket_status(database: LocalDatabase) -> None:
    ticket_id = database.create_ticket(title="Test status update")

    assert database.update_ticket_status(ticket_id, "Resolved") is True

    ticket = database.get_ticket(ticket_id)
    assert ticket is not None
    assert ticket["status"] == "Resolved"
