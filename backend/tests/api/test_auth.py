from fastapi.testclient import TestClient

from app.dependencies.auth import get_authentication_service
from app.main import create_app
from app.schemas.auth import AccountResponse


class StubAuthenticationService:
    def get_account_info(self) -> AccountResponse:
        return AccountResponse(
            connected=True,
            account_id="F123456789",
            broker="Sinopac",
            person_id="A123456789",
            contracts_loaded=True,
        )

    def is_connected(self) -> bool:
        return True


def test_root_account_endpoint_returns_shioaji_connection_status() -> None:
    app = create_app()
    app.dependency_overrides[get_authentication_service] = StubAuthenticationService
    client = TestClient(app)

    response = client.get("/account")

    assert response.status_code == 200
    assert response.json() == {
        "connected": True,
        "account_id": "F123456789",
        "broker": "Sinopac",
        "person_id": "A123456789",
        "contracts_loaded": True,
    }


def test_api_v1_account_endpoint_returns_shioaji_connection_status() -> None:
    app = create_app()
    app.dependency_overrides[get_authentication_service] = StubAuthenticationService
    client = TestClient(app)

    response = client.get("/api/v1/account")

    assert response.status_code == 200
    assert response.json()["connected"] is True
    assert response.json()["broker"] == "Sinopac"
