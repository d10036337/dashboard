from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as root_auth_router
from app.api.health import router as root_health_router
from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.dependencies.auth import get_authentication_service

configure_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    authentication_service = get_authentication_service()
    logger.info("application_starting", service=settings.app_name, environment=settings.environment)
    if settings.shioaji_api_key and settings.shioaji_secret_key and settings.shioaji_person_id:
        await authentication_service.login()
        authentication_service.start_connection_monitor(interval_seconds=10)
    else:
        logger.warning("shioaji_startup_login_skipped", reason="missing_credentials")
    try:
        yield
    finally:
        authentication_service.stop_connection_monitor()
        logger.info("application_stopping", service=settings.app_name)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.2.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(root_health_router)
    app.include_router(root_auth_router)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
