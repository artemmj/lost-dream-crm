from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.dependencies.auth_dependency import get_current_user
from src.dependencies.permissions import RequirePermission
from src.schemas.user import UserMeResponse
from src.schemas.user import (
    UserResponse,
    UserUpdateRequest,
    UserListWithRolesResponse,
)
from src.services.user import (
    UserService,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.dependencies.user_dependency import get_user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(path="/me", status_code=status.HTTP_200_OK, response_model=UserMeResponse)
async def me(
    user: Annotated[UserMeResponse, Depends(get_current_user)],
) -> UserMeResponse:
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: UserMeResponse = Depends(RequirePermission("get_user")),
    user_service: UserService = Depends(get_user_service),
):
    """Получение пользователя по ID."""
    try:
        return await user_service.get_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/", response_model=UserListWithRolesResponse)
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    search: str | None = Query(None, description="Поиск по email, имени, фамилии"),
    current_user: UserMeResponse = Depends(RequirePermission("list_users")),
    user_service: UserService = Depends(get_user_service),
):
    """Список пользователей с пагинацией и фильтрацией."""
    items, total = await user_service.get_users_with_roles(page, per_page, search)
    return UserListWithRolesResponse(
        users=items,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    request: UserUpdateRequest,
    current_user: UserMeResponse = Depends(RequirePermission("update_user")),
    user_service: UserService = Depends(get_user_service),
):
    """
    Частичное обновление пользователя.
    Обновляются только переданные поля.

    Административные поля (is_active, is_banned, is_superuser, is_verified)
    может менять только суперпользователь.
    """
    # Защита от эскалации привилегий: админ-поля — только для суперпользователя
    admin_fields = {"is_active", "is_banned", "is_superuser", "is_verified"}
    if not current_user.is_superuser:
        requested_admin = {f for f in admin_fields if getattr(request, f) is not None}
        if requested_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Only superuser can update fields: "
                    f"{', '.join(sorted(requested_admin))}"
                ),
            )
    try:
        return await user_service.update_user(user_id, request)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: UserMeResponse = Depends(RequirePermission("delete_user")),
    user_service: UserService = Depends(get_user_service),
):
    """Удаление пользователя. Требует пермишен 'delete_user'."""
    try:
        await user_service.delete_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
