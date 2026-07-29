from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from src.dependencies.auth_dependency import get_current_user
from src.schemas.user import LoginResponse, UserMeResponse
from src.schemas.user import (
    AuthUser,
    UserCreateRequest,
    UserResponse,
)
from src.services.user import (
    UserService,
    UserAlreadyExistsError,
)
from src.dependencies.user_dependency import get_user_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    request: UserCreateRequest,
    user_service: UserService = Depends(get_user_service),
):
    """Регистрация нового пользователя."""
    try:
        dto = UserCreateRequest(
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
        )
        return await user_service.register_user(dto)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get(path="/register_confirm", status_code=status.HTTP_200_OK)
async def confirm_registration(
    token: str, user_service: UserService = Depends(get_user_service)
) -> dict[str, str]:
    await user_service.confirm_user(token=token)
    return {"message": "Электронная почта подтверждена"}


@router.post(
    path="/login", response_model=LoginResponse, status_code=status.HTTP_200_OK
)
async def login(user: AuthUser, service: UserService = Depends(get_user_service)):
    return await service.login(user=user)


@router.get(path="/logout", status_code=status.HTTP_200_OK)
async def logout(
    user: Annotated[UserMeResponse, Depends(get_current_user)],
    service: UserService = Depends(get_user_service),
) -> JSONResponse:
    return await service.logout_user(user=user)
