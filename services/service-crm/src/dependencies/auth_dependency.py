from typing import Annotated

from fastapi import HTTPException, Depends
from starlette import status
from starlette.requests import Request

from src.handlers.auth_proxy import (
    AuthProxy,
    TokenInvalidError,
    AuthServiceUnavailableError,
)
from src.schemas.user import UserMeResponse


async def get_token_from_headers(request: Request) -> str:
    token = request.headers.get("Authorization")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing"
        )
    return token


async def get_current_user(
    token: Annotated[str, Depends(get_token_from_headers)],
    auth_proxy: AuthProxy = Depends(AuthProxy),
) -> UserMeResponse:
    """Валидация токена через service-auth (единственный источник аутентификации)."""
    try:
        user_data = await auth_proxy.get_current_user(authorization=token)
    except TokenInvalidError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except AuthServiceUnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )

    return UserMeResponse(**user_data)
