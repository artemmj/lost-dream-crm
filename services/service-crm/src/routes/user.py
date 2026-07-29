from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.dependencies.auth_dependency import get_current_user
from src.schemas.user import LoginResponse, UserMeResponse
from src.schemas.user import (
    AuthUser,
    BulkCreateRequest,
    BulkCreateResponse,
    EmailCheckRequest,
    EmailCheckResponse,
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserUpdateRequest,
)
from src.services.user import (
    UserService,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.dependencies.user_dependency import get_user_service

router = APIRouter(prefix="/users", tags=["Users"])

# @router.get(path="/logout", status_code=status.HTTP_200_OK)
# async def logout(
#     user: Annotated[UserVerifySchema, Depends(get_current_user)],
#     service: UserService = Depends(UserService),
# ) -> JSONResponse:
#     return await service.logout_user(user=user)


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


@router.get(path="/me", status_code=status.HTTP_200_OK, response_model=UserMeResponse)
async def me(
    user: Annotated[UserMeResponse, Depends(get_current_user)],
) -> UserMeResponse:
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
):
    """Получение пользователя по ID."""
    try:
        return await user_service.get_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    user_service: UserService = Depends(get_user_service),
):
    """Список пользователей с пагинацией и фильтрацией."""
    users, total = await user_service.list_users(
        page=page,
        per_page=per_page,
        is_active=is_active,
    )
    return UserListResponse(
        users=users,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    request: UserUpdateRequest,
    user_service: UserService = Depends(get_user_service),
):
    """
    Частичное обновление пользователя.
    Обновляются только переданные поля.
    """
    try:
        dto = UserUpdateRequest(
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            is_active=request.is_active,
            is_banned=request.is_banned,
            is_superuser=request.is_superuser,
            is_verified=request.is_verified,
        )
        return await user_service.update_user(user_id, dto)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
):
    """Удаление пользователя."""
    try:
        await user_service.delete_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
):
    """Деактивация пользователя."""
    try:
        return await user_service.deactivate_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
):
    """Активация пользователя."""
    try:
        return await user_service.activate_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ===== Специализированные endpoints =====


@router.post("/check-emails", response_model=EmailCheckResponse)
async def check_emails(
    request: EmailCheckRequest,
    user_service: UserService = Depends(get_user_service),
):
    """Проверка доступности email."""
    availability = await user_service.check_emails_availability(request.emails)
    return EmailCheckResponse(emails=availability)


@router.post(
    "/bulk", response_model=BulkCreateResponse, status_code=status.HTTP_201_CREATED
)
async def bulk_create_users(
    request: BulkCreateRequest,
    user_service: UserService = Depends(get_user_service),
):
    """Массовое создание пользователей."""
    dtos = [
        UserCreateRequest(
            email=u.email,
            password=u.password,
            first_name=u.first_name,
            last_name=u.last_name,
        )
        for u in request.users
    ]
    result = await user_service.bulk_create_users(dtos)
    return result
