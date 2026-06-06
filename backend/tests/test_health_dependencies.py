from typing import Any

from redis import Redis

from app.dependencies import health


class FakeSession:
    def __enter__(self) -> "FakeSession":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def execute(self, _: Any) -> None:
        return None


class FakeRedisClient:
    def __init__(self, ping_result: bool) -> None:
        self.ping_result = ping_result
        self.closed = False

    def ping(self) -> bool:
        return self.ping_result

    def close(self) -> None:
        self.closed = True


def test_database_health_checker_success(monkeypatch: Any) -> None:
    monkeypatch.setattr(health, "SessionLocal", lambda: FakeSession())

    assert health.check_database_connected() is True


def test_database_health_checker_failure(monkeypatch: Any) -> None:
    def broken_session() -> FakeSession:
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(health, "SessionLocal", broken_session)

    assert health.check_database_connected() is False


def test_redis_health_checker_success(monkeypatch: Any) -> None:
    fake_client = FakeRedisClient(ping_result=True)
    monkeypatch.setattr(Redis, "from_url", lambda *_args, **_kwargs: fake_client)

    assert health.check_redis_connected() is True
    assert fake_client.closed is True


def test_redis_health_checker_failure(monkeypatch: Any) -> None:
    def broken_from_url(*_args: object, **_kwargs: object) -> FakeRedisClient:
        raise RuntimeError("redis unavailable")

    monkeypatch.setattr(Redis, "from_url", broken_from_url)

    assert health.check_redis_connected() is False
