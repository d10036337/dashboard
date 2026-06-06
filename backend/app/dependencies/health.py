from collections.abc import Callable

from redis import Redis
from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import SessionLocal


def check_database_connected() -> bool:
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def check_redis_connected() -> bool:
    try:
        client = Redis.from_url(
            get_settings().redis_url, socket_connect_timeout=1, socket_timeout=1
        )
        try:
            return bool(client.ping())
        finally:
            client.close()
    except Exception:
        return False


def get_database_health_checker() -> Callable[[], bool]:
    return check_database_connected


def get_redis_health_checker() -> Callable[[], bool]:
    return check_redis_connected
