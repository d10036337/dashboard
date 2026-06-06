from functools import lru_cache

from app.core.config import get_settings
from app.services.authentication_service import AuthenticationService


@lru_cache(maxsize=1)
def get_authentication_service() -> AuthenticationService:
    return AuthenticationService(settings=get_settings())
