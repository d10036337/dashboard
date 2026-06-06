from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from app.core.config import Settings
from app.core.exceptions import (
    AuthenticationException,
    CAActivationException,
    ConnectionLostException,
)
from app.services.authentication_service import AuthenticationService, ReconnectPolicy


@dataclass
class FakeAccount:
    account_id: str = "F123456789"
    person_id: str = "A123456789"


class FakeShioajiClient:
    def __init__(self) -> None:
        self.login_failures_remaining = 0
        self.ca_failure = False
        self.contract_failure = False
        self.connected = False
        self.ca_activated = False
        self.contracts_loaded = False
        self.disconnect_callback: Any = None
        self.login_calls = 0

    def set_disconnect_callback(self, callback: Any) -> None:
        self.disconnect_callback = callback

    def login(self, api_key: str, secret_key: str) -> list[FakeAccount]:
        self.login_calls += 1
        if self.login_failures_remaining > 0:
            self.login_failures_remaining -= 1
            raise RuntimeError("login failed")
        self.connected = True
        return [FakeAccount()]

    def logout(self) -> None:
        self.connected = False

    def activate_ca(self, ca_path: str, ca_password: str, person_id: str) -> None:
        if self.ca_failure:
            raise RuntimeError("ca failed")
        self.ca_activated = True

    def fetch_contracts(self) -> None:
        if self.contract_failure:
            raise RuntimeError("contracts failed")
        self.contracts_loaded = True

    def list_accounts(self) -> list[FakeAccount]:
        return [FakeAccount()]

    def is_session_connected(self) -> bool:
        return self.connected


def make_settings(ca_file: Path) -> Settings:
    return Settings(
        shioaji_api_key="api-key",
        shioaji_secret_key="secret-key",
        shioaji_person_id="A123456789",
        shioaji_ca_path=str(ca_file),
        shioaji_ca_password="ca-password",
    )


async def no_sleep(_: float) -> None:
    return None


@pytest.mark.asyncio
async def test_successful_login_activates_ca_and_reloads_contracts(tmp_path: Path) -> None:
    ca_file = tmp_path / "cert.pfx"
    ca_file.write_text("certificate")
    client = FakeShioajiClient()
    service = AuthenticationService(settings=make_settings(ca_file), client=client, sleep=no_sleep)

    account = await service.login()

    assert account.connected is True
    assert account.account_id == "F123456789"
    assert account.broker == "Sinopac"
    assert account.person_id == "A123456789"
    assert account.contracts_loaded is True
    assert client.ca_activated is True
    assert client.contracts_loaded is True


@pytest.mark.asyncio
async def test_failed_login_raises_authentication_exception(tmp_path: Path) -> None:
    ca_file = tmp_path / "cert.pfx"
    ca_file.write_text("certificate")
    client = FakeShioajiClient()
    client.login_failures_remaining = 1
    service = AuthenticationService(settings=make_settings(ca_file), client=client, sleep=no_sleep)

    with pytest.raises(AuthenticationException, match="Shioaji login failed"):
        await service.login()

    assert service.is_connected() is False


@pytest.mark.asyncio
async def test_ca_activation_success(tmp_path: Path) -> None:
    ca_file = tmp_path / "cert.pfx"
    ca_file.write_text("certificate")
    client = FakeShioajiClient()
    service = AuthenticationService(settings=make_settings(ca_file), client=client, sleep=no_sleep)

    await service.activate_ca()

    assert client.ca_activated is True


@pytest.mark.asyncio
async def test_ca_activation_failure_for_missing_file(tmp_path: Path) -> None:
    missing_ca_file = tmp_path / "missing.pfx"
    client = FakeShioajiClient()
    service = AuthenticationService(
        settings=make_settings(missing_ca_file), client=client, sleep=no_sleep
    )

    with pytest.raises(CAActivationException, match="does not exist"):
        await service.activate_ca()


@pytest.mark.asyncio
async def test_reconnect_success_after_immediate_retry(tmp_path: Path) -> None:
    ca_file = tmp_path / "cert.pfx"
    ca_file.write_text("certificate")
    client = FakeShioajiClient()
    client.login_failures_remaining = 1
    service = AuthenticationService(
        settings=make_settings(ca_file),
        client=client,
        reconnect_policy=ReconnectPolicy(delays_seconds=(0, 0)),
        sleep=no_sleep,
    )

    account = await service.reconnect()

    assert account.connected is True
    assert client.login_calls == 2
    assert service.reconnect_attempts == 0


@pytest.mark.asyncio
async def test_reconnect_failure_raises_connection_lost_exception(tmp_path: Path) -> None:
    ca_file = tmp_path / "cert.pfx"
    ca_file.write_text("certificate")
    client = FakeShioajiClient()
    client.login_failures_remaining = 10
    service = AuthenticationService(
        settings=make_settings(ca_file),
        client=client,
        reconnect_policy=ReconnectPolicy(delays_seconds=(0, 0, 0)),
        sleep=no_sleep,
    )

    with pytest.raises(ConnectionLostException, match="could not be restored"):
        await service.reconnect()

    assert client.login_calls == 3
    assert service.is_connected() is False


@pytest.mark.asyncio
async def test_logout_clears_connection_state(tmp_path: Path) -> None:
    ca_file = tmp_path / "cert.pfx"
    ca_file.write_text("certificate")
    client = FakeShioajiClient()
    service = AuthenticationService(settings=make_settings(ca_file), client=client, sleep=no_sleep)
    await service.login()

    await service.logout()

    assert service.is_connected() is False
    assert service.get_account_info().contracts_loaded is False


@pytest.mark.asyncio
async def test_login_with_missing_credentials_raises(tmp_path: Path) -> None:
    ca_file = tmp_path / "cert.pfx"
    ca_file.write_text("certificate")
    settings = Settings(shioaji_ca_path=str(ca_file), shioaji_ca_password="password")
    service = AuthenticationService(settings=settings, client=FakeShioajiClient(), sleep=no_sleep)

    with pytest.raises(AuthenticationException, match="Missing Shioaji credentials"):
        await service.login()


@pytest.mark.asyncio
async def test_ca_activation_failure_from_client(tmp_path: Path) -> None:
    ca_file = tmp_path / "cert.pfx"
    ca_file.write_text("certificate")
    client = FakeShioajiClient()
    client.ca_failure = True
    service = AuthenticationService(settings=make_settings(ca_file), client=client, sleep=no_sleep)

    with pytest.raises(CAActivationException, match="Shioaji CA activation failed"):
        await service.activate_ca()


@pytest.mark.asyncio
async def test_reload_contracts_failure_raises_authentication_exception(tmp_path: Path) -> None:
    ca_file = tmp_path / "cert.pfx"
    ca_file.write_text("certificate")
    client = FakeShioajiClient()
    client.contract_failure = True
    service = AuthenticationService(settings=make_settings(ca_file), client=client, sleep=no_sleep)

    with pytest.raises(AuthenticationException, match="contracts reload failed"):
        await service.reload_contracts()

    assert service.get_account_info().contracts_loaded is False


@pytest.mark.asyncio
async def test_get_connection_status_reports_reconnect_attempts(tmp_path: Path) -> None:
    ca_file = tmp_path / "cert.pfx"
    ca_file.write_text("certificate")
    client = FakeShioajiClient()
    client.login_failures_remaining = 1
    service = AuthenticationService(
        settings=make_settings(ca_file),
        client=client,
        reconnect_policy=ReconnectPolicy(delays_seconds=(0,)),
        sleep=no_sleep,
    )

    with pytest.raises(ConnectionLostException):
        await service.reconnect()

    status = service.get_connection_status()
    assert status.connected is False
    assert status.reconnect_attempts == 1


@pytest.mark.asyncio
async def test_ensure_connected_reconnects_after_disconnect(tmp_path: Path) -> None:
    ca_file = tmp_path / "cert.pfx"
    ca_file.write_text("certificate")
    client = FakeShioajiClient()
    service = AuthenticationService(
        settings=make_settings(ca_file),
        client=client,
        reconnect_policy=ReconnectPolicy(delays_seconds=(0,)),
        sleep=no_sleep,
    )

    service.mark_disconnected()
    await service.ensure_connected()

    assert service.is_connected() is True


@pytest.mark.asyncio
async def test_connection_monitor_attempts_reconnect(tmp_path: Path) -> None:
    ca_file = tmp_path / "cert.pfx"
    ca_file.write_text("certificate")
    client = FakeShioajiClient()

    class CancelAfterSecondSleep:
        def __init__(self) -> None:
            self.calls = 0

        async def __call__(self, _: float) -> None:
            self.calls += 1
            await asyncio.sleep(0)
            if self.calls > 1:
                raise asyncio.CancelledError

    monitor_sleep = CancelAfterSecondSleep()
    service = AuthenticationService(
        settings=make_settings(ca_file),
        client=client,
        reconnect_policy=ReconnectPolicy(delays_seconds=(0,)),
        sleep=monitor_sleep,
    )

    service.start_connection_monitor(interval_seconds=0)
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    service.stop_connection_monitor()

    assert client.login_calls >= 1
