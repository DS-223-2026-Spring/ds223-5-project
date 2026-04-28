"""Publish DS model metrics into Postgres.

Issue: M3 DS outputs requirement.

This script reads the DS team's baseline metrics CSV and upserts rows into
`ds_model_metrics` via the SQL function `upsert_ds_model_metric(...)`.

Expected CSV columns (see `app/ds/outputs/baseline_model_comparison.csv`):
  - model
  - accuracy
  - f1
  - precision
  - recall

Usage:
  python app/db/tools/publish_ds_metrics.py --csv app/ds/outputs/baseline_model_comparison.csv
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict

from db_client import connect_with_retry


def _parse_row(row: Dict[str, str]) -> Dict[str, object]:
    """Parse and type-cast a metrics CSV row.

    Args:
        row: Raw CSV row mapping.

    Returns:
        Parsed row with numeric fields converted.

    Raises:
        KeyError: If required columns are missing.
        ValueError: If numeric conversions fail.
    """
    return {
        "model": row["model"],
        "accuracy": float(row["accuracy"]),
        "f1": float(row["f1"]),
        "precision": float(row["precision"]),
        "recall": float(row["recall"]),
    }


def publish_metrics(csv_path: Path) -> int:
    """Upsert all metrics rows from a CSV into the database.

    Args:
        csv_path: Path to baseline model comparison CSV.

    Returns:
        Number of upserted rows.
    """
    if not csv_path.exists():
        raise FileNotFoundError(str(csv_path))

    upserted = 0
    conn = connect_with_retry()
    try:
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            with conn, conn.cursor() as cur:
                for raw in reader:
                    parsed = _parse_row(raw)
                    cur.execute(
                        "SELECT upsert_ds_model_metric(%s, %s, %s, %s, %s, NOW());",
                        (
                            parsed["model"],
                            parsed["accuracy"],
                            parsed["f1"],
                            parsed["precision"],
                            parsed["recall"],
                        ),
                    )
                    upserted += 1
        return upserted
    finally:
        conn.close()


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("app/ds/outputs/baseline_model_comparison.csv"),
        help="Path to baseline_model_comparison.csv",
    )
    args = parser.parse_args()
    count = publish_metrics(args.csv)
    print(f"Upserted {count} model metric rows into ds_model_metrics.")


if __name__ == "__main__":
    main()

