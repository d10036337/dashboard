from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_authentication_service
from app.schemas.auth import AccountResponse
from app.services.authentication_service import AuthenticationService

router = APIRouter(tags=["account"])


@router.get("/account", response_model=AccountResponse)
def get_account(
    authentication_service: Annotated[AuthenticationService, Depends(get_authentication_service)],
) -> AccountResponse:
    return authentication_service.get_account_info()
