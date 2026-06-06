from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, Protocol, cast


class ShioajiAccountLike(Protocol):
    account_id: str
    person_id: str
    broker_id: str


class ShioajiClient:
    """Thin adapter around the Sinopac Shioaji SDK.

    The adapter keeps direct SDK calls out of application services so tests can use
    deterministic fakes and later trading modules can depend on a stable broker boundary.
    """

    def __init__(self, simulation: bool = False) -> None:
        import shioaji as sj  # type: ignore[import-untyped]

        self._api = sj.Shioaji(simulation=simulation)
        self._disconnect_callback: Callable[[], None] | None = None

    @property
    def api(self) -> Any:
        return self._api

    def login(self, api_key: str, secret_key: str) -> Sequence[Any]:
        return cast(Sequence[Any], self._api.login(api_key=api_key, secret_key=secret_key))

    def logout(self) -> None:
        self._api.logout()

    def activate_ca(self, ca_path: str, ca_password: str, person_id: str) -> None:
        self._api.activate_ca(ca_path=ca_path, ca_passwd=ca_password, person_id=person_id)

    def fetch_contracts(self) -> None:
        # Shioaji reloads the contracts object when fetch_contracts is invoked.
        self._api.fetch_contracts()

    def list_accounts(self) -> Sequence[Any]:
        return cast(Sequence[Any], self._api.list_accounts())

    def is_session_connected(self) -> bool:
        usage = getattr(self._api, "usage", None)
        if callable(usage):
            try:
                usage()
                return True
            except Exception:
                return False
        return bool(getattr(self._api, "_login", False))

    def set_disconnect_callback(self, callback: Callable[[], None]) -> None:
        self._disconnect_callback = callback
        quote = getattr(self._api, "quote", None)
        set_callback = getattr(quote, "set_event_callback", None)
        if callable(set_callback):
            set_callback(self._handle_quote_event)

    def _handle_quote_event(self, code: int, event: str) -> None:
        normalized = event.lower()
        is_disconnect = code < 0 or "disconnect" in normalized or "error" in normalized
        if is_disconnect and self._disconnect_callback is not None:
            self._disconnect_callback()
