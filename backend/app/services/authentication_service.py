from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import structlog

from app.core.config import Settings
from app.core.exceptions import (
    AuthenticationException,
    CAActivationException,
    ConnectionLostException,
)
from app.core.shioaji_client import ShioajiClient
from app.schemas.auth import AccountResponse, ConnectionStatusResponse

logger = structlog.get_logger(__name__)
SleepCallable = Callable[[float], Awaitable[None]]


@dataclass(frozen=True)
class ReconnectPolicy:
    delays_seconds: tuple[float, ...] = (0, 5, 15, 30, 30)

    @property
    def max_retries(self) -> int:
        return len(self.delays_seconds)


class AuthenticationService:
    """Manage Shioaji login, CA activation, session state, and reconnects."""

    def __init__(
        self,
        settings: Settings,
        client: ShioajiClient | Any | None = None,
        reconnect_policy: ReconnectPolicy | None = None,
        sleep: SleepCallable = asyncio.sleep,
    ) -> None:
        self._settings = settings
        self._client = client if client is not None else ShioajiClient()
        self._reconnect_policy = reconnect_policy or ReconnectPolicy()
        self._sleep = sleep
        self._account_id = ""
        self._person_id = settings.shioaji_person_id
        self._contracts_loaded = False
        self._connected = False
        self._reconnect_attempts = 0
        self._monitor_task: asyncio.Task[None] | None = None
        self._reconnect_lock = asyncio.Lock()
        self._client.set_disconnect_callback(self.mark_disconnected)

    @property
    def reconnect_attempts(self) -> int:
        return self._reconnect_attempts

    async def login(self) -> AccountResponse:
        self._validate_credentials()
        try:
            accounts = self._client.login(
                api_key=self._settings.shioaji_api_key,
                secret_key=self._settings.shioaji_secret_key,
            )
            self._connected = True
            self._set_primary_account(accounts)
            logger.info("authentication_success", account_id=self._account_id)
        except Exception as exc:
            self._connected = False
            logger.exception("authentication_failure")
            raise AuthenticationException("Shioaji login failed") from exc

        await self.activate_ca()
        await self.reload_contracts()
        return self.get_account_info()

    async def logout(self) -> None:
        self.stop_connection_monitor()
        try:
            self._client.logout()
        finally:
            self._connected = False
            self._contracts_loaded = False
            logger.info("authentication_logout", account_id=self._account_id)

    async def activate_ca(self) -> None:
        ca_path = self._settings.shioaji_ca_path
        ca_password = self._settings.shioaji_ca_password
        person_id = self._settings.shioaji_person_id
        if not ca_path:
            raise CAActivationException("SHIOAJI_CA_PATH is required for CA activation")
        if not ca_password:
            raise CAActivationException("SHIOAJI_CA_PASSWORD is required for CA activation")
        if not person_id:
            raise CAActivationException("SHIOAJI_PERSON_ID is required for CA activation")
        if not Path(ca_path).is_file():
            raise CAActivationException(f"Shioaji CA certificate file does not exist: {ca_path}")

        try:
            self._client.activate_ca(ca_path=ca_path, ca_password=ca_password, person_id=person_id)
            logger.info("ca_activation_success", person_id=person_id)
        except Exception as exc:
            logger.exception("ca_activation_failure", person_id=person_id)
            raise CAActivationException("Shioaji CA activation failed") from exc

    async def reconnect(self) -> AccountResponse:
        async with self._reconnect_lock:
            last_error: Exception | None = None
            for attempt, delay in enumerate(self._reconnect_policy.delays_seconds, start=1):
                self._reconnect_attempts = attempt
                if delay > 0:
                    await self._sleep(delay)
                logger.info("reconnect_attempt", attempt=attempt, delay_seconds=delay)
                try:
                    account = await self.login()
                    logger.info("reconnect_success", attempt=attempt, account_id=account.account_id)
                    self._reconnect_attempts = 0
                    return account
                except (AuthenticationException, CAActivationException) as exc:
                    last_error = exc
                    logger.warning("reconnect_attempt_failed", attempt=attempt, error=str(exc))

            self._connected = False
            logger.error("connection_lost", max_retries=self._reconnect_policy.max_retries)
            raise ConnectionLostException(
                "Shioaji connection could not be restored"
            ) from last_error

    def is_connected(self) -> bool:
        if not self._connected:
            return False
        return bool(self._client.is_session_connected())

    def get_account_info(self) -> AccountResponse:
        return AccountResponse(
            connected=self.is_connected(),
            account_id=self._account_id,
            broker="Sinopac",
            person_id=self._person_id,
            contracts_loaded=self._contracts_loaded,
        )

    def get_connection_status(self) -> ConnectionStatusResponse:
        account = self.get_account_info()
        return ConnectionStatusResponse(
            **account.model_dump(), reconnect_attempts=self._reconnect_attempts
        )

    async def reload_contracts(self) -> None:
        try:
            self._client.fetch_contracts()
            self._contracts_loaded = True
            logger.info("contracts_reloaded")
        except Exception as exc:
            self._contracts_loaded = False
            logger.exception("contracts_reload_failure")
            raise AuthenticationException("Shioaji contracts reload failed") from exc

    def mark_disconnected(self) -> None:
        self._connected = False
        logger.warning("connection_loss_detected")

    async def ensure_connected(self) -> None:
        if not self.is_connected():
            self.mark_disconnected()
            await self.reconnect()

    def start_connection_monitor(self, interval_seconds: float = 10) -> None:
        if self._monitor_task is None or self._monitor_task.done():
            self._monitor_task = asyncio.create_task(self._connection_monitor(interval_seconds))
            logger.info("connection_monitor_started", interval_seconds=interval_seconds)

    def stop_connection_monitor(self) -> None:
        if self._monitor_task is not None and not self._monitor_task.done():
            self._monitor_task.cancel()
            logger.info("connection_monitor_stopped")
        self._monitor_task = None

    async def _connection_monitor(self, interval_seconds: float) -> None:
        while True:
            await self._sleep(interval_seconds)
            try:
                await self.ensure_connected()
            except ConnectionLostException:
                logger.exception("connection_monitor_reconnect_failed")

    def _validate_credentials(self) -> None:
        missing = [
            name
            for name, value in (
                ("SHIOAJI_API_KEY", self._settings.shioaji_api_key),
                ("SHIOAJI_SECRET_KEY", self._settings.shioaji_secret_key),
                ("SHIOAJI_PERSON_ID", self._settings.shioaji_person_id),
            )
            if not value
        ]
        if missing:
            raise AuthenticationException(f"Missing Shioaji credentials: {', '.join(missing)}")

    def _set_primary_account(self, accounts: Sequence[Any]) -> None:
        listed_accounts = list(accounts) or list(self._client.list_accounts())
        if not listed_accounts:
            self._account_id = ""
            self._person_id = self._settings.shioaji_person_id
            return

        account = listed_accounts[0]
        self._account_id = str(
            getattr(account, "account_id", "")
            or getattr(account, "account", "")
            or getattr(account, "id", "")
        )
        self._person_id = str(getattr(account, "person_id", "") or self._settings.shioaji_person_id)
