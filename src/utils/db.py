"""
Database utilities for the Asana-like SQLite simulation.

This module centralizes:
- Opening a connection with foreign key enforcement.
- Applying the schema from schema.sql.
- Simple, explicit helpers for bulk inserts that avoid ORMs.

We keep the abstraction thin so that generated SQL remains transparent for
debugging and for AI agents that may inspect queries.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, List, Mapping, Sequence, Tuple

from .config import DB_CONFIG

from pathlib import Path

# BASE_DIR = Path(__file__).resolve().parent.parent.parent
# SCHEMA_PATH = BASE_DIR / "schema.sql"



def _ensure_parent_dir(path: Path) -> None:
    """Ensure the parent directory for the SQLite file exists."""
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    """
    Create a SQLite connection with foreign keys enabled.

    We default to the configured output path so callers don't need to know
    filesystem layout. Using row_factory=sqlite3.Row keeps rows dict-like,
    which makes bulk loading and debugging easier.
    """
    if db_path is None:
        db_path = DB_CONFIG.output_path

    path = Path(db_path)
    _ensure_parent_dir(path)

    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row

    # Enforce referential integrity; this is off by default in SQLite.
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn



def apply_schema(conn):
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    SCHEMA_PATH = BASE_DIR / "schema.sql"

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    conn.commit()



def bulk_insert(
    conn: sqlite3.Connection,
    table: str,
    columns: Sequence[str],
    rows: Iterable[Sequence[object]],
) -> None:
    """
    Perform an efficient bulk insert into a given table.

    We avoid clever abstractions here; explicit column lists make it easy to
    reason about the generated SQL and keep the mapping stable for AI agents.
    """
    if not rows:
        return

    cols_sql = ", ".join(columns)
    placeholders = ", ".join(["?"] * len(columns))
    sql = f"INSERT INTO {table} ({cols_sql}) VALUES ({placeholders})"

    conn.executemany(sql, list(rows))
    conn.commit()


@contextmanager
def db_session(db_path: str | None = None) -> sqlite3.Connection:
    """
    Context manager that yields a connection and ensures it is closed.

    Usage:
        with db_session() as conn:
            apply_schema(conn)
            ...
    """
    conn = get_connection(db_path)
    try:
        yield conn
    finally:
        conn.close()


