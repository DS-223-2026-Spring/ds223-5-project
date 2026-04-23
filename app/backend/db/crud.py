from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from sqlalchemy import RowMapping, text
from sqlalchemy.engine import Engine

from db.connection import get_engine, wait_for_db


_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _validate_identifier(name: str) -> str:
    """Validate a SQL identifier to prevent SQL injection.

    Args:
        name: Table or column name.

    Returns:
        The same name if valid.

    Raises:
        ValueError: If the identifier is invalid.
    """
    if not _IDENTIFIER_RE.fullmatch(name):
        raise ValueError(f"Invalid SQL identifier: {name!r}")
    return name


def _q(name: str) -> str:
    """Quote a validated SQL identifier for Postgres."""
    return f"\"{_validate_identifier(name)}\""


def insert_one(
    table: str,
    data: Mapping[str, Any],
    *,
    engine: Optional[Engine] = None,
    returning: Sequence[str] = ("id",),
) -> Dict[str, Any]:
    """Insert a single row and return selected columns.

    Args:
        table: Target table name.
        data: Column/value mapping.
        engine: Optional SQLAlchemy engine.
        returning: Columns to return (default: `("id",)`).

    Returns:
        A dict containing the returned columns.
    """
    if not data:
        raise ValueError("insert_one requires non-empty data")

    eng = engine or get_engine()
    wait_for_db(eng)

    cols = list(data.keys())
    col_sql = ", ".join(_q(c) for c in cols)
    val_sql = ", ".join(f":{c}" for c in cols)
    ret_sql = ", ".join(_q(c) for c in returning) if returning else ""

    sql = f"INSERT INTO {_q(table)} ({col_sql}) VALUES ({val_sql})"
    if ret_sql:
        sql += f" RETURNING {ret_sql}"

    with eng.begin() as conn:
        res = conn.execute(text(sql), dict(data))
        row = res.mappings().first()
        return dict(row) if row is not None else {}


def select_many(
    table: str,
    *,
    where: Optional[Mapping[str, Any]] = None,
    columns: Sequence[str] = ("*",),
    order_by: Optional[Sequence[Tuple[str, str]]] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    engine: Optional[Engine] = None,
) -> List[RowMapping]:
    """Select rows from a table.

    Args:
        table: Table name.
        where: Optional equality filters (ANDed together).
        columns: Columns to fetch (use `("*",)` for all).
        order_by: Optional list of (column, direction) where direction is `ASC`/`DESC`.
        limit: Optional row limit.
        offset: Optional row offset.
        engine: Optional SQLAlchemy engine.

    Returns:
        Rows as SQLAlchemy `RowMapping` objects.
    """
    eng = engine or get_engine()
    wait_for_db(eng)

    params: Dict[str, Any] = {}
    if columns == ("*",):
        col_sql = "*"
    else:
        col_sql = ", ".join(_q(c) for c in columns)

    sql = f"SELECT {col_sql} FROM {_q(table)}"

    if where:
        parts = []
        for i, (k, v) in enumerate(where.items()):
            _validate_identifier(k)
            param = f"w_{i}"
            parts.append(f"{_q(k)} = :{param}")
            params[param] = v
        sql += " WHERE " + " AND ".join(parts)

    if order_by:
        order_parts = []
        for col, direction in order_by:
            _validate_identifier(col)
            dir_up = direction.upper()
            if dir_up not in {"ASC", "DESC"}:
                raise ValueError("order_by direction must be 'ASC' or 'DESC'")
            order_parts.append(f"{_q(col)} {dir_up}")
        sql += " ORDER BY " + ", ".join(order_parts)

    if limit is not None:
        sql += " LIMIT :limit"
        params["limit"] = int(limit)
    if offset is not None:
        sql += " OFFSET :offset"
        params["offset"] = int(offset)

    with eng.connect() as conn:
        res = conn.execute(text(sql), params)
        return list(res.mappings().all())


def update_many(
    table: str,
    data: Mapping[str, Any],
    *,
    where: Mapping[str, Any],
    engine: Optional[Engine] = None,
) -> int:
    """Update rows in a table.

    Args:
        table: Table name.
        data: Columns to update.
        where: Equality filters (ANDed together). Must be non-empty.
        engine: Optional SQLAlchemy engine.

    Returns:
        Number of updated rows.
    """
    if not data:
        raise ValueError("update_many requires non-empty data")
    if not where:
        raise ValueError("update_many requires non-empty where clause")

    eng = engine or get_engine()
    wait_for_db(eng)

    params: Dict[str, Any] = {}
    set_parts = []
    for i, (k, v) in enumerate(data.items()):
        _validate_identifier(k)
        p = f"s_{i}"
        set_parts.append(f"{_q(k)} = :{p}")
        params[p] = v

    where_parts = []
    for i, (k, v) in enumerate(where.items()):
        _validate_identifier(k)
        p = f"w_{i}"
        where_parts.append(f"{_q(k)} = :{p}")
        params[p] = v

    sql = f"UPDATE {_q(table)} SET " + ", ".join(set_parts) + " WHERE " + " AND ".join(where_parts)
    with eng.begin() as conn:
        res = conn.execute(text(sql), params)
        return int(res.rowcount or 0)


def delete_many(
    table: str,
    *,
    where: Mapping[str, Any],
    engine: Optional[Engine] = None,
) -> int:
    """Delete rows from a table.

    Args:
        table: Table name.
        where: Equality filters (ANDed together). Must be non-empty.
        engine: Optional SQLAlchemy engine.

    Returns:
        Number of deleted rows.
    """
    if not where:
        raise ValueError("delete_many requires non-empty where clause")

    eng = engine or get_engine()
    wait_for_db(eng)

    params: Dict[str, Any] = {}
    where_parts = []
    for i, (k, v) in enumerate(where.items()):
        _validate_identifier(k)
        p = f"w_{i}"
        where_parts.append(f"{_q(k)} = :{p}")
        params[p] = v

    sql = f"DELETE FROM {_q(table)} WHERE " + " AND ".join(where_parts)
    with eng.begin() as conn:
        res = conn.execute(text(sql), params)
        return int(res.rowcount or 0)

