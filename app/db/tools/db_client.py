"""PostgreSQL connection helpers for db tools.

This module is intentionally standalone and only used by scripts in `app/db/tools/`.
It provides:
  - Environment-driven configuration (DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD)
  - Retry logic for transient startup failures

Notes:
  - These helpers use `psycopg2` directly to stay lightweight.
  - The main backend already manages its own DB connection layer; this module is for tools only.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PgConfig:
    """Postgres connection settings for tool scripts.

    Attributes:
        host: Postgres hostname.
        port: Postgres port.
        dbname: Database name.
        user: Database user.
        password: Database password.
    """

    host: str
    port: int
    dbname: str
    user: str
    password: str

    @staticmethod
    def from_env() -> "PgConfig":
        """Build config from environment variables."""
        return PgConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            dbname=os.getenv("DB_NAME", os.getenv("POSTGRES_DB", "imp")),
            user=os.getenv("DB_USER", os.getenv("POSTGRES_USER", "imp_user")),
            password=os.getenv("DB_PASSWORD", os.getenv("POSTGRES_PASSWORD", "imp_password")),
        )


def connect_with_retry(
    *,
    config: Optional[PgConfig] = None,
    timeout_s: int = 60,
    initial_delay_s: float = 0.5,
    max_delay_s: float = 5.0,
):
    """Connect to Postgres with retries.

    Args:
        config: Optional `PgConfig`. If omitted, reads from environment variables.
        timeout_s: Maximum time to keep retrying.
        initial_delay_s: First sleep delay between retries.
        max_delay_s: Upper bound for exponential backoff delay.

    Returns:
        A live psycopg2 connection.

    Raises:
        TimeoutError: If unable to connect within the timeout.
    """
    cfg = config or PgConfig.from_env()

    try:
        import psycopg2  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "psycopg2 is required for db tools. Install it (e.g., psycopg2-binary)."
        ) from exc

    deadline = time.time() + timeout_s
    delay = initial_delay_s
    last_exc: Optional[Exception] = None

    while time.time() < deadline:
        try:
            return psycopg2.connect(
                host=cfg.host,
                port=cfg.port,
                dbname=cfg.dbname,
                user=cfg.user,
                password=cfg.password,
            )
        except Exception as exc:  # pragma: no cover
            last_exc = exc
            time.sleep(delay)
            delay = min(max_delay_s, delay * 1.5)

    raise TimeoutError("Timed out connecting to Postgres") from last_exc


def health_check() -> bool:
    """Return True if a `SELECT 1` succeeds."""
    try:
        conn = connect_with_retry(timeout_s=5)
        with conn, conn.cursor() as cur:
            cur.execute("SELECT 1;")
        conn.close()
        return True
    except Exception:
        return False

