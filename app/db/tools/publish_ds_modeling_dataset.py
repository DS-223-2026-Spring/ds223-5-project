"""Publish DS modeling dataset snapshot into Postgres.

Milestone 3 DB task: store DS outputs in the database.

This script reads `app/ds/outputs/modeling_dataset.csv` from the DS pipeline and upserts
rows into `ds_modeling_dataset`. Column names are preserved exactly as produced by DS.

Expected CSV columns:
  - name
  - niche
  - follower_count
  - engagement_rate
  - location
  - campaign_conversions
  - synthetic_data
  - target_high_performer

Upsert key:
  - (name, location)

Usage:
  python app/db/tools/publish_ds_modeling_dataset.py --csv app/ds/outputs/modeling_dataset.csv
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from db_client import connect_with_retry


def _parse_bool(value: str) -> bool:
    """Parse common boolean encodings used in CSVs."""
    v = value.strip().lower()
    if v in {"true", "1", "t", "yes", "y"}:
        return True
    if v in {"false", "0", "f", "no", "n"}:
        return False
    raise ValueError(f"Invalid boolean: {value!r}")


def _parse_row(row: Dict[str, str]) -> Dict[str, object]:
    """Parse and type-cast a modeling dataset CSV row."""
    return {
        "name": row["name"],
        "niche": row["niche"],
        "follower_count": int(row["follower_count"]),
        "engagement_rate": float(row["engagement_rate"]),
        "location": row["location"],
        "campaign_conversions": int(row["campaign_conversions"]),
        "synthetic_data": _parse_bool(row["synthetic_data"]),
        "target_high_performer": int(row["target_high_performer"]),
    }


def publish_modeling_dataset(csv_path: Path) -> int:
    """Upsert rows from the DS modeling dataset CSV into Postgres.

    Args:
        csv_path: Path to the DS `modeling_dataset.csv`.

    Returns:
        The number of processed rows.
    """
    if not csv_path.exists():
        raise FileNotFoundError(str(csv_path))

    conn = connect_with_retry()
    try:
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows = [_parse_row(r) for r in reader]

        with conn, conn.cursor() as cur:
            for r in rows:
                cur.execute(
                    """
                    INSERT INTO ds_modeling_dataset (
                      name, niche, follower_count, engagement_rate, location,
                      campaign_conversions, synthetic_data, target_high_performer, written_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (name, location) DO UPDATE SET
                      niche = EXCLUDED.niche,
                      follower_count = EXCLUDED.follower_count,
                      engagement_rate = EXCLUDED.engagement_rate,
                      campaign_conversions = EXCLUDED.campaign_conversions,
                      synthetic_data = EXCLUDED.synthetic_data,
                      target_high_performer = EXCLUDED.target_high_performer,
                      written_at = EXCLUDED.written_at;
                    """,
                    (
                        r["name"],
                        r["niche"],
                        r["follower_count"],
                        r["engagement_rate"],
                        r["location"],
                        r["campaign_conversions"],
                        r["synthetic_data"],
                        r["target_high_performer"],
                    ),
                )
        return len(rows)
    finally:
        conn.close()


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("app/ds/outputs/modeling_dataset.csv"),
        help="Path to modeling_dataset.csv",
    )
    args = parser.parse_args()
    count = publish_modeling_dataset(args.csv)
    print(f"Upserted {count} rows into ds_modeling_dataset.")


if __name__ == "__main__":
    main()

