from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from sqlalchemy import text
from sqlalchemy.engine import Engine

from db.connection import get_engine, wait_for_db
from db.crud import insert_one


def _read_json_records(path: Path) -> List[Dict[str, Any]]:
    """Read a JSON file containing either a list of objects or a dict with a `records` list."""
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if isinstance(payload, list):
        return [r for r in payload if isinstance(r, dict)]
    if isinstance(payload, dict) and isinstance(payload.get("records"), list):
        return [r for r in payload["records"] if isinstance(r, dict)]
    raise ValueError("JSON must be a list of objects or an object with a 'records' list")


def _read_csv_records(path: Path) -> List[Dict[str, Any]]:
    """Read a CSV file into a list of dict records."""
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def _table_columns(engine: Engine, table: str, schema: str = "public") -> Dict[str, str]:
    """Return column_name -> data_type for a table using information_schema."""
    sql = text(
        """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = :schema AND table_name = :table
        ORDER BY ordinal_position
        """
    )
    with engine.connect() as conn:
        rows = conn.execute(sql, {"schema": schema, "table": table}).mappings().all()
    return {r["column_name"]: r["data_type"] for r in rows}


def _row_count(engine: Engine, table: str) -> int:
    """Return SELECT COUNT(*) for a table."""
    with engine.connect() as conn:
        return int(conn.execute(text(f'SELECT COUNT(*) AS c FROM "{table}"')).mappings().one()["c"])


def load_flat_file(
    *,
    table: str,
    path: str | Path,
    engine: Optional[Engine] = None,
    json_format_tags_field: str = "content_formats",
) -> Dict[str, Any]:
    """Load a CSV/JSON file into a table and validate row counts + schema shape.

    This loader is intentionally lightweight and expects the flat-file keys to match
    database column names (excluding generated columns like `id`, `created_at`).

    Args:
        table: Target database table.
        path: Path to a `.csv` or `.json` file.
        engine: Optional SQLAlchemy engine; defaults to `get_engine()`.
        json_format_tags_field: If present in JSON/CSV and the value is a JSON string or list,
            it will be normalized to a comma-separated string (to match ERD `TEXT`).

    Returns:
        A dict with load summary and validation results.
    """
    eng = engine or get_engine()
    wait_for_db(eng)

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(str(p))

    if p.suffix.lower() == ".json":
        records = _read_json_records(p)
    elif p.suffix.lower() == ".csv":
        records = _read_csv_records(p)
    else:
        raise ValueError("Only .csv and .json files are supported")

    before = _row_count(eng, table)
    cols = _table_columns(eng, table)

    inserted = 0
    for record in records:
        # Basic schema consistency check: incoming keys must be subset of table columns
        unknown = [k for k in record.keys() if k not in cols]
        if unknown:
            raise ValueError(f"Record contains unknown columns for table '{table}': {unknown}")

        # Normalize array-like field to comma-separated string (common in exports).
        if json_format_tags_field in record:
            val = record[json_format_tags_field]
            if isinstance(val, str):
                raw = val.strip()
                if raw.startswith("[") and raw.endswith("]"):
                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        record[json_format_tags_field] = ", ".join(str(x) for x in parsed)
            elif isinstance(val, list):
                record[json_format_tags_field] = ", ".join(str(x) for x in val)

        insert_one(table, record, engine=eng, returning=())
        inserted += 1

    after = _row_count(eng, table)

    return {
        "table": table,
        "file": str(p),
        "source_rows": len(records),
        "inserted_rows": inserted,
        "db_rows_before": before,
        "db_rows_after": after,
        "row_count_match": (after - before) == len(records),
        "table_columns": cols,
    }

