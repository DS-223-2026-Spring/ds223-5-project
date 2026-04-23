from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import QueuePool
from sqlalchemy import create_engine


@dataclass(frozen=True)
class DatabaseConfig:
    """PostgreSQL connection configuration.

    Reads configuration from environment variables exposed in `docker-compose.yml`.

    Attributes:
        host: Database hostname (e.g., `db` when using Docker Compose).
        port: Database port (default 5432).
        name: Database name.
        user: Database user.
        password: Database password.
        connect_timeout_s: Server-side connect timeout.
    """

    host: str
    port: int
    name: str
    user: str
    password: str
    connect_timeout_s: int = 5

    @staticmethod
    def from_env() -> "DatabaseConfig":
        """Create a config from environment variables."""
        return DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            name=os.getenv("DB_NAME", "imp"),
            user=os.getenv("DB_USER", "imp_user"),
            password=os.getenv("DB_PASSWORD", "imp_password"),
            connect_timeout_s=int(os.getenv("DB_CONNECT_TIMEOUT_S", "5")),
        )

    def sqlalchemy_url(self) -> str:
        """Build a SQLAlchemy PostgreSQL URL."""
        return (
            f"postgresql+psycopg2://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
            f"?connect_timeout={self.connect_timeout_s}"
        )


_ENGINE: Optional[Engine] = None


def get_engine(config: Optional[DatabaseConfig] = None) -> Engine:
    """Get a singleton SQLAlchemy engine with connection pooling.

    Pooling notes:
        - Uses `QueuePool` (default for psycopg2) with explicit sizing.
        - `pool_pre_ping=True` helps avoid stale connections.
    """
    global _ENGINE  # noqa: PLW0603
    if _ENGINE is not None:
        return _ENGINE

    cfg = config or DatabaseConfig.from_env()
    _ENGINE = create_engine(
        cfg.sqlalchemy_url(),
        poolclass=QueuePool,
        pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
        pool_pre_ping=True,
        future=True,
    )
    return _ENGINE


def wait_for_db(
    engine: Optional[Engine] = None,
    *,
    timeout_s: int = 60,
    initial_delay_s: float = 0.5,
    max_delay_s: float = 5.0,
) -> None:
    """Wait until the database is reachable.

    Args:
        engine: Optional SQLAlchemy engine; if not provided, uses `get_engine()`.
        timeout_s: Total time budget for retries.
        initial_delay_s: First sleep interval between retries.
        max_delay_s: Maximum sleep interval between retries.

    Raises:
        TimeoutError: If the database is not reachable within the timeout.
    """
    eng = engine or get_engine()
    deadline = time.time() + timeout_s
    delay = initial_delay_s

    while True:
        try:
            with eng.connect() as conn:
                conn.execute(text("SELECT 1"))
            return
        except OperationalError:
            if time.time() >= deadline:
                raise TimeoutError("Database not reachable within timeout") from None
            time.sleep(delay)
            delay = min(max_delay_s, delay * 1.5)


def health_check(engine: Optional[Engine] = None) -> bool:
    """Return True if the database connection is alive."""
    try:
        wait_for_db(engine=engine, timeout_s=5)
        return True
    except Exception:
        return False

