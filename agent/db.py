"""
agent/db.py
Database connector — supports PostgreSQL and MySQL via SQLAlchemy.
Handles connection, schema introspection, and safe query execution.
"""

import os
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

_engine = None


def get_engine():
    """Return a cached SQLAlchemy engine."""
    global _engine
    if _engine is None:
        db_url = os.getenv("DB_URL")
        if not db_url:
            raise ValueError("DB_URL is not set in your .env file.")
        _engine = create_engine(db_url, pool_pre_ping=True)
    return _engine


def get_schema() -> dict[str, list[str]]:
    """
    Introspect the connected database and return a dict of
    { table_name: [column_name, ...] } for every user table.
    """
    engine = get_engine()
    insp = inspect(engine)
    schema: dict[str, list[str]] = {}

    for table_name in insp.get_table_names():
        columns = insp.get_columns(table_name)
        schema[table_name] = [col["name"] for col in columns]

    return schema


def get_schema_detailed() -> dict[str, list[dict]]:
    """
    Return detailed schema info including column types and nullability.
    Used for richer LLM context.
    """
    engine = get_engine()
    insp = inspect(engine)
    schema: dict[str, list[dict]] = {}

    for table_name in insp.get_table_names():
        columns = insp.get_columns(table_name)
        schema[table_name] = [
            {
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col.get("nullable", True),
            }
            for col in columns
        ]

    return schema


def _is_safe_query(sql: str) -> bool:
    """
    Reject any SQL that is not a SELECT statement.
    A simple but effective guard against destructive queries.
    """
    normalized = sql.strip().lstrip(";").upper()
    allow_write = os.getenv("ALLOW_WRITE", "false").lower() == "true"

    if allow_write:
        return True

    unsafe_keywords = ("INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
                       "TRUNCATE", "CREATE", "REPLACE", "GRANT", "REVOKE")
    for kw in unsafe_keywords:
        if normalized.startswith(kw) or f" {kw} " in normalized:
            return False

    return normalized.startswith("SELECT") or normalized.startswith("WITH")


def run_query(sql: str, max_rows: int | None = None) -> pd.DataFrame:
    """
    Execute a SQL query and return results as a pandas DataFrame.
    Raises ValueError for unsafe (non-SELECT) queries.
    Raises RuntimeError on database errors.
    """
    if max_rows is None:
        max_rows = int(os.getenv("MAX_ROWS", "500"))

    sql = sql.strip().rstrip(";")

    if not _is_safe_query(sql):
        raise ValueError(
            "Only SELECT queries are allowed. "
            "Set ALLOW_WRITE=true in .env to enable write operations."
        )

    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = result.fetchmany(max_rows)
            df = pd.DataFrame(rows, columns=list(result.keys()))
            return df
    except SQLAlchemyError as e:
        raise RuntimeError(f"Database error: {e}") from e


def test_connection() -> bool:
    """Return True if the database is reachable."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
