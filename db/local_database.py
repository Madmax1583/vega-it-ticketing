"""Local SQLite database adapter for Cloudflare D1 development.

This adapter is intentionally separate from the Streamlit UI so that the
application can later use either a local SQLite database or Cloudflare D1
without changing business logic.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

DEFAULT_DB_PATH = Path("data") / "vega_ticketing_local.db"


class LocalDatabase:
    """Small SQLite adapter used for local Vega Ticketing development."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def execute(self, sql: str, parameters: tuple[Any, ...] = ()) -> None:
        with self.connect() as connection:
            connection.execute(sql, parameters)

    def executescript(self, sql_script: str) -> None:
        with self.connect() as connection:
            connection.executescript(sql_script)

    def fetch_all(
        self,
        sql: str,
        parameters: tuple[Any, ...] = (),
    ) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(sql, parameters).fetchall()
            return [dict(row) for row in rows]

    def fetch_one(
        self,
        sql: str,
        parameters: tuple[Any, ...] = (),
    ) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(sql, parameters).fetchone()
            return dict(row) if row else None

    def initialize(self, schema_path: str | Path = "migrations/d1_schema.sql") -> None:
        schema = Path(schema_path).read_text(encoding="utf-8")
        self.executescript(schema)

    def create_ticket(
        self,
        *,
        title: str,
        description: str | None = None,
        category: str | None = None,
        priority: str | None = None,
        status: str = "Open",
        assigned_to: str | None = None,
        created_by: str | None = None,
        ticket_date: str | None = None,
        start_time: str | None = None,
        close_time: str | None = None,
    ) -> int:
        sql = """
            INSERT INTO tickets (
                title, description, category, priority, status,
                assigned_to, created_by, ticket_date, start_time, close_time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        parameters = (
            title,
            description,
            category,
            priority,
            status,
            assigned_to,
            created_by,
            ticket_date,
            start_time,
            close_time,
        )
        with self.connect() as connection:
            cursor = connection.execute(sql, parameters)
            return int(cursor.lastrowid)

    def list_tickets(self, status: str | None = None) -> list[dict[str, Any]]:
        if status:
            return self.fetch_all(
                "SELECT * FROM tickets WHERE status = ? ORDER BY created_at DESC",
                (status,),
            )
        return self.fetch_all("SELECT * FROM tickets ORDER BY created_at DESC")

    def get_ticket(self, ticket_id: int) -> dict[str, Any] | None:
        return self.fetch_one("SELECT * FROM tickets WHERE id = ?", (ticket_id,))

    def update_ticket_status(self, ticket_id: int, status: str) -> bool:
        with self.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE tickets
                SET status = ?, updated_at = datetime('now')
                WHERE id = ?
                """,
                (status, ticket_id),
            )
            return cursor.rowcount > 0
