from pydantic import BaseModel, ConfigDict


class AccountResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    connected: bool
    account_id: str
    broker: str
    person_id: str
    contracts_loaded: bool


class ConnectionStatusResponse(AccountResponse):
    reconnect_attempts: int
