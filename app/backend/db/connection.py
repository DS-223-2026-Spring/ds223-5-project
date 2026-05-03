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


# Immutable connection config populated from environment variables
@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    name: str
    user: str
    password: str
    connect_timeout_s: int = 5

    @staticmethod
    def from_env() -> "DatabaseConfig":
        return DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            name=os.getenv("DB_NAME", "imp"),
            user=os.getenv("DB_USER", "imp_user"),
            password=os.getenv("DB_PASSWORD", "imp_password"),
            connect_timeout_s=int(os.getenv("DB_CONNECT_TIMEOUT_S", "5")),
        )

    def sqlalchemy_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
            f"?connect_timeout={self.connect_timeout_s}"
        )


_ENGINE: Optional[Engine] = None


# Lazy-initialized singleton engine with connection pooling
def get_engine(config: Optional[DatabaseConfig] = None) -> Engine:
    global _ENGINE
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


# Block until DB accepts connections; exponential backoff with ceiling
def wait_for_db(
    engine: Optional[Engine] = None,
    *,
    timeout_s: int = 60,
    initial_delay_s: float = 0.5,
    max_delay_s: float = 5.0,
) -> None:
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


# Non-throwing connectivity probe for /health endpoint
def health_check(engine: Optional[Engine] = None) -> bool:
    try:
        wait_for_db(engine=engine, timeout_s=5)
        return True
    except Exception:
        return False
