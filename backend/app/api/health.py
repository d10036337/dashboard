from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_authentication_service
from app.dependencies.health import get_database_health_checker, get_redis_health_checker
from app.schemas.health import HealthResponse
from app.services.authentication_service import AuthenticationService

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check(
    authentication_service: Annotated[AuthenticationService, Depends(get_authentication_service)],
    database_health_checker: Annotated[Callable[[], bool], Depends(get_database_health_checker)],
    redis_health_checker: Annotated[Callable[[], bool], Depends(get_redis_health_checker)],
) -> HealthResponse:
    shioaji_connected = authentication_service.is_connected()
    redis_connected = redis_health_checker()
    database_connected = database_health_checker()
    healthy = shioaji_connected and redis_connected and database_connected
    return HealthResponse(
        status="healthy" if healthy else "degraded",
        shioaji_connected=shioaji_connected,
        redis_connected=redis_connected,
        database_connected=database_connected,
    )
