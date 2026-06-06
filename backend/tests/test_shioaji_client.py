from __future__ import annotations

import sys
from types import SimpleNamespace
from typing import Any

from app.core.shioaji_client import ShioajiClient


class FakeApi:
    def __init__(self, simulation: bool = False) -> None:
        self.simulation = simulation
        self.logged_out = False
        self.ca_args: dict[str, str] = {}
        self.contracts_fetched = False
        self.event_callback: Any = None
        self.quote = SimpleNamespace(set_event_callback=self.set_event_callback)

    def login(self, api_key: str, secret_key: str) -> list[SimpleNamespace]:
        return [SimpleNamespace(account_id="F123", person_id="A123")]

    def logout(self) -> None:
        self.logged_out = True

    def activate_ca(self, ca_path: str, ca_passwd: str, person_id: str) -> None:
        self.ca_args = {"ca_path": ca_path, "ca_passwd": ca_passwd, "person_id": person_id}

    def fetch_contracts(self) -> None:
        self.contracts_fetched = True

    def list_accounts(self) -> list[SimpleNamespace]:
        return [SimpleNamespace(account_id="F123")]

    def usage(self) -> dict[str, int]:
        return {"connections": 1}

    def set_event_callback(self, callback: Any) -> None:
        self.event_callback = callback


class FakeShioajiModule:
    def __init__(self) -> None:
        self.instances: list[FakeApi] = []

    def Shioaji(self, simulation: bool = False) -> FakeApi:  # noqa: N802 - SDK constructor name
        api = FakeApi(simulation=simulation)
        self.instances.append(api)
        return api


def test_shioaji_client_delegates_sdk_calls(monkeypatch: Any) -> None:
    fake_module = FakeShioajiModule()
    monkeypatch.setitem(sys.modules, "shioaji", fake_module)
    client = ShioajiClient(simulation=True)

    accounts = client.login(api_key="key", secret_key="secret")
    client.activate_ca(ca_path="/cert.pfx", ca_password="password", person_id="A123")
    client.fetch_contracts()
    listed_accounts = client.list_accounts()

    api = fake_module.instances[0]
    assert api.simulation is True
    assert accounts[0].account_id == "F123"
    assert listed_accounts[0].account_id == "F123"
    assert api.ca_args["ca_passwd"] == "password"
    assert api.contracts_fetched is True
    assert client.is_session_connected() is True

    client.logout()
    assert api.logged_out is True


def test_shioaji_client_disconnect_callback_receives_quote_disconnect(monkeypatch: Any) -> None:
    fake_module = FakeShioajiModule()
    monkeypatch.setitem(sys.modules, "shioaji", fake_module)
    client = ShioajiClient()
    disconnected = False

    def on_disconnect() -> None:
        nonlocal disconnected
        disconnected = True

    client.set_disconnect_callback(on_disconnect)
    fake_module.instances[0].event_callback(-1, "disconnect")

    assert disconnected is True
