from fastapi.testclient import TestClient

from app.dependencies.auth import get_authentication_service
from app.dependencies.health import get_database_health_checker, get_redis_health_checker
from app.main import create_app


class StubAuthenticationService:
    def is_connected(self) -> bool:
        return True


def healthy_checker() -> bool:
    return True


def build_client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_authentication_service] = StubAuthenticationService
    app.dependency_overrides[get_database_health_checker] = lambda: healthy_checker
    app.dependency_overrides[get_redis_health_checker] = lambda: healthy_checker
    return TestClient(app)


def assert_healthy_response(payload: dict[str, object]) -> None:
    assert payload == {
        "status": "healthy",
        "shioaji_connected": True,
        "redis_connected": True,
        "database_connected": True,
    }


def test_health_endpoint_returns_dependency_status() -> None:
    client = build_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert_healthy_response(response.json())


def test_api_v1_health_endpoint_returns_dependency_status() -> None:
    client = build_client()

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert_healthy_response(response.json())
