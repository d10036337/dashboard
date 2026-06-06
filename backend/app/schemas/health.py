from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: str
    shioaji_connected: bool
    redis_connected: bool
    database_connected: bool
